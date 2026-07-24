# Graph Report - /root/projects/insight/Modules/Diagnosis-1.2.0  (2026-07-23)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 603 nodes · 1229 edges · 39 communities (30 shown, 9 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 106 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e90053e8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_readiness.py
- Diagnosis Module — REST API Contract
- DiagnosisStore
- test_csrf.py
- test_auth.py
- test_config.py
- test_embed.py
- config.py
- test_patient.py
- TestPatientIdentity
- TestCSRF
- test_unittest.py
- test_routes.py
- TestCriteriaRules
- Session
- HANDOFF — `diagnosis` module
- TestRestContract
- dashboard.py
- test_discovery.py
- `diagnosis` module
- TestPersistence
- csrf.py
- TestClinicianAuthority
- criteria.py
- TestAuditSeam
- put_session
- auth.py
- UnsupportedDiagnosis
- csrf_token
- CriteriaEvaluation
- build-graph.py
- add-tests.py
- build-graph2.py
- ua-inline-validate.cjs

## God Nodes (most connected - your core abstractions)
1. `TestCriteriaRules` - 27 edges
2. `evaluate()` - 24 edges
3. `TestRestContract` - 24 edges
4. `DiagnosisStore` - 22 edges
5. `check_readiness()` - 20 edges
6. `TestPersistence` - 20 edges
7. `DiagnosisAssertion` - 18 edges
8. `main()` - 18 edges
9. `TestClinicianAuthority` - 18 edges
10. `Session` - 17 edges

