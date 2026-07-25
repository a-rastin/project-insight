# Dashboard API Contract: INSIGHT Workspace

Dashboard exposes one primary INSIGHT contract: an authenticated workspace shell with role-scoped module links. Dashboard verifies identity through Authentication over REST, creates a Dashboard-local session, and returns only navigation metadata. Dashboard does not import Authentication code, decode JWTs, read Authentication storage, or implement patient, treatment, logs, backup, user-management, guideline, Bayesian model, or downstream module workflows.

Backend: Python FastAPI. Local state: Dashboard sessions plus optional workspace events. Dashboard does not duplicate Authentication users or profiles. Standalone mock auth is in-memory dev/test behavior, not persisted schema.

## Primary INSIGHT Flow

1. Host app calls `POST /internal/dashboard/session` with valid Authentication credentials.
2. Dashboard calls `GET /api/auth/session` and ignores request-body identity fields.
3. Dashboard creates a local Dashboard session bound to verified `user.id`, `role`, and Authentication session id.
4. UI calls `GET /internal/dashboard/workspace`.
5. Dashboard re-validates local session and calls `GET /api/auth/session` again.
6. Dashboard returns INSIGHT workspace metadata and live discovery results for configured modules.

Protected Dashboard endpoints accept the Dashboard session through the HttpOnly
`insight_dashboard_session` cookie or the `X-Dashboard-Session` server-to-server header.
Dashboard session and patient identifiers are never URL parameters.

## Auth Verification Contract

Dashboard verifies identity by calling Authentication:

```http
GET /api/auth/session
```

Dashboard forwards caller credentials when present:

- `Authorization`
- `Cookie`
- `X-Auth-Session`
- `X-Auth-Session-Id`

Expected success response:

```json
{
  "authenticated": true,
  "session": {
    "id": "auth-789"
  },
  "user": {
    "id": "psy-1",
    "role": "PSYCHIATRIST",
    "fullName": "Mina Rahimi",
    "title": "Dr."
  }
}
```

Accepted roles:

- `PSYCHIATRIST`
- `ADMIN`

Dashboard requires a concrete Authentication session id from `session.id`, `sessionId`, or `authSessionId`.

Rejected Authentication states:

- missing auth session id
- unauthenticated response
- inactive session
- expired session or past `expiresAt`
- forced password change/reset
- password reset required
- disclaimer-required or disclaimer-blocked state
- unsupported role
- missing user id

Authentication `401` or `403` maps to Dashboard `authentication_session_required`. Authentication transport failures, missing endpoint config, or non-2xx/non-auth failures map to `authentication_session_unavailable`.

Config:

| Variable | Meaning |
| --- | --- |
| `AUTH_SESSION_URL` | Exact Authentication session URL. |
| `AUTH_BASE_URL` | Base URL; Dashboard appends `/api/auth/session`. |
| `DASHBOARD_MOCK_AUTH` | `1` enables standalone mock auth; `0` disables it. |
| `DASHBOARD_DB_PATH` | SQLite path; defaults to `dashboard.sqlite3`. |
| `DASHBOARD_MODULE_REGISTRY` | JSON array of `{moduleId, title, roles, contractUrl}` entries; overrides `module-config.json`. |
| `DASHBOARD_MODULE_TIMEOUT_MS` | Timeout for each module contract/readiness request; defaults to `2000`. |

When neither `AUTH_SESSION_URL` nor `AUTH_BASE_URL` is set, standalone mock auth is enabled unless `DASHBOARD_MOCK_AUTH=0`.

## Create Dashboard Session

```http
POST /internal/dashboard/session
```

Headers: valid Authentication credentials.

Body:

```json
{
  "device": "Clinic desktop"
}
```

Identity fields in body are ignored. Authentication response is source of truth.

Success: `201`

```json
{
  "sessionId": "dashboard-session-uuid",
  "dashboardUrl": "/dashboard/",
  "user": {
    "id": "psy-1",
    "role": "PSYCHIATRIST",
    "fullName": "Mina Rahimi",
    "title": "Dr.",
    "disclaimerAcceptedAt": null
  }
}
```

