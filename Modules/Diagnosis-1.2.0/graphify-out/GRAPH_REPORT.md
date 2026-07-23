# Graph Report - Diagnosis-1.2.0  (2026-07-22)

## Corpus Check
- 57 files · ~90,093 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 588 nodes · 1106 edges · 36 communities (29 shown, 7 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 70 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a359f301`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Diagnosis API Router
- CSRF Test Suite
- Auth Enforcement Tests
- SQLite Persistence Layer
- CSRF Module
- Auth Adapter
- API Self-Check
- Fake Auth HTTP Handler
- HTTP Server
- HANDOFF Doc
- test_discovery.py
- test_readiness.py
- TestCSRF
- TestPersistence
- TestRestContract
- test_routes.py
- TestRestContract
- auth.py
- dashboard.py
- TestClinicianAuthority
- Session
- test_unittest.py
- TestAuditSeam
- build-graph.py
- add-tests.py
- build-graph2.py
- ua-inline-validate.cjs
- auth.py
- _load
- page

## God Nodes (most connected - your core abstractions)
1. `evaluate()` - 23 edges
2. `DiagnosisStore` - 22 edges
3. `Session` - 18 edges
4. `check_readiness()` - 18 edges
5. `main()` - 18 edges
6. `TestCriteriaRules` - 18 edges
7. `TestRestContract` - 18 edges
8. `_reload_config()` - 17 edges
9. `TestPersistence` - 17 edges
10. `resolve_patient()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `TestAuditSeam` --uses--> `Evaluation`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestAuthRejection` --uses--> `Evaluation`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestCSRF` --uses--> `Evaluation`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestPatientIdentity` --uses--> `Evaluation`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestPersistence` --uses--> `Evaluation`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py

## Import Cycles
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/__init__.py`
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/readiness.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/readiness.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/dashboard.py -> diagnosis/deps.py -> diagnosis/__init__.py`

## Communities (36 total, 7 thin omitted)

### Community 0 - "Diagnosis API Router"
Cohesion: 0.12
Nodes (28): Read ``static/index.html`` once per request (no build step)., _read_page(), main(), Embeddable module UI tests for the diagnosis module.  Issue: replace the standal, The previous shell baked a ``<button ... id="back-btn">Back to     dashboard</bu, The previous shell baked ``<header class="topbar"><h1>Insight</h1>...``     dire, When opts.embedded is true, the fn must NOT render the     ``<header class="dm-t, The host needs to mount AND unmount the module cleanly (a     dashboard that swa (+20 more)

### Community 1 - "CSRF Test Suite"
Cohesion: 0.15
Nodes (26): _client(), _free_port(), _Handler, main(), _mint_bad_token(), _mint_valid_token(), BaseHTTPRequestHandler, HTTPServer (+18 more)

### Community 2 - "Auth Enforcement Tests"
Cohesion: 0.11
Nodes (28): _build_session(), Normalize the auth-service payload. Never raises on missing fields —     a parti, _arm_with_csrf(), _client_for(), _exercise(), _free_port(), _Handler, main() (+20 more)

### Community 3 - "SQLite Persistence Layer"
Cohesion: 0.26
Nodes (28): _clear_env(), main(), Settings-adapter tests for the diagnosis module.  Strategy:     - Exercise the `, When ``AUTH_BASE_URL`` is unset, ``auth.AUTH_BASE_URL`` defaults to     the sett, ``dashboard.MODULE_ID`` defaults to the settings-derived id; a     custom ``DIAG, ``app.py`` builds its CORS middleware from ``settings.cors_origins``     (no lon, ``__main__`` builds its ``--host`` / ``--port`` defaults from     ``settings`` (, Re-import ``diagnosis.config`` so ``_load`` re-runs against the     current env. (+20 more)

### Community 4 - "CSRF Module"
Cohesion: 0.27
Nodes (10): Request, Signed double-submit CSRF for the diagnosis module's write routes.  PUT /diagnos, FastAPI dependency. Fail closed (403) on any mismatch.      Mirrors ``auth.requi, Test-only hook (mirrors ``auth.reset_auth_for_tests``). Pin a     known secret s, Constant-time check that ``token`` was signed by this secret., _read_cookie(), _read_header(), require_csrf() (+2 more)

### Community 5 - "Auth Adapter"
Cohesion: 0.13
Nodes (15): 6.1. `GET /diagnosis/_meta`, 6.2. `GET /diagnosis/_csrf`, 6.3. `GET /internal/dashboard/module-routes/{moduleId}`, 6.4. `GET /internal/diagnosis/audit/{code}`, 6. Dashboard discovery seam, Errors, Errors, Errors (+7 more)

### Community 6 - "API Self-Check"
Cohesion: 0.20
Nodes (21): _arm_with_csrf(), _AuthHandler, _client(), _free_port(), main(), _PatientHandler, BaseHTTPRequestHandler, HTTPServer (+13 more)

### Community 7 - "Fake Auth HTTP Handler"
Cohesion: 0.11
Nodes (17): 10. Gotchas that cost time if you don't know, 11. Glossary, 12. If you only read four files, 1. What this module is, 2. Repo layout, 3. The two layers and how to find things, 4. The web page (`static/index.html`), 5. Run it (+9 more)

### Community 8 - "HTTP Server"
Cohesion: 0.05
Nodes (42): 10. Configuration (env knobs → `Settings`), 11. Invariants — break these and you've changed the contract, 12. Patient identity (canonical id from "Add New Patient"), 13. Clinician Authority (the safety contract), 14. Source-of-truth tests, 1. Conventions, 2. Route catalogue, 3. Browser page — `GET /` (+34 more)

### Community 9 - "HANDOFF Doc"
Cohesion: 0.12
Nodes (12): _build_patient(), _fetch_patient(), _PatientNotFound, _PatientUnavailable, Exception, The registry responded 404 — the code is not a known patient., Normalize the registry payload. Fail closed on missing ``id`` —     a partially, Resolve a free-text patient code to the canonical INSIGHT patient.      Honours (+4 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.20
Nodes (14): _client(), _free_port(), _Handler, main(), BaseHTTPRequestHandler, HTTPServer, TestClient, Dashboard discovery-route tests for the diagnosis module.  Mirrors the ``test_au (+6 more)

### Community 15 - "test_readiness.py"
Cohesion: 0.13
Nodes (37): Any, _check_auth(), _check_db(), _check_patient(), check_readiness(), Patient-identity adapter configuration check. The adapter is     opt-in; "disabl, Return the module-local readiness snapshot. Pure: no HTTP, no     env mutation,, Probe the process-wide ``DiagnosisStore``. Imports the store from     ``deps`` a (+29 more)

### Community 16 - "TestCSRF"
Cohesion: 0.14
Nodes (4): _fake_request(), Minimal stand-in for ``fastapi.Request`` for dep-level unittests.     ``auth.req, TestAuthRejection, TestCSRF

### Community 18 - "TestRestContract"
Cohesion: 0.10
Nodes (6): evaluate(), Evaluation, Pure function: given the clinician's checked criteria, return an     Evaluation., Pure-rule + REST contract mix: locks the no-auto-diagnosis invariant., TestClinicianAuthority, TestCriteriaRules

### Community 19 - "test_routes.py"
Cohesion: 0.17
Nodes (20): main(), _paths(), Route-seam split tests for the diagnosis module.  Issue: split public routes fro, Invariant 4: ``/_meta`` and ``/_csrf`` MUST match before     ``/{code}`` or Fast, The Dashboard discovery route lives in ``dashboard.py`` only —     invariant 10, The audit-log route lives in ``dashboard.py`` only — invariant 10     (seam spli, `MODULE_ID` is part of the discovery contract — Dashboard joins on     it and th, Tests + Insight callers import contract symbols from     ``diagnosis.api`` direc (+12 more)

### Community 21 - "auth.py"
Cohesion: 0.15
Nodes (18): BaseModel, API seam for the diagnosis module — the composed router.  The single ``router``, The slice of an Insight auth session this module consumes.      Never holds a to, Session, _dump_for_audit(), JSON snapshot for audit logging. Persisted to the audit table by     ``store.aud, _bypass_dep(), Shared wiring for the diagnosis route seams.  The public router was split into t (+10 more)

### Community 22 - "dashboard.py"
Cohesion: 0.16
Nodes (13): get_criteria(), meta_contract(), DSM-5-TR schizophrenia diagnostic criteria and evaluation engine.  Source: DSM-5, Return the criteria tree, grouped for the UI. Caller must not mutate., Rule contract the browser page consumes for its optimistic display.      The web, audit_log(), meta(), module_routes() (+5 more)

### Community 23 - "TestClinicianAuthority"
Cohesion: 0.10
Nodes (23): Cursor, _http_selfcheck(), Run the REST-contract unittest cases under the bypass shim.      The inline ``as, _config_selfcheck(), Self-verify the adapter. Covers:     - every previously hard-coded default surfa, _demo(), Run the rule-suite unittest cases. Exit non-zero on failure.      Run: ``python, main() (+15 more)

### Community 24 - "Session"
Cohesion: 0.13
Nodes (15): 7.1. `POST /diagnosis/{code}/init`, 7.2. `GET /diagnosis/{code}`, 7.3. `PUT /diagnosis/{code}`, 7. Per-patient diagnosis REST seam, Errors, Errors, Errors, Path parameters (+7 more)

### Community 25 - "test_unittest.py"
Cohesion: 0.13
Nodes (11): Standalone FastAPI app for the diagnosis module.  Usage:     python -m diagnosis, ready(), Settings adapter for the diagnosis module.  Single source of truth for every pre, Patient, Patient identity adapter for the diagnosis module.  Aligns the diagnosis module', Test-only hook: rebind the patient-registry base URL for the     lifetime of the, Canonical patient identity as the diagnosis module consumes it.      ``id`` is t, reset_patient_for_tests() (+3 more)

### Community 33 - "auth.py"
Cohesion: 0.20
Nodes (10): _AuthUnavailable, _fetch_session(), Exception, Canonical Authentication session adapter for Diagnosis., FastAPI dependency factory. Returns a dependency that enforces     membership in, Test-only hook: rebind the auth base URL for the lifetime of the     current pro, The auth service is unreachable or returned a non-JSON body., Call the Insight auth service. Returns the parsed JSON.      Raises ``_AuthUnava (+2 more)

### Community 34 - "_load"
Cohesion: 0.18
Nodes (9): _env_list(), _env_truthy(), _load(), Stable id this module advertises to Dashboard discovery.          Derived from `, ``/modules/<id>`` href the Dashboard descriptor points at.          Stays aligne, Read the env once at import time. Pure; never raises on absence —     every fiel, Comma-separated list env var. Empty / unset -> ``default``.      A single ``*``, Immutable snapshot of every integration knob the module reads.      Frozen so a (+1 more)

### Community 35 - "page"
Cohesion: 0.22
Nodes (10): mint(), Attach an HMAC-SHA256 signature to ``raw``. Returns ``raw.sig``., Mint a fresh signed token. Callers set it as the CSRF cookie and     surface it, Stamp the ``csrf`` cookie on ``response``. FastAPI's     ``set_cookie`` is the p, set_cookie(), _sign(), csrf_token(), Mint a signed double-submit CSRF token. Sets the ``csrf`` cookie     and returns (+2 more)

## Knowledge Gaps
- **70 isolated node(s):** `fs`, `1. What this module is`, `2. Repo layout`, `Layer A — the seams (api.py + 3 sub-seams, app.py, __init__.py, __main__.py)`, `Layer C — the repository (store.py)` (+65 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_config_selfcheck()` connect `TestClinicianAuthority` to `test_unittest.py`, `_load`, `SQLite Persistence Layer`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `DiagnosisStore` connect `TestClinicianAuthority` to `test_unittest.py`, `auth.py`, `test_readiness.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `TestPersistence` connect `TestPersistence` to `test_unittest.py`, `TestRestContract`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `main()` (e.g. with `test_app_cors_reads_settings()` and `test_auth_module_sourced_from_settings()`) actually correct?**
  _`main()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `fs`, `1. What this module is`, `2. Repo layout` to the rest of the system?**
  _70 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Diagnosis API Router` be split into smaller, more focused modules?**
  _Cohesion score 0.1206896551724138 - nodes in this community are weakly interconnected._
- **Should `CSRF Test Suite` be split into smaller, more focused modules?**
  _Cohesion score 0.14532019704433496 - nodes in this community are weakly interconnected._