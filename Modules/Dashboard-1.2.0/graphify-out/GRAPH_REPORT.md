# Graph Report - Dashboard-1.2.0  (2026-07-22)

## Corpus Check
- 15 files · ~8,401 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 216 nodes · 400 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b82b9358`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Auth & Session Management
- Test Suite
- Database Layer
- API Routes
- Auth REST Client
- Package Config
- Workspace Model
- Architecture Patterns
- Backend Init
- Dashboard — Module Handoff
- Dashboard API Contract: INSIGHT Workspace
- Dashboard Module
- Dashboard Dataset Schema

## God Nodes (most connected - your core abstractions)
1. `DashboardRepository` - 18 edges
2. `DashboardServer` - 18 edges
3. `DashboardBackendTest` - 16 edges
4. `request_json()` - 15 edges
5. `renderWorkspace()` - 13 edges
6. `SQLiteAdapter` - 13 edges
7. `MockAuthenticationServer` - 11 edges
8. `fetch_auth_identity()` - 10 edges
9. `renderAccess()` - 9 edges
10. `Dashboard — Module Handoff` - 9 edges

## Surprising Connections (you probably didn't know these)
- `AuthSessionNormalizationTest` --uses--> `SQLiteAdapter`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/db.py
- `DashboardBackendTest` --uses--> `SQLiteAdapter`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/db.py
- `DashboardServer` --uses--> `SQLiteAdapter`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/db.py
- `MockAuthenticationServer` --uses--> `SQLiteAdapter`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/db.py
- `AuthSessionNormalizationTest` --uses--> `DashboardRepository`  [INFERRED]
  test_dashboard_backend.py → dashboard_backend/repository.py

## Import Cycles
- None detected.

## Communities (14 total, 1 thin omitted)

### Community 0 - "Auth & Session Management"
Cohesion: 0.11
Nodes (35): Authentication Boundary, Authentication REST Client, acceptDisclaimer(), activateDevRole(), api, app, buttonMeta(), clearUrl() (+27 more)

### Community 1 - "Test Suite"
Cohesion: 0.17
Nodes (9): auth_payload(), AuthSessionNormalizationTest, create_session(), DashboardBackendTest, DashboardServer, free_port(), future_iso(), MockAuthenticationServer (+1 more)

### Community 2 - "Database Layer"
Cohesion: 0.11
Nodes (9): Connection, DatabaseAdapter, SQLite adapter. Repository owns SQL, so Postgres can replace adapter later., SQLiteAdapter, DashboardRepository, now_iso(), Any, session_row() (+1 more)

### Community 3 - "API Routes"
Cohesion: 0.17
Nodes (26): accept_disclaimer(), create_dashboard_session(), dashboard_index(), delete_dashboard_session(), display_name_for(), healthz(), http_exception_handler(), json_error() (+18 more)

### Community 4 - "Auth REST Client"
Cohesion: 0.21
Nodes (19): auth_session_url(), AuthSessionError, _blocked_auth_session(), fetch_auth_identity(), _fetch_json(), forwarded_auth_headers(), _has_blocked_status(), _has_truthy_flag() (+11 more)

### Community 5 - "Package Config"
Cohesion: 0.25
Nodes (7): name, private, scripts, start, test, type, version

### Community 6 - "Workspace Model"
Cohesion: 0.53
Nodes (6): ADMIN Role, Disclaimer Acceptance, Module Placeholders, PSYCHIATRIST Role, Role-Scoped Buttons, INSIGHT Workspace

### Community 7 - "Architecture Patterns"
Cohesion: 0.67
Nodes (4): DatabaseAdapter Protocol, Postgres Adapter, Repository Pattern, SQLite Persistence

### Community 10 - "Dashboard — Module Handoff"
Cohesion: 0.11
Nodes (18): 1. What this module is, 2. Current state of the working tree, 3. Architecture, 4. How to run, 5. Known gaps and things still owed, 6. Workspace button contracts (for reference), 7. Where to look first when changing something, 8. Etiquette for upstream changes (+10 more)

### Community 11 - "Dashboard API Contract: INSIGHT Workspace"
Cohesion: 0.20
Nodes (9): Auth Verification Contract, Create Dashboard Session, Dashboard API Contract: INSIGHT Workspace, Disclaimer Acceptance, Health And Readiness, INSIGHT Workspace Response, Module-Link Placeholders, Primary INSIGHT Flow (+1 more)

### Community 12 - "Dashboard Module"
Cohesion: 0.22
Nodes (8): Dashboard Module, Files, Health, Module Interface, Postgres Upgrade Path, Run, Test, Workspace Rules

### Community 13 - "Dashboard Dataset Schema"
Cohesion: 0.25
Nodes (7): Dashboard Dataset Schema, dashboard_sessions, Explicit Non-Owners, Module Route Placeholders, Tables, workspace_events, Workspace Strings

## Knowledge Gaps
- **50 isolated node(s):** `app`, `params`, `ROLE_META`, `STATUS_META`, `state` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DashboardRepository` connect `Database Layer` to `Test Suite`, `API Routes`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `SQLiteAdapter` connect `Database Layer` to `Test Suite`, `API Routes`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `DashboardServer` connect `Test Suite` to `Database Layer`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `DashboardRepository` (e.g. with `DatabaseAdapter` and `AuthSessionNormalizationTest`) actually correct?**
  _`DashboardRepository` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `DashboardServer` (e.g. with `SQLiteAdapter` and `DashboardRepository`) actually correct?**
  _`DashboardServer` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `DashboardBackendTest` (e.g. with `SQLiteAdapter` and `DashboardRepository`) actually correct?**
  _`DashboardBackendTest` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `renderWorkspace()` (e.g. with `acceptDisclaimer()` and `signOut()`) actually correct?**
  _`renderWorkspace()` has 2 INFERRED edges - model-reasoned connections that need verification._