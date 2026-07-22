# Dashboard — Module Handoff

**Repo:** `a-rastin/Dashboard` · **Branch:** `main` · **As of:** 2026-07-06

---

## 1. What this module is

Dashboard is a **workspace router** — a thin, embeddable FastAPI app that verifies an Authentication session over REST, binds it to a Dashboard-local session, and returns a role-scoped workspace shell with placeholder buttons that discover downstream module routes.

It deliberately owns **only** the navigation shell. It does *not* implement patient, treatment, logs, backup, user-management, guideline, Bayesian, or admin oversight logic. Those live in their own downstream modules at `/modules/{moduleId}`.

Boundary rule (inviolable): **internal REST only**. Dashboard never imports Authentication code, decodes JWTs, reads an auth DB, or implements downstream module workflows.

---

## 2. Current state of the working tree

⚠️ **Out of sync with origin.** This is a hard-cut rewrite from a Node.js server (`server.mjs`) to a Python FastAPI backend (`dashboard_backend/`). Status:

| Ref | Contents |
| --- | --- |
| `origin/main` | `a837587` — the old Node `server.mjs` version. **No Python backend exists on the remote.** |
| local `main` HEAD | `57ff7f8` — "Lock dashboard auth boundary" (still Node-based, per the diff stats). |
| **Uncommitted working tree** | The FastAPI rewrite. `dashboard_backend/`, `server.py`, `requirements.txt`, `test_dashboard_backend.py`, `test_dashboard_frontend.mjs`, `.gitignore` are all untracked or modified. `server.mjs` / `server.test.mjs` are staged for deletion. |

**Action required before any handoff is meaningful**: stage and commit the FastAPI rewrite on a feature branch, refactor off `main`, and push. The current HEAD commit is not the FastAPI code that the docs describe.

### Git status snapshot

```
M  HANDOFF.md, README.md, api-contract.md, dashboard.js
M  dataset-schema.md, index.html, package.json, styles.css
D  server.mjs, server.test.mjs          # old Node impl, removed
?? .gitignore, dashboard_backend/, requirements.txt
?? server.py, test_dashboard_backend.py, test_dashboard_frontend.mjs
```

### Verification status (tests pass on the working tree)

- `python -m unittest` → **15 tests, OK** (12.4s). Covers auth normalization, session creation from verified identity, exact workspace button contracts, module-route placeholders, absence of a Dashboard patient-mutation endpoint, sign-out behavior, expiry enforcement, role-change-is-not-spoofable, contract against a mocked Authentication server, health, readiness, and dataset-schema table isolation.
- `node test_dashboard_frontend.mjs` → **passing** (asserts psychiatrist and ADMIN workspace render expected display names and button titles, doctor prefix logic, date formatting).

`npm test` runs both.

---

## 3. Architecture

```
index.html                 ← static entry, mounts #app
styles.css                 ← layout, single CSS file
dashboard.js               ← vanilla JS UI adapter (loads #app, talks to REST)
server.py                  ← one line: `from dashboard_backend.main import app` (uvicorn entry)
package.json               ← npm `start` shells out to uvicorn; `test` runs unittest + node
requirements.txt           ← fastapi, uvicorn  (only two deps)
dashboard_backend/
  __init__.py
  config.py                ← env-driven Settings
  auth.py                  ← Authentication REST client + identity normalization
  db.py                    ← DatabaseAdapter Protocol + SQLiteAdapter + DDL
  repository.py            ← DashboardRepository — owns all SQL
  main.py                  ← FastAPI app, routes, mock-auth dev endpoint, workspace model
test_dashboard_backend.py  ← unittest integration suite, spins up uvicorn in-process
test_dashboard_frontend.mjs← node assert-based render suite
api-contract.md            ← canonical REST contract (source of truth for the API)
dataset-schema.md          ← Dashboard-local persistence + workspace strings
HANDOFF.md                 ← this file
```

### Request flow (primary INSIGHT contract)

1. Host calls `POST /internal/dashboard/session` with Authentication credentials (`Authorization` | `Cookie` | `X-Auth-Session`).
2. Dashboard calls `GET /api/auth/session` (real or mock). **Request-body identity is ignored** — Authentication is the source of truth.
3. Dashboard creates a local `dashboard_sessions` row bound to verified `user.id`, `role`, and Authentication session id; records `session_created` event.
4. UI calls `GET /internal/dashboard/workspace?session={id}` (or `summary`).
5. Dashboard re-validates the local session **and** re-calls `GET /api/auth/session`; rejects user mismatch, expired/blocked auth sessions; refreshes role + authSessionId from verified identity.
6. Returns INSIGHT workspace metadata: `displayName`, `currentDateTime`, `workspace.{kind,title,buttons}`, psychiatrist responses add `requiresDisclaimer` + `disclaimer`.
7. Each button carries `routeDiscovery: { method: "GET", href: "/internal/dashboard/module-routes/{moduleId}" }`. UI hits that to get a placeholder `{ moduleId, title, href: "/modules/{moduleId}", placeholder: true }`.

