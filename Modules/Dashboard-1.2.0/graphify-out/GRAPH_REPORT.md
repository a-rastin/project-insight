# Graph Report - .  (2026-07-25)

## Corpus Check
- 11 files · ~10,111 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 268 nodes · 522 edges · 15 communities (12 shown, 3 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 35 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 12
- Community 13
- Community 14

## God Nodes (most connected - your core abstractions)
1. `DashboardServer` - 24 edges
2. `DashboardBackendTest` - 23 edges
3. `DashboardRepository` - 21 edges
4. `request_json()` - 20 edges
5. `Dashboard Module (v1.2.0)` - 19 edges
6. `SQLiteAdapter` - 14 edges
7. `MockAuthenticationServer` - 14 edges
8. `renderWorkspace()` - 13 edges
9. `dashboard_backend/main.py` - 12 edges
10. `fetch_auth_identity()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `AuthSessionNormalizationTest` --uses--> `SQLiteAdapter`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/db.py
- `DashboardBackendTest` --uses--> `SQLiteAdapter`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/db.py
- `DashboardServer` --uses--> `SQLiteAdapter`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/db.py
- `MockAuthenticationServer` --uses--> `SQLiteAdapter`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/db.py
- `MockModuleServer` --uses--> `SQLiteAdapter`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/db.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Authenticated Workspace Flow** — api_contract_authentication_session_endpoint, api_contract_dashboard_session_endpoint, api_contract_workspace_endpoint, api_contract_dashboard_session [EXTRACTED 1.00]
- **Protected Workflow Operations** — api_contract_module_route_discovery, api_contract_workflow_context, api_contract_disclaimer_acceptance, api_contract_sign_out [EXTRACTED 1.00]

## Communities (15 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (40): AUTH_BASE_URL (Env Config), AUTH_SESSION_TIMEOUT_MS (Env Config), AUTH_SESSION_URL (Env Config), Ari Morgan (Mock Admin), AuthSessionError Exception, Authentication Module (External), DASHBOARD_DB_PATH (Env Config), DASHBOARD_MOCK_AUTH (Env Config) (+32 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (10): auth_payload(), create_session(), DashboardBackendTest, DashboardServer, free_port(), future_iso(), MockAuthenticationServer, MockModuleServer (+2 more)

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (30): accept_disclaimer(), canonical_uuid(), create_dashboard_session(), create_workflow_context(), dashboard_index(), dashboard_spa_fallback(), delete_dashboard_session(), discover_registered_module() (+22 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (9): Connection, DatabaseAdapter, SQLite adapter. Repository owns SQL, so Postgres can replace adapter later., SQLiteAdapter, DashboardRepository, now_iso(), Any, session_row() (+1 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (28): acceptDisclaimer(), activateDevRole(), api, app, buttonMeta(), clearUrl(), escapeHtml(), fmtDate() (+20 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (23): Backup Module (Downstream), Bayesian Module (Downstream), DashboardRepository, Dashboard Module (v1.2.0), DatabaseAdapter Protocol, FastAPI Backend (dashboard_backend/), FastAPI Framework, Guideline Module (Downstream) (+15 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (22): ADMIN Role, Authentication Session Endpoint, authentication_session_mismatch Error, authentication_session_required Error, authentication_session_unavailable Error, Dashboard Configuration, Dashboard Local Session, Create Dashboard Session Endpoint (+14 more)

### Community 7 - "Community 7"
Cohesion: 0.26
Nodes (12): auth_session_url(), AuthSessionError, fetch_auth_identity(), _fetch_json(), forwarded_auth_headers(), normalize_auth_identity(), _parse_expiry(), Any (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.42
Nodes (6): Settings, discover_module(), ModuleRegistration, Any, ready_url_for(), _request_json()

### Community 9 - "Community 9"
Cohesion: 0.22
Nodes (8): Dashboard Module, Files, Health, Module Interface, Postgres Upgrade Path, Run, Test, Workspace Rules

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (7): name, private, scripts, start, test, type, version

## Knowledge Gaps
- **57 isolated node(s):** `name`, `version`, `private`, `type`, `start` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DashboardRepository` connect `Community 3` to `Community 1`, `Community 2`, `Community 7`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `SQLiteAdapter` connect `Community 3` to `Community 1`, `Community 2`, `Community 7`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `DashboardServer` (e.g. with `SQLiteAdapter` and `DashboardRepository`) actually correct?**
  _`DashboardServer` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `DashboardBackendTest` (e.g. with `SQLiteAdapter` and `DashboardRepository`) actually correct?**
  _`DashboardBackendTest` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `DashboardRepository` (e.g. with `DatabaseAdapter` and `AuthSessionNormalizationTest`) actually correct?**
  _`DashboardRepository` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Dashboard Module (v1.2.0)` (e.g. with `Backup Module (Downstream)` and `Bayesian Module (Downstream)`) actually correct?**
  _`Dashboard Module (v1.2.0)` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `private` to the rest of the system?**
  _57 weakly-connected nodes found - possible documentation gaps or missing edges._