## Surprising Connections (you probably didn't know these)
- `TestAuditSeam` --uses--> `UnsupportedDiagnosis`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestAuthRejection` --uses--> `UnsupportedDiagnosis`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestClinicianAuthority` --uses--> `UnsupportedDiagnosis`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestCriteriaRules` --uses--> `UnsupportedDiagnosis`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py
- `TestCSRF` --uses--> `UnsupportedDiagnosis`  [INFERRED]
  test_unittest.py → diagnosis/criteria.py

## Import Cycles
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/__init__.py`
- 3-file cycle: `diagnosis/__init__.py -> diagnosis/readiness.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/__init__.py`
- 4-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/dashboard.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/dashboard.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/dashboard.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/diagnosis_api.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/api.py -> diagnosis/page.py -> diagnosis/deps.py -> diagnosis/__init__.py`
- 5-file cycle: `diagnosis/__init__.py -> diagnosis/app.py -> diagnosis/contract.py -> diagnosis/readiness.py -> diagnosis/deps.py -> diagnosis/__init__.py`

## Communities (39 total, 9 thin omitted)

### Community 0 - "test_readiness.py"
Cohesion: 0.12
Nodes (40): Any, __getattr__(), _check_auth(), _check_clinical_scope(), _check_db(), _check_patient(), check_readiness(), Patient-identity adapter configuration check. The adapter is     opt-in; "disabl (+32 more)

### Community 1 - "Diagnosis Module — REST API Contract"
Cohesion: 0.08
Nodes (38): 10. Configuration (env knobs → `Settings`), 11. Invariants — break these and you've changed the contract, 12. Patient identity (canonical id from "Add New Patient"), 13. Clinician Authority (the safety contract), 14. Source-of-truth tests, 1. Conventions, 2. Route catalogue, 3. Browser page — `GET /` (+30 more)

### Community 2 - "DiagnosisStore"
Cohesion: 0.10
Nodes (25): Cursor, _http_selfcheck(), Run the REST-contract unittest cases under the bypass shim.      The inline ``as, _demo(), Run the rule-suite unittest cases. Exit non-zero on failure.      Run: ``python, main(), Boot the diagnosis module as a standalone web app.      python -m diagnosis, _patient_selfcheck() (+17 more)

### Community 3 - "test_csrf.py"
Cohesion: 0.15
Nodes (28): Test-only hook (mirrors ``auth.reset_auth_for_tests``). Pin a     known secret s, reset_secret_for_tests(), _client(), _free_port(), _Handler, main(), _mint_bad_token(), _mint_valid_token() (+20 more)

### Community 4 - "test_auth.py"
Cohesion: 0.13
Nodes (25): _build_session(), _arm_with_csrf(), _client_for(), _exercise(), _free_port(), _Handler, main(), BaseHTTPRequestHandler (+17 more)

### Community 5 - "test_config.py"
Cohesion: 0.26
Nodes (28): _clear_env(), main(), Settings-adapter tests for the diagnosis module.  Strategy:     - Exercise the `, When ``AUTH_BASE_URL`` is unset, ``auth.AUTH_BASE_URL`` defaults to     the sett, ``dashboard.MODULE_ID`` defaults to the settings-derived id; a     custom ``DIAG, ``app.py`` builds its CORS middleware from ``settings.cors_origins``     (no lon, ``__main__`` builds its ``--host`` / ``--port`` defaults from     ``settings`` (, Re-import ``diagnosis.config`` so ``_load`` re-runs against the     current env. (+20 more)

### Community 6 - "test_embed.py"
Cohesion: 0.12
Nodes (26): main(), Embeddable module UI tests for the diagnosis module.  Issue: replace the standal, The previous shell baked a ``<button ... id="back-btn">Back to     dashboard</bu, The previous shell baked ``<header class="topbar"><h1>Insight</h1>...``     dire, When opts.embedded is true, the fn must NOT render the     ``<header class="dm-t, The host needs to mount AND unmount the module cleanly (a     dashboard that swa, The page seam stamps ``<meta name="csrf-token">`` on serve (the     byte-clean p, The page seam + ``diagnosis.api`` keep ``_read_page`` re-exported     for tests (+18 more)

### Community 7 - "config.py"
Cohesion: 0.10
Nodes (21): Standalone FastAPI app for the diagnosis module.  Usage:     python -m diagnosis, _config_selfcheck(), _env_list(), _env_truthy(), _load(), Settings adapter for the diagnosis module.  Single source of truth for every pre, Stable id this module advertises to Dashboard discovery.          Derived from `, ``/modules/<id>`` href the Dashboard descriptor points at.          Stays aligne (+13 more)

### Community 8 - "test_patient.py"
Cohesion: 0.20
Nodes (21): _arm_with_csrf(), _AuthHandler, _client(), _free_port(), main(), _PatientHandler, BaseHTTPRequestHandler, HTTPServer (+13 more)

### Community 9 - "TestPatientIdentity"
Cohesion: 0.12
Nodes (14): _build_patient(), _fetch_patient(), Patient, _PatientNotFound, _PatientUnavailable, Exception, The registry responded 404 — the code is not a known patient., Normalize the registry payload. Fail closed on missing ``id`` —     a partially (+6 more)

### Community 10 - "TestCSRF"
Cohesion: 0.14
Nodes (4): _fake_request(), Minimal stand-in for ``fastapi.Request`` for dep-level unittests.     ``auth.req, TestAuthRejection, TestCSRF

### Community 11 - "test_unittest.py"
Cohesion: 0.14
Nodes (12): datetime, DiagnosisAssertion, A clinician-authored assertion, independent of computed evidence., require_csrf(), legacy_decision_to_assertion(), Protected diagnosis REST seam — per-patient session state.  This is the only rou, Translate the legacy wire decision into the explicit record state.      ``confir, Patient identity adapter for the diagnosis module.  Aligns the diagnosis module' (+4 more)

### Community 12 - "test_routes.py"
Cohesion: 0.17
Nodes (20): main(), _paths(), Route-seam split tests for the diagnosis module.  Issue: split public routes fro, Invariant 4: ``/_meta`` and ``/_csrf`` MUST match before     ``/{code}`` or Fast, The Dashboard discovery route lives in ``dashboard.py`` only —     invariant 10, The audit-log route lives in ``dashboard.py`` only — invariant 10     (seam spli, `MODULE_ID` is part of the discovery contract — Dashboard joins on     it and th, Tests + Insight callers import contract symbols from     ``diagnosis.api`` direc (+12 more)

### Community 13 - "TestCriteriaRules"
Cohesion: 0.18
Nodes (3): evaluate(), Pure function: given the clinician's checked criteria, return a     CriteriaEval, TestCriteriaRules

### Community 14 - "Session"
Cohesion: 0.16
Nodes (12): API seam for the diagnosis module — the composed router.  The single ``router``, Session, _bypass_dep(), Shared wiring for the diagnosis route seams.  The public router was split into t, get_session(), Return criteria tree and the patient's current evaluation state.      404 if the, diagnosis module — DSM-5-TR schizophrenia criteria checklist for Insight.  Deep, page() (+4 more)

### Community 15 - "HANDOFF — `diagnosis` module"
Cohesion: 0.11
Nodes (17): 10. Gotchas that cost time if you don't know, 11. Glossary, 12. If you only read four files, 1. What this module is, 2. Repo layout, 3. The two layers and how to find things, 4. The web page (`static/index.html`), 5. Run it (+9 more)

### Community 17 - "dashboard.py"
Cohesion: 0.15
Nodes (13): meta_contract(), Return the immutable contract for the module's supported scope., Rule contract the browser page consumes for its optimistic display.      The web, supported_clinical_scope(), audit_log(), meta(), module_routes(), _problem() (+5 more)

### Community 18 - "test_discovery.py"
Cohesion: 0.21
Nodes (14): _client(), _free_port(), _Handler, main(), BaseHTTPRequestHandler, HTTPServer, TestClient, Dashboard discovery-route tests for the diagnosis module.  Mirrors the ``test_au (+6 more)

### Community 19 - "`diagnosis` module"
Cohesion: 0.13
Nodes (13): Architecture (deep module), Configuration (env knobs → `Settings`), CSRF on write routes, Dashboard module-route discovery, `diagnosis` module, Embeddable module UI — `createDiagnosisModule({root, apiBaseUrl})`, Interface (the seam), Module-local readiness (`/ready`) (+5 more)

### Community 21 - "csrf.py"
Cohesion: 0.27
Nodes (10): Request, Signed double-submit CSRF for the diagnosis module's write routes.  PUT /diagnos, FastAPI dependency. Fail closed (403) on any mismatch.      Mirrors ``auth.requi, Attach an HMAC-SHA256 signature to ``raw``. Returns ``raw.sig``., Constant-time check that ``token`` was signed by this secret., _read_cookie(), _read_header(), require_csrf() (+2 more)

### Community 23 - "criteria.py"
Cohesion: 0.25
Nodes (6): AssertionState, DSM-5-TR schizophrenia diagnostic criteria and evaluation engine.  Source: DSM-5, Explicit states for a clinician-authored diagnosis assertion., Enum, str, ValueError

### Community 25 - "put_session"
Cohesion: 0.25
Nodes (8): BaseModel, _dump_for_audit(), JSON snapshot for audit logging. Persisted to the audit table by     ``store.aud, init_session(), put_session(), Request, Persist the clinician's checked criteria and final decision.      Returns the ne, Submission

### Community 26 - "auth.py"
Cohesion: 0.33
Nodes (5): _AuthUnavailable, _fetch_session(), Exception, Canonical Authentication session adapter for Diagnosis., require_role()

### Community 27 - "UnsupportedDiagnosis"
Cohesion: 0.33
Nodes (4): get_criteria(), Return the criteria tree for the one supported diagnosis., Raised when a caller requests a diagnosis outside this module's scope., UnsupportedDiagnosis

### Community 28 - "csrf_token"
Cohesion: 0.29
Nodes (7): mint(), Mint a fresh signed token. Callers set it as the CSRF cookie and     surface it, Stamp the ``csrf`` cookie on ``response``. FastAPI's     ``set_cookie`` is the p, set_cookie(), csrf_token(), Mint a signed double-submit CSRF token. Sets the ``csrf`` cookie     and returns, JSONResponse

## Knowledge Gaps
- **45 isolated node(s):** `1. What this module is`, `2. Repo layout`, `Layer A — the seams (api.py + 3 sub-seams, app.py, __init__.py, __main__.py)`, `Layer C — the repository (store.py)`, `Layer B — the engine (criteria.py)` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_config_selfcheck()` connect `config.py` to `DiagnosisStore`, `test_config.py`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `TestRestContract` connect `TestRestContract` to `TestPatientIdentity`, `test_unittest.py`, `dashboard.py`, `criteria.py`, `UnsupportedDiagnosis`, `CriteriaEvaluation`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `DiagnosisStore` connect `DiagnosisStore` to `test_readiness.py`, `Session`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `TestCriteriaRules` (e.g. with `AssertionState` and `CriteriaEvaluation`) actually correct?**
  _`TestCriteriaRules` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `TestRestContract` (e.g. with `AssertionState` and `CriteriaEvaluation`) actually correct?**
  _`TestRestContract` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `1. What this module is`, `2. Repo layout`, `Layer A — the seams (api.py + 3 sub-seams, app.py, __init__.py, __main__.py)` to the rest of the system?**
  _45 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_readiness.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1184939091915836 - nodes in this community are weakly interconnected._