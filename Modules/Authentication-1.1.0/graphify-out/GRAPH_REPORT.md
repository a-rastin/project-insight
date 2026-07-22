# Graph Report - G:\INSIGHT-Project\Modules\Authentication-1.1.0  (2026-07-12)

## Corpus Check
- Corpus is ~47,681 words - fits in a single context window. You may not need a graph.

## Summary
- 221 nodes · 505 edges · 16 communities (14 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.64)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Authentication Flow
- API Contract
- Documentation & Routes
- Session & Password Management
- Error Handling
- Database Schema
- Version Management
- Application Entry Point
- JWT & Configuration
- Rate Limiting
- Role Management
- Design System
- Input Validation
- Sessions Table
- Login Failures Table

## God Nodes (most connected - your core abstractions)
1. `get_conn()` - 25 edges
2. `_tx()` - 15 edges
3. `AuthTestCase` - 14 edges
4. `_require_csrf()` - 12 edges
5. `_audit()` - 11 edges
6. `cfg()` - 11 edges
7. `_run_migrations()` - 11 edges
8. `_require_admin()` - 10 edges
9. `login()` - 10 edges
10. `change_password()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Authentication v1 Contract` --references--> `Authentication v1 Contract`  [EXTRACTED]
  README.md → docs/Authentication v1 Contract.md
- `FastAPI Web Framework` --powers--> `router.py HTTP Interface`  [INFERRED]
  requirements.txt → docs/Executive Summary.md
- `healthz()` --calls--> `liveness()`  [EXTRACTED]
  main.py → router.py
- `readyz()` --calls--> `readiness()`  [EXTRACTED]
  main.py → router.py
- `Security Properties` --uses--> `bcrypt Password Hashing`  [EXTRACTED]
  README.md → requirements.txt

## Import Cycles
- None detected.

## Communities (16 total, 2 thin omitted)

### Community 0 - "Authentication Flow"
Cohesion: 0.12
Nodes (50): BaseModel, HTTPException, Request, accept_disclaimer(), _account_response(), AccountListResponse, AccountResponse, _audit() (+42 more)

### Community 1 - "API Contract"
Cohesion: 0.08
Nodes (8): assert_auth_schema(), assert_safe_session(), AuthTestCase, AuthContractTests, AuthMigrationTests, AuthRouteTests, SecurityBehaviorTests, SecurityUnitTests

### Community 2 - "Documentation & Routes"
Cohesion: 0.08
Nodes (33): Admin Account Lifecycle, Session Cookie Policy, CSRF Double-Submit Protection, Disclaimer Gating for Psychiatrists, JWT Session Payload, POST /api/auth/login Route, GET /api/auth/session Route, Authentication v1 Contract (+25 more)

### Community 3 - "Session & Password Management"
Cohesion: 0.22
Nodes (15): change_user_password(), get_conn(), hash_password(), list_audit_entries(), Append one audit row. Never raises — audit must not break auth.      `actor` / `, Return audit rows newest-first, capped. Caller (admin route) paginates., Invalidate all active sessions for account disable or password reset., record_audit() (+7 more)

### Community 4 - "Error Handling"
Cohesion: 0.20
Nodes (14): _active_admin_count(), DuplicateUsernameError, LastActiveAdminError, PasswordVerificationError, Exception, Raised when account creation conflicts with an existing username., Raised when an account-management operation targets a missing user., Raised when an operation would remove the final active administrator. (+6 more)

### Community 5 - "Database Schema"
Cohesion: 0.29
Nodes (13): Connection, _migrate_account_state_columns(), _migrate_disclaimer_acceptances(), _migrate_legacy_user_role(), _migration_001_create_users(), _migration_002_create_sessions(), _migration_003_normalize_roles(), _migration_004_account_state_and_login_failures() (+5 more)

### Community 6 - "Version Management"
Cohesion: 0.23
Nodes (10): active_disclaimer_version(), get_user(), get_user_by_id(), list_users(), Return the SQLite schema version stored in the database header., readiness_report(), _safe_check(), schema_version() (+2 more)

### Community 7 - "Application Entry Point"
Cohesion: 0.27
Nodes (10): healthz(), index(), Response, SPA-like fallback so deep links on the login surface resolve to the same     pag, readyz(), spa_fallback(), HealthResponse, liveness() (+2 more)

### Community 8 - "JWT & Configuration"
Cohesion: 0.39
Nodes (9): cfg(), cfg_bool(), cfg_int(), cookie_kwargs(), csrf_cookie_kwargs(), issue_csrf_token(), issue_token(), _now() (+1 more)

### Community 9 - "Rate Limiting"
Cohesion: 0.33
Nodes (9): login_attempt_allowed(), _login_attempt_scope(), _login_failure_limit(), _login_failure_window_seconds(), _login_lockout_seconds(), _prune_login_failures(), Return whether a login attempt should be evaluated for this principal.      This, record_login_failure() (+1 more)

### Community 10 - "Role Management"
Cohesion: 0.29
Nodes (7): _get_session_record(), is_psychiatrist_role(), normalize_role(), Return the canonical API/storage role for accepted role aliases., Resolve a token into the current account state.      JWTs are only signed snapsh, resolve_session(), verify_token()

### Community 11 - "Design System"
Cohesion: 0.67
Nodes (3): Carbon Health Design System, Five-State Clinical Status System, Teal as Clinical Trust

### Community 12 - "Input Validation"
Cohesion: 0.67
Nodes (3): InvalidRoleError, Raised when a caller asks for a role outside the auth domain., ValueError

## Knowledge Gaps
- **14 isolated node(s):** `Five-State Clinical Status System`, `Admin and Psychiatrist Roles`, `Session Cookie Policy`, `JWT Session Payload`, `Admin Account Lifecycle` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Five-State Clinical Status System`, `Admin and Psychiatrist Roles`, `Session Cookie Policy` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Authentication Flow` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Should `API Contract` be split into smaller, more focused modules?**
  _Cohesion score 0.08095238095238096 - nodes in this community are weakly interconnected._
- **Should `Documentation & Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.07954545454545454 - nodes in this community are weakly interconnected._