Errors:

| Status | Error | Cause |
| --- | --- | --- |
| `401` | `authentication_session_required` | Authentication rejected, missing, expired, blocked, or unsupported. |
| `502` | `authentication_session_unavailable` | Authentication endpoint unavailable, failed, or misconfigured. |

## INSIGHT Workspace Response

```http
GET /internal/dashboard/workspace
```

Alias:

```http
GET /internal/dashboard/summary
```

Before returning workspace metadata, Dashboard:

1. verifies Dashboard session exists and is active
2. calls `GET /api/auth/session`
3. rejects if Authentication `user.id` differs from Dashboard session `userId`
4. refreshes local role and Authentication session id from verified identity

Common response:

```json
{
  "user": {
    "id": "psy-1",
    "role": "PSYCHIATRIST",
    "fullName": "Mina Rahimi",
    "title": "Dr.",
    "disclaimerAcceptedAt": null,
    "displayName": "Dr. Mina Rahimi"
  },
  "displayName": "Dr. Mina Rahimi",
  "currentDateTime": "2026-07-06T10:30:00.000000Z",
  "workspace": {
    "kind": "PSYCHIATRIST",
    "title": "Workspace",
    "buttons": [
      {
         "id": "add-new-patient",
         "title": "Add New Patient",
         "href": "/modules/add-new-patient",
         "status": "available",
         "reason": "contract and readiness checks passed",
         "routeDiscovery": {
          "method": "GET",
          "href": "/internal/dashboard/module-routes/add-new-patient"
        }
      }
    ]
  },
  "requiresDisclaimer": true,
  "disclaimer": {
    "acceptedAt": null,
    "text": "This workspace is a research prototype. It is not a substitute for clinical judgment, emergency care, or licensed guideline review."
  }
}
```

Response rules:

- `workspace.title` is always `Workspace`.
- `workspace.kind` is verified role: `PSYCHIATRIST` or `ADMIN`.
- `displayName` equals `Dr. {fullName}` for `PSYCHIATRIST`.
- `displayName` equals `{fullName}` for `ADMIN`.
- Psychiatrist-only responses include `requiresDisclaimer` and `disclaimer`.
- Responses contain no patient lists, treatment data, drafts, follow-ups, oversight module data, guideline revisions, Bayesian models, backup payloads, or module implementation payloads.

Role button sets:

| Role | Button ids | Button titles |
| --- | --- | --- |
| `PSYCHIATRIST` | `add-new-patient`, `patient-follow-up`, `list-of-patients`, `setting` | `Add New Patient`, `Patient Follow-up`, `List of Patients`, `Setting` |
| `ADMIN` | `user-management` | `User Management` |

Errors:

| Status | Error | Cause |
| --- | --- | --- |
| `401` | `dashboard_session_required` | Dashboard session missing, invalid, inactive, or signed out. |
| `401` | `authentication_session_required` | Authentication rejected, missing, expired, blocked, or unsupported. |
| `401` | `authentication_session_mismatch` | Authentication user differs from Dashboard session user. |
| `502` | `authentication_session_unavailable` | Authentication endpoint unavailable, failed, or misconfigured. |

## Runtime Module Discovery

Dashboard has no hard-coded module links. It reads `moduleRegistry` from `module-config.json` (or the `DASHBOARD_MODULE_REGISTRY` override), queries every role-visible module's configured `/contract` URL and adjacent `/ready` URL, and keeps failed modules visible with a status and reason.

Every workspace button includes route discovery metadata plus `status`, `reason`, and the compatible contract's `basePath` as `href`:

```json
{
  "routeDiscovery": {
    "method": "GET",
    "href": "/internal/dashboard/module-routes/{moduleId}"
  }
}
```

Discovery endpoint:

```http
GET /internal/dashboard/module-routes/{moduleId}
X-Dashboard-Session: {dashboardSessionId}
```

Dashboard verifies Dashboard session and Authentication before route discovery. `moduleId` must belong to caller role.

