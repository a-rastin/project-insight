"""Add missing test file nodes and edges to batch-5.json."""
import json

OUT = "E:\\diagnosis\\.understand-anything\\intermediate"

with open(f"{OUT}\\batch-5.json") as f:
    b5 = json.load(f)

extra_nodes = [
    {"id": "file:test_unittest.py", "type": "file", "name": "test_unittest.py",
     "filePath": "test_unittest.py", "language": "python", "complexity": "moderate",
     "summary": "Unittest suite locking clinical contracts: TestCriteriaRules (pure rule engine), TestRestContract (route/persistence contract), TestAuditSeam (audit hook on every PUT), TestClinicianAuthority (model-never-auto-decides invariant), TestAuthRejection, TestCSRF, TestPersistence, TestPatientIdentity. Loaded by _http_selfcheck and _demo at boot time.",
     "tags": ["unittest","clinical-contracts","criteria-rules","audit","authority-invariant"], "fileCategory": "code", "languageNotes": ""},
    {"id": "file:test_auth.py", "type": "file", "name": "test_auth.py",
     "filePath": "test_auth.py", "language": "python", "complexity": "simple",
     "summary": "Role-enforcement tests. In-process fake HTTP server exercising all protected paths with no-cookie, unauthenticated, nurse-role, psychiatrist-role, and admin-role requests. No external framework — stdlib unittest plus threading HTTP server.",
     "tags": ["auth-tests","role-enforcement","fake-http-server","ponytail-harness"], "fileCategory": "code", "languageNotes": ""},
    {"id": "file:test_config.py", "type": "file", "name": "test_config.py",
     "filePath": "test_config.py", "language": "python", "complexity": "simple",
     "summary": "Settings adapter tests: blank env returns prior defaults, custom env is honoured, Settings is frozen, module_id derives from mount prefix, CORS parses comma list, mock_auth and patient_lookup are truthy gates, host/port override.",
     "tags": ["config-tests","settings-adapter","env-snapshot"], "fileCategory": "code", "languageNotes": ""},
    {"id": "file:test_embed.py", "type": "file", "name": "test_embed.py",
     "filePath": "test_embed.py", "language": "python", "complexity": "simple",
     "summary": "Embeddable module UI tests: page is standalone shell, exposes createDiagnosisModule, contract takes root+apiBaseUrl, drops dashboard placeholder, no standalone topbar, embedded flag skips chrome, mount/unmount handle, CSRF meta tag still read, route layer unchanged, bypass serve byte-clean.",
     "tags": ["embed-tests","ui-contract","createDiagnosisModule"], "fileCategory": "code", "languageNotes": ""},
    {"id": "file:test_routes.py", "type": "file", "name": "test_routes.py",
     "filePath": "test_routes.py", "language": "python", "complexity": "simple",
     "summary": "Route-seam split tests: page seam owns only browser page, dashboard seam owns only discovery routes, diagnosis seam owns only per-patient REST, composed router has all paths, literal routes precede parameterized, audit seam is in dashboard only, discovery moduleId constant, back-compat re-exports, each seam shares one store and policy.",
     "tags": ["route-tests","seam-split","route-invariants"], "fileCategory": "code", "languageNotes": ""},
]

extra_edges = [
    # test_unittest -> diagnosis modules
    {"source": "file:test_unittest.py", "target": "file:diagnosis/criteria.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_unittest.py", "target": "file:diagnosis/api.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_unittest.py", "target": "file:diagnosis/store.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_unittest.py", "target": "file:diagnosis/patient.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_unittest.py", "target": "file:diagnosis/readiness.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_unittest.py", "target": "file:diagnosis/config.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_unittest.py", "target": "file:diagnosis/auth.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_unittest.py", "target": "file:diagnosis/csrf.py", "type": "imports", "weight": 0.7},
    # test_auth -> diagnosis modules
    {"source": "file:test_auth.py", "target": "file:diagnosis/api.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_auth.py", "target": "file:diagnosis/auth.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_auth.py", "target": "file:diagnosis/deps.py", "type": "imports", "weight": 0.7},
    # test_config -> diagnosis modules
    {"source": "file:test_config.py", "target": "file:diagnosis/config.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_config.py", "target": "file:diagnosis/app.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_config.py", "target": "file:diagnosis/__main__.py", "type": "imports", "weight": 0.7},
    # test_embed -> diagnosis modules
    {"source": "file:test_embed.py", "target": "file:diagnosis/api.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_embed.py", "target": "file:diagnosis/page.py", "type": "imports", "weight": 0.7},
    # test_routes -> diagnosis modules
    {"source": "file:test_routes.py", "target": "file:diagnosis/api.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_routes.py", "target": "file:diagnosis/page.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_routes.py", "target": "file:diagnosis/dashboard.py", "type": "imports", "weight": 0.7},
    {"source": "file:test_routes.py", "target": "file:diagnosis/diagnosis_api.py", "type": "imports", "weight": 0.7},
]

b5["nodes"].extend(extra_nodes)
b5["edges"].extend(extra_edges)
b5["files"].extend([
    {"path": "test_unittest.py", "language": "python", "sizeLines": 1075, "fileCategory": "code"},
    {"path": "test_auth.py",     "language": "python", "sizeLines": 322,  "fileCategory": "code"},
    {"path": "test_config.py",   "language": "python", "sizeLines": 439,  "fileCategory": "code"},
    {"path": "test_embed.py",    "language": "python", "sizeLines": 325,  "fileCategory": "code"},
    {"path": "test_routes.py",   "language": "python", "sizeLines": 250,  "fileCategory": "code"},
])

with open(f"{OUT}\\batch-5.json", "w") as f:
    json.dump(b5, f, indent=2)

print(f"Updated batch-5.json: {len(b5['nodes'])} nodes, {len(b5['edges'])} edges")