Every protected endpoint routes through `require_session` (Depends), which runs `require_auth_identity` and enforces `user.id == session.userId`.

### Auth identity normalization (`auth.py:146` `normalize_auth_identity`)

Accepts the Authentication JSON shape from `api-contract.md` (plus field-name variants) and rejects:
- missing/empty auth session id
- `authenticated: false` / inactive session
- blocked statuses: `expired`, `force_password_change`, `forced_password_reset`, `password_reset_required`, `disclaimer_blocked`, `disclaimer_required`, etc.
- truthy expired/password-reset/disclaimer flags across `data`, `session`, `user`
- unsupported role (only `PSYCHIATRIST` and `ADMIN`)
- missing user id

Normalizes the user to `{ id, role, fullName, title }` (defaults `title` to `"Dr."` for psychiatrists). Auth transport failures → `AuthSessionError` → HTTP `502 authentication_session_unavailable`. Auth 401/403 → no identity → HTTP `401 authentication_session_required`.

### Persistence (`db.py`, `repository.py`)

SQLite only, behind a `DatabaseAdapter` Protocol so a Postgres adapter can drop in. Schema DDL on `db.py:8-34` creates exactly two tables:

- `dashboard_sessions(id, user_id, role, auth_session_id, active, created_at, disclaimer_accepted_at)` with role CHECK constraint
- `workspace_events(id, dashboard_session_id, user_id, role, event_type, at)` with FK to sessions

Schema also `DROP`s legacy `dashboard_profiles`, `logins`, `mock_auth_sessions` (leftover from prior iterations) and `ALTER`s `disclaimer_accepted_at` in if missing — so the same DDL works against both fresh and pre-existing DBs.

**Dashboard does not store** Authentication users/profiles/passwords, clinical patient records, admin oversight data, guideline data, Bayesian models, backup payloads, or downstream module data. `test_dataset_schema_keeps_only_dashboard_owned_tables` enforces the table set.

### Standalone dev/mock auth

If neither `AUTH_SESSION_URL` nor `AUTH_BASE_URL` is set, `DASHBOARD_MOCK_AUTH` defaults to on (mock on unless explicitly `=0`). Then `GET /api/auth/session` is served in-process by `main.py:161 mock_auth_session`, keyed off `X-Demo-Auth-User` (`psy-1` psychiatrist "Mina Rahimi" or `admin-1` admin "Ari Morgan"). Mock auth state is in-memory (`MOCK_AUTH_SESSIONS` dict) — never persisted.

**`X-Demo-Auth-User` is a dev/test header only — not the production contract.** Never accept it from a real caller; never document it as a supported auth path.

### Disclaimer

Only `PSYCHIATRIST` responses include `requiresDisclaimer` and `disclaimer`. `POST /internal/dashboard/disclaimer/accept` (403 `psychiatrist_only` for admins) stamps `disclaimer_accepted_at` on the session row and returns the updated workspace. Until accepted, the frontend disables module launch buttons.

### Error envelope

All HTTP errors return `{ "error": "<code>" }` (optionally `+ detail`). The exception handler at `main.py:50` unwraps `HTTPException(detail={"error": ...})`. Codes used:

- `dashboard_session_required` — 401: missing/inactive/signed-out local session
- `authentication_session_required` — 401: auth rejected/missing/expired/blocked/unsupported
- `authentication_session_mismatch` — 401: verified auth user id ≠ dashboard session user id
- `authentication_session_unavailable` — 502: auth endpoint unreachable/misconfigured
- `module_route_not_available` — 404: moduleId not in caller's role button set
- `psychiatrist_only` — 403: disclaimer accept attempted by an ADMIN

---

## 4. How to run

```powershell
# Backend (FastAPI on 127.0.0.1:4173, mock auth on by default)
npm start
# or: python -m uvicorn dashboard_backend.main:app --host 127.0.0.1 --port 4173

# Open the workspace
#   http://localhost:4173/dashboard/        (auto-activates a mock session)
#   http://localhost:4173/dashboard/?session=<id>

# Tests (runs python unittest + node frontend suite)
npm test
# or individually:
python -m unittest
node test_dashboard_frontend.mjs
```

### Config (env vars)

| Variable | Default | Meaning |
| --- | --- | --- |
| `AUTH_SESSION_URL` | — | Exact Authentication session URL. |
| `AUTH_BASE_URL` | — | Base URL; Dashboard appends `/api/auth/session`. |
| `DASHBOARD_MOCK_AUTH` | `1` if no auth URL set, else unset | `1` enables mock auth; `0` disables. |
| `DASHBOARD_DB_PATH` | `./dashboard.sqlite3` | SQLite path. |
| `AUTH_SESSION_TIMEOUT_MS` | `2000` | Outbound auth request timeout in ms. |
| `PORT` | `4173` | Settings field (not currently wired into the `npm start` command — uvicorn uses the CLI flag). |