Success:

```json
{
  "moduleId": "logs",
  "title": "Logs",
  "href": "/modules/logs",
  "status": "available",
  "reason": "contract and readiness checks passed"
}
```

Discovery states:

- `available`: contract uses supported interface major version `1` and readiness reports `ready`.
- `degraded`: contract is compatible but readiness failed or did not report `ready`.
- `incompatible`: contract identity, interface version, or `basePath` is invalid for Dashboard.
- `unavailable`: the contract endpoint could not be reached or returned a non-success status.
- Every state includes a non-empty `reason`; failed entries are never omitted.
- `href` is the compatible contract's `basePath`, otherwise `null`.
- Target module owns data, mutations, permissions beyond entry, UI, and workflow implementation.
- Dashboard returns no module payload in route discovery.

## Server-Owned Workflow Context

`POST /internal/dashboard/workflow-context` accepts canonical `patientUuid` and
`encounterUuid` values in the request body and returns only an opaque
`workflowContextId`. Dashboard stores both identifiers server-side, scoped to
the authenticated Dashboard session, with the Authentication session expiry.

Modules resolve context server-to-server with
`GET /internal/dashboard/workflow-context` and the opaque id in
`X-Workflow-Context`. Module launches retain the module's clean `basePath`; no
patient code, patient UUID, encounter UUID, or PHI is appended to the URL.

`GET /internal/dashboard/workflow-status` accepts `X-Workflow-Context` and
returns read-only module `status` and `summary` values obtained from module
contract and readiness interfaces. Dashboard exposes no clinical mutation
through either workflow endpoint.

Errors:

| Status | Error | Cause |
| --- | --- | --- |
| `401` | `dashboard_session_required` | Dashboard session missing, invalid, inactive, or signed out. |
| `401` | `authentication_session_required` | Authentication rejected, missing, expired, blocked, or unsupported. |
| `401` | `authentication_session_mismatch` | Authentication user differs from Dashboard session user. |
| `404` | `module_route_not_available` | Module id unavailable to verified role. |
| `502` | `authentication_session_unavailable` | Authentication endpoint unavailable, failed, or misconfigured. |

## Disclaimer Acceptance

```http
POST /internal/dashboard/disclaimer/accept
X-Dashboard-Session: {dashboardSessionId}
```

Allowed for verified `PSYCHIATRIST` sessions only. Returns updated INSIGHT workspace response.

Errors:

| Status | Error | Cause |
| --- | --- | --- |
| `401` | `dashboard_session_required` | Dashboard session missing, invalid, inactive, or signed out. |
| `401` | `authentication_session_required` | Authentication rejected, missing, expired, blocked, or unsupported. |
| `401` | `authentication_session_mismatch` | Authentication user differs from Dashboard session user. |
| `403` | `psychiatrist_only` | Verified role is not `PSYCHIATRIST`. |
| `502` | `authentication_session_unavailable` | Authentication endpoint unavailable, failed, or misconfigured. |

## Sign Out

```http
DELETE /internal/dashboard/session
X-Dashboard-Session: {dashboardSessionId}
```

Dashboard verifies Dashboard session and Authentication, then marks local Dashboard session inactive.

Success:

```json
{ "ok": true }
```

Errors:

| Status | Error | Cause |
| --- | --- | --- |
| `401` | `dashboard_session_required` | Dashboard session missing, invalid, inactive, or signed out. |
| `401` | `authentication_session_required` | Authentication rejected, missing, expired, blocked, or unsupported. |
| `401` | `authentication_session_mismatch` | Authentication user differs from Dashboard session user. |
| `502` | `authentication_session_unavailable` | Authentication endpoint unavailable, failed, or misconfigured. |

## Health And Readiness

```http
GET /healthz
```

Success:

```json
{ "ok": true }
```

```http
GET /readyz
```

Returns `200` with `{ "ok": true }` when DB adapter can run trivial query. Returns `503` with `{ "ok": false, "error": "..." }` when DB readiness fails.
