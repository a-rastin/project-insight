# Graph Report - Diagnosis-1.2.0  (2026-07-22)

## Corpus Check
- 56 files · ~90,510 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 585 nodes · 1101 edges · 33 communities (25 shown, 8 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 70 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e60a821a`
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
- `TestClinicianAuthority` --uses--> `Evaluation`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestCriteriaRules` --uses--> `Evaluation`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestCSRF` --uses--> `Evaluation`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py

## Import Cycles
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/readiness.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/readiness.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/dashboard.py -> diagnosis/deps.py -> diagnosis/__init__.py`

## Communities (33 total, 8 thin omitted)

### Community 0 - "Diagnosis API Router"
Cohesion: 0.10
Nodes (31): page(), Browser page seam for the diagnosis module.  The single ``GET /`` route serves, Read ``static/index.html`` once per request (no build step)., Serve the SPA. Stamp a fresh signed CSRF token into the page     (``<meta name=, _read_page(), main(), Embeddable module UI tests for the diagnosis module.  Issue: replace the stand, The previous shell baked a ``<button ... id="back-btn">Back to     dashboard</b (+23 more)

### Community 1 - "CSRF Test Suite"
Cohesion: 0.15
Nodes (26): _client(), _free_port(), _Handler, main(), _mint_bad_token(), _mint_valid_token(), BaseHTTPRequestHandler, HTTPServer (+18 more)

### Community 2 - "Auth Enforcement Tests"
Cohesion: 0.14
Nodes (23): _arm_with_csrf(), _client_for(), _exercise(), _free_port(), _Handler, main(), BaseHTTPRequestHandler, HTTPServer (+15 more)

### Community 3 - "SQLite Persistence Layer"
Cohesion: 0.26
Nodes (28): _clear_env(), main(), Settings-adapter tests for the diagnosis module.  Strategy:     - Exercise th, When ``AUTH_BASE_URL`` is unset, ``auth.AUTH_BASE_URL`` defaults to     the set, ``dashboard.MODULE_ID`` defaults to the settings-derived id; a     custom ``DIA, ``app.py`` builds its CORS middleware from ``settings.cors_origins``     (no lo, ``__main__`` builds its ``--host`` / ``--port`` defaults from     ``settings``, Re-import ``diagnosis.config`` so ``_load`` re-runs against the     current env (+20 more)

### Community 4 - "CSRF Module"
Cohesion: 0.16
Nodes (16): mint(), Request, Signed double-submit CSRF for the diagnosis module's write routes.  PUT /diagnos, FastAPI dependency. Fail closed (403) on any mismatch.      Mirrors ``auth.requi, Test-only hook (mirrors ``auth.reset_auth_for_tests``). Pin a     known secret s, Attach an HMAC-SHA256 signature to ``raw``. Returns ``raw.sig``., Constant-time check that ``token`` was signed by this secret., Mint a fresh signed token. Callers set it as the CSRF cookie and     surface it (+8 more)

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
Cohesion: 0.06
Nodes (37): _http_selfcheck(), Run the REST-contract unittest cases under the bypass shim.      The inline ``, _config_selfcheck(), _env_list(), _env_truthy(), _load(), Settings adapter for the diagnosis module.  Single source of truth for every p, Stable id this module advertises to Dashboard discovery.          Derived from (+29 more)

### Community 11 - "test_discovery.py"
Cohesion: 0.20
Nodes (14): _client(), _free_port(), _Handler, main(), BaseHTTPRequestHandler, HTTPServer, TestClient, Dashboard discovery-route tests for the diagnosis module.  Mirrors the ``test_ (+6 more)

### Community 15 - "test_readiness.py"
Cohesion: 0.07
Nodes (51): Any, Cursor, Standalone FastAPI app for the diagnosis module.  Usage:     python -m diagnosis, ready(), _check_auth(), _check_db(), _check_patient(), check_readiness() (+43 more)

### Community 16 - "TestCSRF"
Cohesion: 0.14
Nodes (4): _fake_request(), Minimal stand-in for ``fastapi.Request`` for dep-level unittests.     ``auth.re, TestAuthRejection, TestCSRF

### Community 18 - "TestRestContract"
Cohesion: 0.18
Nodes (3): evaluate(), Pure function: given the clinician's checked criteria, return an     Evaluation., TestCriteriaRules

### Community 19 - "test_routes.py"
Cohesion: 0.17
Nodes (20): main(), _paths(), Route-seam split tests for the diagnosis module.  Issue: split public routes f, Invariant 4: ``/_meta`` and ``/_csrf`` MUST match before     ``/{code}`` or Fas, The Dashboard discovery route lives in ``dashboard.py`` only —     invariant 10, The audit-log route lives in ``dashboard.py`` only — invariant 10     (seam spl, `MODULE_ID` is part of the discovery contract — Dashboard joins on     it and t, Tests + Insight callers import contract symbols from     ``diagnosis.api`` dire (+12 more)

### Community 21 - "auth.py"
Cohesion: 0.07
Nodes (38): BaseModel, API seam for the diagnosis module — the composed router.  The single ``router`, _AuthUnavailable, _build_session(), _fetch_session(), Exception, Authentication adapter for the diagnosis module.  Delegates trust to the central, FastAPI dependency factory. Returns a dependency that enforces     membership in (+30 more)

### Community 22 - "dashboard.py"
Cohesion: 0.18
Nodes (6): get_criteria(), meta_contract(), DSM-5-TR schizophrenia diagnostic criteria and evaluation engine.  Source: DSM-5, Return the criteria tree, grouped for the UI. Caller must not mutate., Rule contract the browser page consumes for its optimistic display.      The web, diagnosis module — DSM-5-TR schizophrenia criteria checklist for Insight.  Dee

### Community 24 - "Session"
Cohesion: 0.13
Nodes (15): 7.1. `POST /diagnosis/{code}/init`, 7.2. `GET /diagnosis/{code}`, 7.3. `PUT /diagnosis/{code}`, 7. Per-patient diagnosis REST seam, Errors, Errors, Errors, Path parameters (+7 more)

### Community 25 - "test_unittest.py"
Cohesion: 0.28
Nodes (5): Evaluation, Patient, Canonical patient identity as the diagnosis module consumes it.      ``id`` is t, Unittest test suite for the diagnosis module.  Replaces the assert-based smoke, TestSuiteIsolation

## Knowledge Gaps
- **70 isolated node(s):** `fs`, `1. What this module is`, `2. Repo layout`, `Layer A — the seams (api.py + 3 sub-seams, app.py, __init__.py, __main__.py)`, `Layer C — the repository (store.py)` (+65 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_config_selfcheck()` connect `HANDOFF Doc` to `SQLite Persistence Layer`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `DiagnosisStore` connect `test_readiness.py` to `HANDOFF Doc`, `auth.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `TestPersistence` connect `TestPersistence` to `test_unittest.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `main()` (e.g. with `test_app_cors_reads_settings()` and `test_auth_module_sourced_from_settings()`) actually correct?**
  _`main()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `fs`, `1. What this module is`, `2. Repo layout` to the rest of the system?**
  _70 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Diagnosis API Router` be split into smaller, more focused modules?**
  _Cohesion score 0.10416666666666667 - nodes in this community are weakly interconnected._
- **Should `CSRF Test Suite` be split into smaller, more focused modules?**
  _Cohesion score 0.14532019704433496 - nodes in this community are weakly interconnected._