Integrated deployments set `AUTH_BASE_URL` or `AUTH_SESSION_URL` and `DASHBOARD_MOCK_AUTH=0`.

---

## 5. Known gaps and things still owed

These are **not** TODO comments in the code (none exist) — they are observations from the handoff review.

1. **Uncommitted FastAPI rewrite.** The whole point of this handoff: the working tree is the FastAPI version, the remote is the Node version. Stage and commit before anything else. The `57ff7f8` HEAD commit does not contain the Python code.
2. **`PORT` env var is read by `Settings` (`config.py:11`) but unused.** `npm start` hard-codes `--port 4173`. Either wire `PORT` through (e.g. `--port ${PORT:-4173}`) or delete the field. One tiny edit either way.
3. **`AuthSessionError` is the only transport-error path**, and it collapses all non-auth HTTP statuses to `502`. If Authentication ever returns structured codes (e.g. rate limit, maintenance), the contract will need a sub-code. Fine for now; flag if Authentication grows.
4. **No rate limiting / abuse protection.** The boundary assumes the host app front-ends Dashboard. If Dashboard is ever exposed directly, add rate limiting at the auth-boundary routes.
5. **Mock auth is in-memory** and shares nothing across workers. Single-process `npm start` is fine; multi-worker uvicorn will silently break role simulation. Don't scale mock auth horizontally — turn it off.
6. **SQLite is a single file** (`dashboard.sqlite3`, gitignored). Production should swap in the Postgres adapter promised by the `DatabaseAdapter` Protocol in `db.py:37`. The repository owns all SQL, so the adapter swap should be a contained change.
7. **Frontend has no build step** — vanilla JS module in `dashboard.js`. Fine for now; if a build pipeline lands (TS, bundler), revisit.
8. **`api-contract.md` is the canonical REST contract.** `README.md` and `HANDOFF.md` are summaries; if they disagree, `api-contract.md` wins.
9. **`test_dashboard_frontend.mjs` is render-output assertion only.** It does not exercise the real FastAPI backend (no http server in that suite). The backend test covers the HTTP contract; the frontend test covers HTML rendering. Neither covers the full end-to-end JS↔FastAPI loop.
10. **`uvicorn.log`, `uvicorn.err.log`, `uvicorn.pid`, `dashboard.sqlite3` are gitignored** and therefore intentionally not committed. They are runtime artifacts, not source.

---

## 6. Workspace button contracts (for reference)

| Role | Button ids → titles |
| --- | --- |
| `PSYCHIATRIST` | `add-new-patient`→"Add New Patient", `patient-follow-up`→"Patient Follow-up", `list-of-patients`→"List of Patients", `setting`→"Setting" |
| `ADMIN` | `add-new-user`→"Add New User", `logs`→"Logs", `backup`→"Backup", `list-of-users`→"List of Users" |

- Psychiatrist `displayName` = `Dr. {fullName}` (idempotent if already prefixed).
- Admin `displayName` = `{fullName}`.
- `workspace.title` is always `"Workspace"`. `workspace.kind` mirrors the verified role.

---

## 7. Where to look first when changing something

| If you need to… | Start at |
| --- | --- |
| Add/rename a workspace button or fix role scoping | `dashboard_backend/main.py:21` `MODULE_BUTTONS` + `main.py:110` `workspace_buttons` |
| Change the REST contract shape | `api-contract.md` first, then `main.py` routes |
| Add a new endpoint | `main.py` route + a `require_session` dependency if protected; record an event in `repository.py` if it's a shell event |
| Tweak auth rejection rules | `dashboard_backend/auth.py:19` (blocked sets) and `auth.py:133` `_blocked_auth_session` |
| Swap SQLite → Postgres | `dashboard_backend/db.py` — implement a new `DatabaseAdapter`; repository owns no driver-specific code |
| Change dev mock users | `dashboard_backend/main.py:36` `MOCK_AUTH_USERS` |
| Restyle the UI | `styles.css` (single file, CSS custom properties at top) |
| Update the JS render flow | `dashboard.js` (`renderWorkspace`, `load`, `signOut`) |
| Add a backend integration test | `test_dashboard_backend.py` — use `DashboardServer` (boots uvicorn in-thread) and `MockAuthenticationServer` for auth |

---

## 8. Etiquette for upstream changes

- **Run `npm test` before pushing.** The unittest suite spins up a real uvicorn in-process; failures catch contract regressions.
- **Do not weaken the auth boundary.** Every new protected route must `Depends(require_session)` and must not trust request-body identity fields.
- **Do not delete the role CHECK constraint** in the schema or accept new roles without updating `MODULE_BUTTONS`, the contract, and the tests.
- **Keep tables to `dashboard_sessions` and `workspace_events` only.** Adding a third means Dashboard is owning a dataset it shouldn't — push that to the downstream module instead.
- **Keep `placeholder: true` honest.** If a module route ever returns a real payload, the boundary has been broken — that belongs in the target module, not Dashboard.
