# Graph Report - .  (2026-07-22)

## Corpus Check
- Corpus is ~8,409 words - fits in a single context window. You may not need a graph.

## Summary
- 232 nodes · 436 edges · 17 communities (15 shown, 2 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Test Dashboard Backend Dashboardbackendtest
- Dashboard
- Dashboard Backend Main
- Handoff.Md::Backup Module Downstream
- Dashboard Backend Auth
- Dashboard Backend Repository
- Api-Contract.Md::Get Internal Dashboard
- Handoff.Md::Disclaimer Concept
- Handoff.Md::Dashboardserver
- Package
- Handoff.Md::Auth Base Url
- Handoff.Md::Ari Morgan
- Handoff.Md::X Dashboard Session
- Handoff.Md::Authsessionerror
- Dashboard Backend Init
- Requirements.Txt::Python Dependencies

## God Nodes (most connected - your core abstractions)
1. `Dashboard Module (v1.2.0)` - 20 edges
2. `dashboard_backend/main.py` - 19 edges
3. `DashboardRepository` - 18 edges
4. `DashboardServer` - 18 edges
5. `DashboardBackendTest` - 16 edges
6. `request_json()` - 15 edges
7. `renderWorkspace()` - 13 edges
8. `SQLiteAdapter` - 13 edges
9. `MockAuthenticationServer` - 11 edges
10. `fetch_auth_identity()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `AuthSessionNormalizationTest` --uses--> `DashboardRepository`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/repository.py
- `DashboardBackendTest` --uses--> `DashboardRepository`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/repository.py
- `DashboardServer` --uses--> `DashboardRepository`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/repository.py
- `MockAuthenticationServer` --uses--> `DashboardRepository`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/repository.py
- `GET /readyz (Readiness Check)` ----> `dashboard_backend/main.py`  [EXTRACTED]
  api-contract.md → HANDOFF.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **** — HANDOFF.md::Dashboard_Module, HANDOFF.md::Authentication_Module, api-contract.md::POST_internal_dashboard_session [INFERRED]
- **** — HANDOFF.md::Dashboard_Module, HANDOFF.md::Authentication_Module, api-contract.md::GET_internal_dashboard_workspace [INFERRED]
- **** — HANDOFF.md::dashboard_backend_main, HANDOFF.md::Mock_Auth_System, HANDOFF.md::MOCK_AUTH_USERS, HANDOFF.md::MOCK_AUTH_SESSIONS [INFERRED]
- **** — HANDOFF.md::dashboard_backend_main, HANDOFF.md::require_session, HANDOFF.md::require_auth_identity, HANDOFF.md::normalize_auth_identity [INFERRED]
- **** — HANDOFF.md::DashboardRepository, HANDOFF.md::DatabaseAdapter_Protocol, HANDOFF.md::SQLiteAdapter, HANDOFF.md::Postgres_Upgrade_Path [INFERRED]
- **** — HANDOFF.md::dashboard_backend_db, dataset-schema.md::dashboard_sessions_Table, dataset-schema.md::workspace_events_Table [INFERRED]
- **** — HANDOFF.md::Dashboard_Module, HANDOFF.md::MODULE_BUTTONS, HANDOFF.md::Workspace_Button_Contracts, HANDOFF.md::Module_Route_Placeholders [INFERRED]

## Communities (17 total, 2 thin omitted)

### Community 0 - "Test Dashboard Backend Dashboardbackendtest"
Cohesion: 0.13
Nodes (11): SQLite adapter. Repository owns SQL, so Postgres can replace adapter later., SQLiteAdapter, auth_payload(), AuthSessionNormalizationTest, create_session(), DashboardBackendTest, DashboardServer, free_port() (+3 more)

### Community 1 - "Dashboard"
Cohesion: 0.15
Nodes (28): acceptDisclaimer(), activateDevRole(), api, app, buttonMeta(), clearUrl(), escapeHtml(), fmtDate() (+20 more)

### Community 2 - "Dashboard Backend Main"
Cohesion: 0.17
Nodes (26): accept_disclaimer(), create_dashboard_session(), dashboard_index(), delete_dashboard_session(), display_name_for(), healthz(), http_exception_handler(), json_error() (+18 more)

### Community 3 - "Handoff.Md::Backup Module Downstream"
Cohesion: 0.09
Nodes (26): Backup Module (Downstream), Bayesian Module (Downstream), DashboardRepository, Dashboard Module (v1.2.0), DatabaseAdapter Protocol, FastAPI Backend (dashboard_backend/), FastAPI Framework, Guideline Module (Downstream) (+18 more)

### Community 4 - "Dashboard Backend Auth"
Cohesion: 0.21
Nodes (19): auth_session_url(), AuthSessionError, _blocked_auth_session(), fetch_auth_identity(), _fetch_json(), forwarded_auth_headers(), _has_blocked_status(), _has_truthy_flag() (+11 more)

### Community 5 - "Dashboard Backend Repository"
Cohesion: 0.15
Nodes (7): Connection, DatabaseAdapter, DashboardRepository, now_iso(), Any, session_row(), Protocol

### Community 6 - "Api-Contract.Md::Get Internal Dashboard"
Cohesion: 0.21
Nodes (13): Error Envelope Convention, X-Demo-Auth-User Header (Dev Only), dashboard_backend/main.py, dashboard.js (Vanilla JS UI Adapter), styles.css (Layout), DELETE /internal/dashboard/session (Sign Out), GET /api/auth/session (Authentication Verification), GET /healthz (Health Check) (+5 more)

### Community 7 - "Handoff.Md::Disclaimer Concept"
Cohesion: 0.22
Nodes (10): Disclaimer Feature, MODULE_BUTTONS (Role-Scoped Button Config), Module Route Placeholders, Workspace Button Contracts, Workspace Response Model, normalize_auth_identity Function, require_auth_identity Dependency, require_session Dependency (+2 more)

### Community 8 - "Handoff.Md::Dashboardserver"
Cohesion: 0.22
Nodes (9): DashboardServer (Test Fixture), MockAuthenticationServer (Test Fixture), Uvicorn ASGI Server, npm start (Launch Command), npm test (Test Suite Runner), package.json (NPM Config), server.py (Uvicorn Entry Point), test_dashboard_backend.py (Integration Test Suite) (+1 more)

### Community 9 - "Package"
Cohesion: 0.25
Nodes (7): name, private, scripts, start, test, type, version

### Community 10 - "Handoff.Md::Auth Base Url"
Cohesion: 0.29
Nodes (7): AUTH_BASE_URL (Env Config), AUTH_SESSION_TIMEOUT_MS (Env Config), AUTH_SESSION_URL (Env Config), DASHBOARD_DB_PATH (Env Config), PORT Configuration, Settings (config.py), dashboard_backend/config.py

### Community 11 - "Handoff.Md::Ari Morgan"
Cohesion: 0.33
Nodes (6): Ari Morgan (Mock Admin), DASHBOARD_MOCK_AUTH (Env Config), MOCK_AUTH_SESSIONS (In-Memory Dict), MOCK_AUTH_USERS (Dev Users), Mina Rahimi (Mock Psychiatrist), Mock Authentication System

### Community 12 - "Handoff.Md::X Dashboard Session"
Cohesion: 0.50
Nodes (4): X-Dashboard-Session Header, Authentication Credential Forwarding, Dashboard Session ID, POST /internal/dashboard/session

### Community 14 - "Handoff.Md::Authsessionerror"
Cohesion: 0.67
Nodes (3): AuthSessionError Exception, Authentication Module (External), dashboard_backend/auth.py

## Knowledge Gaps
- **45 isolated node(s):** `app`, `params`, `ROLE_META`, `STATUS_META`, `state` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dashboard_backend/main.py` connect `Api-Contract.Md::Get Internal Dashboard` to `Handoff.Md::Backup Module Downstream`, `Handoff.Md::Disclaimer Concept`, `Handoff.Md::Dashboardserver`, `Handoff.Md::Auth Base Url`, `Handoff.Md::Ari Morgan`, `Handoff.Md::X Dashboard Session`, `Handoff.Md::Authsessionerror`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `DashboardRepository` connect `Dashboard Backend Repository` to `Test Dashboard Backend Dashboardbackendtest`, `Dashboard Backend Main`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `SQLiteAdapter` connect `Test Dashboard Backend Dashboardbackendtest` to `Dashboard Backend Main`, `Dashboard Backend Repository`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `Dashboard Module (v1.2.0)` (e.g. with `Backup Module (Downstream)` and `Bayesian Module (Downstream)`) actually correct?**
  _`Dashboard Module (v1.2.0)` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `dashboard_backend/main.py` (e.g. with `dashboard_backend/auth.py` and `dashboard_backend/config.py`) actually correct?**
  _`dashboard_backend/main.py` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `DashboardRepository` (e.g. with `DatabaseAdapter` and `AuthSessionNormalizationTest`) actually correct?**
  _`DashboardRepository` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `DashboardServer` (e.g. with `SQLiteAdapter` and `DashboardRepository`) actually correct?**
  _`DashboardServer` has 2 INFERRED edges - model-reasoned connections that need verification._