# Graph Report - .  (2026-07-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 3533 nodes · 7753 edges · 188 communities (164 shown, 24 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 833 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f90336c8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- edit_ledger.py
- Authentication-1.1.0/security.py
- clinical_context.py
- router.py
- DdiMedicationChecker
- AddNewPatientServer
- ddi-engine.js
- AuthTestCase
- required
- PlanEditLedger
- src/app.js
- bn_evaluation.py
- ingest.mjs
- test_readiness.py
- properties
- scope-matrix.v1.json
- BnEvaluationBundle
- test_auth.py
- PlanFinalizer
- bn_manager_backend/main.py
- treatment_plan/app.py
- ClinicalGraphModel
- ProbabilisticRecommendation
- test_tp21_clinical_validation.py
- add_new_patient_backend/main.py
- compile_xmlbif
- PostgreSQLRepository
- diagnosis/__init__.py
- properties
- test_unittest.py
- frontend/package.json
- Observability
- ._cursor
- DashboardServer
- SQLiteRepository
- dashboard.js
- evaluate
- Medical-History-1.0.0/server.js
- test_embed.py
- test_config.py
- test_csrf.py
- Any
- dashboard_backend/main.py
- properties
- PlanContent
- diagnosis/csrf.py
- test_patient.py
- PatientRepository
- enum
- compilerOptions
- properties
- properties
- TestCSRF
- check_tp05_contracts.py
- severity
- review-workspace.ts
- ValidateModelTests
- test_routes.py
- properties
- reduce
- fetch_auth_identity
- properties
- clinical_graph_models/__init__.py
- RuntimeError
- DashboardRepository
- DDI-Checker-1.2.0/package.json
- properties
- ConfigurationError
- ua-finalize.cjs
- MigrationRunner
- required
- required
- $defs
- properties
- schemaVersion
- properties
- properties
- type
- items
- required
- properties
- dashboard_backend/auth.py
- TestRestContract
- TestPersistence
- medicalHistory
- csrf
- errorPolicy
- timeoutPolicy
- required
- Severity-1.1.0/package.json
- auth
- properties
- diagnosis/config.py
- TestClinicianAuthority
- required
- Severity-1.1.0/server.js
- contract.json
- properties
- BnManagerBackendTests
- Medical-History-1.0.0/package.json
- properties
- Add-New-Patient-1.1.0/app.js
- properties
- auth-session.schema.json
- gates
- SharedIdentifierContractTests
- AccessDenied
- sessionCookie
- identifier
- decisionGates
- SQLiteAdapter
- required
- required
- ._client
- SQLiteAdapter
- TestAuditSeam
- test/server.test.js
- DatabaseAdapter
- properties
- roles
- Dashboard-1.2.0/package.json
- storage-adapter.test.mjs
- auth-adapter.test.js
- required
- items
- EditLedgerTests
- public_file_response
- supportedClinicalScope
- id
- user
- src/auth-adapter.js
- enum
- who
- required
- test_auth_adapter.js
- compatibility
- properties
- agent
- ContextOwnershipTests
- auth-contract.schema.json
- schemas
- properties
- security-policy.schema.json
- writeMethods
- enum
- audit-event.schema.json
- scope-matrix.schema.json
- ReleaseGateTests
- capabilities
- schemas
- supportedClinicalScope
- ui-source.test.mjs
- build-graph.py
- audit-provenance.schema.json
- clinical-input-snapshot.schema.json
- final-plan.schema.json
- follow-up-delta.schema.json
- plan-edit.schema.json
- primary-plan.schema.json
- problem-details.schema.json
- recommendation-run.schema.json
- safety-finding.schema.json
- check_context_ownership.py
- check_identifier_contract.py
- check_tp01_release_gate.py
- test_frontend.mjs
- ua-arch-analyze.js
- ua-tour-analyze.js
- recorded
- name
- add_new_patient_backend/__init__.py
- dashboard_backend/__init__.py
- add-tests.py
- build-graph2.py
- ua-inline-validate.cjs
- treatment_plan/__init__.py
- migrations/__init__.py
- policies/__init__.py
- clinical-graph-models

## God Nodes (most connected - your core abstractions)
1. `DdiMedicationChecker` - 69 edges
2. `PlanEditLedger` - 60 edges
3. `PlanFinalizer` - 56 edges
4. `SQLiteRepository` - 53 edges
5. `AddNewPatientServer` - 46 edges
6. `request_json()` - 43 edges
7. `Medication` - 42 edges
8. `InMemoryPlanEditStore` - 40 edges
9. `SQLitePlanEditStore` - 40 edges
10. `ProbabilisticRecommendation` - 39 edges

## Surprising Connections (you probably didn't know these)
- `ScaffoldTests` --uses--> `Settings`  [INFERRED]
  Treatment-Plan/tests/test_tp06_scaffold.py → Add-New-Patient-1.1.0/add_new_patient_backend/config.py
- `SecurityTests` --uses--> `Settings`  [INFERRED]
  Treatment-Plan/tests/test_tp07_security.py → Add-New-Patient-1.1.0/add_new_patient_backend/config.py
- `EditLedgerRouteTests` --uses--> `Settings`  [INFERRED]
  Treatment-Plan/tests/test_tp15_edit_ledger.py → Add-New-Patient-1.1.0/add_new_patient_backend/config.py
- `EditLedgerTests` --uses--> `Settings`  [INFERRED]
  Treatment-Plan/tests/test_tp15_edit_ledger.py → Add-New-Patient-1.1.0/add_new_patient_backend/config.py
- `TP20ObservabilityTests` --uses--> `Settings`  [INFERRED]
  Treatment-Plan/tests/test_tp20_observability.py → Add-New-Patient-1.1.0/add_new_patient_backend/config.py

## Import Cycles
- 3-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/readiness.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 3-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/dashboard.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 3-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 3-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/page.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/app.py -> Diagnosis-1.2.0/diagnosis/readiness.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/app.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/dashboard.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/app.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/app.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/page.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/dashboard.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Diagnosis-1.2.0/diagnosis/dashboard.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/page.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/app.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/dashboard.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/app.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Diagnosis-1.2.0/diagnosis/dashboard.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/app.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/app.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/page.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Diagnosis-1.2.0/diagnosis/__init__.py -> Diagnosis-1.2.0/diagnosis/api.py -> Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Diagnosis-1.2.0/diagnosis/dashboard.py -> Diagnosis-1.2.0/diagnosis/deps.py -> Diagnosis-1.2.0/diagnosis/__init__.py`

## Communities (188 total, 24 thin omitted)

### Community 0 - "edit_ledger.py"
Cohesion: 0.05
Nodes (68): EditLedgerRouteTests, ConcurrentSnapshotProvider, final_plan(), finalized_ledger(), follow_up_delta(), Generator, hash_json(), prior_primary_plan() (+60 more)

### Community 1 - "Authentication-1.1.0/security.py"
Cohesion: 0.06
Nodes (89): _active_admin_count(), active_disclaimer_version(), _canonical_uuid(), cfg(), cfg_bool(), cfg_int(), change_user_password(), _clock_skew_seconds() (+81 more)

### Community 2 - "clinical_context.py"
Cohesion: 0.06
Nodes (45): payloads(), TP08ContractTests, context(), TP09EligibilityPolicyTests, _BnAdapter, _Circuit, ClinicalContext, ClinicalContextAssembler (+37 more)

### Community 3 - "router.py"
Cohesion: 0.07
Nodes (77): contract_payload(), _load_json(), openapi_document(), Path, Authentication discovery artifacts and runtime security metadata., schema(), _schema_path(), contract() (+69 more)

### Community 4 - "DdiMedicationChecker"
Cohesion: 0.08
Nodes (32): primary_plan(), RecordingDdiPort, TP13DdiCheckTests, FailingDdiPort, TP13CheckerFailureTests, no_interaction_response(), TP13MedicationSetBindingTests, TP13HttpAdapterTests (+24 more)

### Community 5 - "AddNewPatientServer"
Cohesion: 0.10
Nodes (18): AddNewPatientBackendTest, AddNewPatientServer, auth_payload(), AuthBoundaryTest, AuthIdentityNormalizationTest, canonical_encounter_payload(), canonical_patient_payload(), ConcurrencyTest (+10 more)

### Community 6 - "ddi-engine.js"
Cohesion: 0.06
Nodes (52): CONFIDENCE, fingerprint(), here, label(), object(), pair(), REQUIRED, runCli() (+44 more)

### Community 7 - "AuthTestCase"
Cohesion: 0.06
Nodes (11): assert_auth_schema(), assert_safe_session(), AuthTestCase, Auth03SecurityTests, AuthDiscoveryTests, AuthUuidContractTests, AuthContractTests, AuthMigrationTests (+3 more)

### Community 8 - "required"
Cohesion: 0.05
Nodes (52): actorId, after, attestation, before, changes, code, codeSystem, content (+44 more)

### Community 9 - "PlanEditLedger"
Cohesion: 0.14
Nodes (25): Settings, BlockingPort, command(), context(), primary_plan(), RecordingPort, TP16FinalizationTests, ConcurrentPort (+17 more)

### Community 10 - "src/app.js"
Cohesion: 0.09
Nodes (45): activateRevision(), addDrugToKb(), addInteraction(), checkNow(), clearStorageFailure(), currentResultsExport(), escapeHtml(), exportAudit() (+37 more)

### Community 11 - "bn_evaluation.py"
Cohesion: 0.09
Nodes (25): FakeEvaluator, TP10BnEvaluationTests, BnEvaluationOrchestrator, BnEvaluationStore, BnEvaluator, BnFinding, BnFindingCode, BnManagerHttpEvaluator (+17 more)

### Community 12 - "ingest.mjs"
Cohesion: 0.09
Nodes (41): addDoseSuggestions(), buildKnowledgeBase(), cleanLine(), compareRelativePaths(), createInteraction(), createRevisionId(), __dirname, drugIdFor() (+33 more)

### Community 13 - "test_readiness.py"
Cohesion: 0.11
Nodes (42): Standalone FastAPI app for the diagnosis module.  Usage:     python -m diagnosis, ready(), _check_auth(), _check_db(), _check_patient(), check_readiness(), Any, Module-local health/readiness probe for the diagnosis module.  Liveness (``/heal (+34 more)

### Community 14 - "properties"
Cohesion: 0.05
Nodes (47): $ref, additionalProperties, properties, type, $ref, $ref, $ref, ClinicalInputSnapshot (+39 more)

### Community 15 - "scope-matrix.v1.json"
Cohesion: 0.04
Nodes (47): approvals, clinicalScope, appointmentPolicy, emergencyBehavior, planBreadth, supportedDiagnoses, supportedPopulation, clinicalValidation (+39 more)

### Community 16 - "BnEvaluationBundle"
Cohesion: 0.18
Nodes (33): BnEvaluationBundle, BnModel, ModelEvaluation, Any, _AppointmentOption, _bundled_policy(), EvidenceKind, EvidenceLink (+25 more)

### Community 17 - "test_auth.py"
Cohesion: 0.08
Nodes (39): _build_session(), _arm_with_csrf(), _client_for(), _exercise(), _free_port(), _Handler, main(), BaseHTTPRequestHandler (+31 more)

### Community 18 - "PlanFinalizer"
Cohesion: 0.13
Nodes (20): DdiCheckResult, PlanView, PreconditionRequired, AuthoritativeContextUnavailable, FinalizationContext, FinalizationContextProvider, FinalizationError, _hash_json() (+12 more)

### Community 19 - "bn_manager_backend/main.py"
Cohesion: 0.10
Nodes (27): assert_csrf_token(), AuthenticationRestAdapter, CsrfError, Any, Exception, Protocol, Request, session_from_payload() (+19 more)

### Community 20 - "treatment_plan/app.py"
Cohesion: 0.12
Nodes (17): ScaffoldTests, create_app(), FastAPI, Settings, Settings, InMemoryRepository, AuthenticationPort, AuthenticationUnavailable (+9 more)

### Community 21 - "ClinicalGraphModel"
Cohesion: 0.15
Nodes (29): _enumerate_chance_assignments(), evaluate_expected_utilities(), evaluate_posterior(), EvaluationResult, _evidence_weight(), ClinicalGraphModel, Node, Potential (+21 more)

### Community 22 - "ProbabilisticRecommendation"
Cohesion: 0.14
Nodes (22): TP11SafetyPolicyTests, bundle(), evaluation(), facts(), TP12PrimaryPlanTests, MappingCoverage, _Definition, EmergencyEscalation (+14 more)

### Community 23 - "test_tp21_clinical_validation.py"
Cohesion: 0.14
Nodes (24): StrEnum, evaluate_payloads(), main(), Any, Fail-closed TP-21 clinical validation and safety-case gate., cases(), hazards(), observations() (+16 more)

### Community 24 - "add_new_patient_backend/main.py"
Cohesion: 0.13
Nodes (30): csrf_error(), generate_csrf_token(), JSONResponse, Request, request_has_valid_csrf(), sign_csrf_token(), verify_csrf_token(), create_canonical_encounter() (+22 more)

### Community 25 - "compile_xmlbif"
Cohesion: 0.15
Nodes (24): get_registry_entry(), list_registry_entries(), ModelRegistryEntry, Path, read_owned_registry_file(), read_registry_model(), read_registry_schema(), resolve_owned_registry_file() (+16 more)

### Community 26 - "PostgreSQLRepository"
Cohesion: 0.13
Nodes (17): Collection, PermissionError, RepositoryContractTests, RetentionPolicyTests, TP19BackupTests, PostgreSQLRepository, Any, datetime (+9 more)

### Community 27 - "diagnosis/__init__.py"
Cohesion: 0.10
Nodes (26): API seam for the diagnosis module — the composed router.  The single ``router``, _AuthUnavailable, _fetch_session(), Exception, Canonical Authentication session adapter for Diagnosis., require_role(), Session, _dump_for_audit() (+18 more)

### Community 28 - "properties"
Cohesion: 0.11
Nodes (19): minLength, pattern, type, $ref, minLength, type, pattern, type (+11 more)

### Community 29 - "test_unittest.py"
Cohesion: 0.10
Nodes (19): _build_patient(), _fetch_patient(), Patient, _PatientNotFound, _PatientUnavailable, Exception, Patient identity adapter for the diagnosis module.  Aligns the diagnosis module', The registry responded 404 — the code is not a known patient. (+11 more)

### Community 30 - "frontend/package.json"
Cohesion: 0.06
Nodes (33): jsdom, react, react-dom, @testing-library/react, @testing-library/user-event, dependencies, react, react-dom (+25 more)

### Community 31 - "Observability"
Cohesion: 0.10
Nodes (15): Logger, LogRecord, TP20ObservabilityTests, configure_logging(), JsonFormatter, Any, _safe_fields(), AuditEvent (+7 more)

### Community 32 - "._cursor"
Cohesion: 0.09
Nodes (21): Cursor, _http_selfcheck(), Run the REST-contract unittest cases under the bypass shim.      The inline ``as, _config_selfcheck(), Self-verify the adapter. Covers:     - every previously hard-coded default surfa, _demo(), Run the rule-suite unittest cases. Exit non-zero on failure.      Run: ``python, main() (+13 more)

### Community 33 - "DashboardServer"
Cohesion: 0.17
Nodes (9): auth_payload(), AuthSessionNormalizationTest, create_session(), DashboardBackendTest, DashboardServer, free_port(), future_iso(), MockAuthenticationServer (+1 more)

### Community 34 - "SQLiteRepository"
Cohesion: 0.10
Nodes (9): TP19MigrationTests, Protocol, Persistence seam used by the application and its tests., Repository, RuntimeRecord, Connection, datetime, Path (+1 more)

### Community 35 - "dashboard.js"
Cohesion: 0.15
Nodes (28): acceptDisclaimer(), activateDevRole(), api, app, buttonMeta(), clearUrl(), escapeHtml(), fmtDate() (+20 more)

### Community 36 - "evaluate"
Cohesion: 0.11
Nodes (11): evaluate(), Evaluation, get_criteria(), meta_contract(), DSM-5-TR schizophrenia diagnostic criteria and evaluation engine.  Source: DSM-5, Pure function: given the clinician's checked criteria, return an     Evaluation., Return the criteria tree, grouped for the UI. Caller must not mutate., Rule contract the browser page consumes for its optimistic display.      The web (+3 more)

### Community 37 - "Medical-History-1.0.0/server.js"
Cohesion: 0.15
Nodes (29): activateMedicalHistory(), ANTIPSYCHOTIC_OPTIONS, CLOZAPINE_CONTRAINDICATION_OPTIONS, COMORBIDITY_OPTIONS, crypto, ensureDataFiles(), ensureJsonFile(), fs (+21 more)

### Community 38 - "test_embed.py"
Cohesion: 0.12
Nodes (28): Read ``static/index.html`` once per request (no build step)., _read_page(), main(), Embeddable module UI tests for the diagnosis module.  Issue: replace the standal, The previous shell baked a ``<button ... id="back-btn">Back to     dashboard</bu, The previous shell baked ``<header class="topbar"><h1>Insight</h1>...``     dire, When opts.embedded is true, the fn must NOT render the     ``<header class="dm-t, The host needs to mount AND unmount the module cleanly (a     dashboard that swa (+20 more)

### Community 39 - "test_config.py"
Cohesion: 0.26
Nodes (28): _clear_env(), main(), Settings-adapter tests for the diagnosis module.  Strategy:     - Exercise the `, When ``AUTH_BASE_URL`` is unset, ``auth.AUTH_BASE_URL`` defaults to     the sett, ``dashboard.MODULE_ID`` defaults to the settings-derived id; a     custom ``DIAG, ``app.py`` builds its CORS middleware from ``settings.cors_origins``     (no lon, ``__main__`` builds its ``--host`` / ``--port`` defaults from     ``settings`` (, Re-import ``diagnosis.config`` so ``_load`` re-runs against the     current env. (+20 more)

### Community 40 - "test_csrf.py"
Cohesion: 0.15
Nodes (26): _client(), _free_port(), _Handler, main(), _mint_bad_token(), _mint_valid_token(), BaseHTTPRequestHandler, HTTPServer (+18 more)

### Community 41 - "Any"
Cohesion: 0.11
Nodes (9): CanonicalEncounterCreate, CanonicalPatientCreate, ClinicalFlag, ClinicalSection, PatientDemographics, PatientIntake, Any, BaseModel (+1 more)

### Community 42 - "dashboard_backend/main.py"
Cohesion: 0.17
Nodes (26): accept_disclaimer(), create_dashboard_session(), dashboard_index(), delete_dashboard_session(), display_name_for(), healthz(), http_exception_handler(), json_error() (+18 more)

### Community 43 - "properties"
Cohesion: 0.10
Nodes (28): domain, dose, frequency, medicationCode, route, sourceResourceId, items, items (+20 more)

### Community 44 - "PlanContent"
Cohesion: 0.07
Nodes (28): emergency, inpatient, intensive-outpatient, interval, nextAppointment, outpatient, pharmacotherapy, setting (+20 more)

### Community 45 - "diagnosis/csrf.py"
Cohesion: 0.10
Nodes (26): mint(), Request, Signed double-submit CSRF for the diagnosis module's write routes.  PUT /diagnos, FastAPI dependency. Fail closed (403) on any mismatch.      Mirrors ``auth.requi, Test-only hook (mirrors ``auth.reset_auth_for_tests``). Pin a     known secret s, Attach an HMAC-SHA256 signature to ``raw``. Returns ``raw.sig``., Constant-time check that ``token`` was signed by this secret., Mint a fresh signed token. Callers set it as the CSRF cookie and     surface it (+18 more)

### Community 46 - "test_patient.py"
Cohesion: 0.20
Nodes (21): _arm_with_csrf(), _AuthHandler, _client(), _free_port(), main(), _PatientHandler, BaseHTTPRequestHandler, HTTPServer (+13 more)

### Community 47 - "PatientRepository"
Cohesion: 0.19
Nodes (11): generate_patient_code(), canonical_suicidality(), compute_age(), _find_patient_id_row(), intake_row(), json_list(), now_iso(), patient_row() (+3 more)

### Community 48 - "enum"
Cohesion: 0.08
Nodes (25): acknowledged, confirmed, editing, evaluating, gathering-inputs, generated, generation-failed, ICD-10-CM (+17 more)

### Community 49 - "compilerOptions"
Cohesion: 0.08
Nodes (24): DOM, DOM.Iterable, ES2022, src, vite/client, vitest/globals, compilerOptions, allowJs (+16 more)

### Community 50 - "properties"
Cohesion: 0.08
Nodes (26): informational_only, null, reject_generation, safety_escalation, string, enum, minLength, type (+18 more)

### Community 51 - "properties"
Cohesion: 0.08
Nodes (24): allergy, contraindication, data-quality, interaction, urgent-risk, enum, type, SafetyFinding (+16 more)

### Community 52 - "TestCSRF"
Cohesion: 0.14
Nodes (4): _fake_request(), Minimal stand-in for ``fastapi.Request`` for dep-level unittests.     ``auth.req, TestAuthRejection, TestCSRF

### Community 53 - "check_tp05_contracts.py"
Cohesion: 0.21
Nodes (14): check_compatibility(), ContractError, lint_openapi(), load(), _pointer(), Path, ValueError, Offline TP-05 JSON Schema, example, compatibility, and OpenAPI conformance. (+6 more)

### Community 54 - "severity"
Cohesion: 0.09
Nodes (22): critical, high, info, instrument, interpretation, low, moderate, score (+14 more)

### Community 55 - "review-workspace.ts"
Cohesion: 0.17
Nodes (18): App(), reviewCase, clonePlan(), compare(), Comparison, createReviewWorkspace(), Dose, fields (+10 more)

### Community 56 - "ValidateModelTests"
Cohesion: 0.37
Nodes (3): _make_node(), _make_potential(), ValidateModelTests

### Community 57 - "test_routes.py"
Cohesion: 0.17
Nodes (20): main(), _paths(), Route-seam split tests for the diagnosis module.  Issue: split public routes fro, Invariant 4: ``/_meta`` and ``/_csrf`` MUST match before     ``/{code}`` or Fast, The Dashboard discovery route lives in ``dashboard.py`` only —     invariant 10, The audit-log route lives in ``dashboard.py`` only — invariant 10     (seam spli, `MODULE_ID` is part of the discovery contract — Dashboard joins on     it and th, Tests + Insight callers import contract symbols from     ``diagnosis.api`` direc (+12 more)

### Community 58 - "properties"
Cohesion: 0.09
Nodes (22): add, remove, replace, $ref, $ref, $ref, enum, type (+14 more)

### Community 59 - "reduce"
Cohesion: 0.22
Nodes (11): main(), Run: python prototype/run_lifecycle.py (synthetic walkthrough only)., initial_state(), ValueError, THROWAWAY TP-04 lifecycle prototype. Not for clinical use or production import., Return a new state for one action; never mutate ``state``., reduce(), _require() (+3 more)

### Community 60 - "fetch_auth_identity"
Cohesion: 0.22
Nodes (14): auth_session_url(), AuthSessionError, _expiry(), fetch_auth_identity(), _fetch_json(), forwarded_auth_headers(), normalize_authenticated_session(), normalize_psychiatrist_session() (+6 more)

### Community 61 - "properties"
Cohesion: 0.10
Nodes (20): additionalProperties, properties, required, type, type, type, const, type (+12 more)

### Community 62 - "clinical_graph_models/__init__.py"
Cohesion: 0.19
Nodes (9): contract_payload(), error_response(), _meta(), ok_response(), Any, RouteContract, TargetNodeContract, XmlBifTarget (+1 more)

### Community 63 - "RuntimeError"
Cohesion: 0.21
Nodes (18): CompletedProcess, RuntimeError, build(), clinical_release_gates(), main(), Path, Cross-platform release image build, SBOM, scan, and human-gated promotion., run() (+10 more)

### Community 64 - "DashboardRepository"
Cohesion: 0.15
Nodes (7): DatabaseAdapter, Protocol, DashboardRepository, now_iso(), Any, DatabaseAdapter, session_row()

### Community 65 - "DDI-Checker-1.2.0/package.json"
Cohesion: 0.10
Nodes (19): description, keywords, license, name, private, scripts, ingest, test (+11 more)

### Community 66 - "properties"
Cohesion: 0.10
Nodes (21): minLength, type, pattern, type, FinalPlan, Version, $ref, $ref (+13 more)

### Community 67 - "ConfigurationError"
Cohesion: 0.18
Nodes (11): TP22DeploymentTests, _bool(), ConfigurationError, ValueError, main(), migration_gate(), Settings, Container startup and migration readiness gate (TP-22). (+3 more)

### Community 68 - "ua-finalize.cjs"
Cohesion: 0.11
Nodes (16): assigned, fileTypes, finalGraph, fs, graph, inter, issues, layers (+8 more)

### Community 69 - "MigrationRunner"
Cohesion: 0.20
Nodes (8): Dialect, Migration, MigrationRunner, _postgres_immutable_trigger(), Any, Path, Dialect-aware, reversible migrations for the repository adapters., Apply or reverse the same ordered migration set on SQLite/PostgreSQL.

### Community 70 - "required"
Cohesion: 0.12
Nodes (19): behavior, case, decision, role, scopeHash, signatureRef, signedAt, items (+11 more)

### Community 71 - "required"
Cohesion: 0.13
Nodes (17): add-new-patient, bn-manager, capturedAt, category, currentMedications, ddi-checker, detectedAt, diagnosis (+9 more)

### Community 72 - "$defs"
Cohesion: 0.12
Nodes (16): $defs, Instant, PlanEdit, ProblemDetails, Uuid, $id, format, type (+8 more)

### Community 73 - "properties"
Cohesion: 0.13
Nodes (15): minItems, type, FollowUpDelta, $ref, additionalProperties, properties, type, $ref (+7 more)

### Community 74 - "schemaVersion"
Cohesion: 0.12
Nodes (17): SourceReference, minLength, type, type, etag, module, resourceId, retrievedAt (+9 more)

### Community 75 - "properties"
Cohesion: 0.12
Nodes (16): const, const, const, const, pattern, type, properties, basePath (+8 more)

### Community 76 - "properties"
Cohesion: 0.12
Nodes (16): type, type, minLength, type, type, type, properties, additionalProperties (+8 more)

### Community 77 - "type"
Cohesion: 0.14
Nodes (15): items, type, uniqueItems, minLength, type, type, items, type (+7 more)

### Community 78 - "items"
Cohesion: 0.13
Nodes (15): items, type, const, additionalProperties, properties, required, path, type (+7 more)

### Community 79 - "required"
Cohesion: 0.13
Nodes (15): schemaVersion, required, auth, basePath, capabilities, compatibility, compatibilityRoutes, dependencies (+7 more)

### Community 80 - "properties"
Cohesion: 0.13
Nodes (15): const, minimum, type, minLength, type, const, httpOnly, maxAgeSeconds (+7 more)

### Community 81 - "dashboard_backend/auth.py"
Cohesion: 0.27
Nodes (12): auth_session_url(), AuthSessionError, fetch_auth_identity(), _fetch_json(), forwarded_auth_headers(), normalize_auth_identity(), _parse_expiry(), Any (+4 more)

### Community 84 - "medicalHistory"
Cohesion: 0.13
Nodes (15): allergies, conditions, items, type, uniqueItems, items, type, uniqueItems (+7 more)

### Community 85 - "csrf"
Cohesion: 0.14
Nodes (14): bootstrapPath, cookieName, failureStatus, headerName, httpOnly, maxAgeSeconds, path, sameSite (+6 more)

### Community 86 - "errorPolicy"
Cohesion: 0.14
Nodes (14): message, status, errorPolicy, csrfFailure, disclosure, loginFailure, readinessFailure, validationFailure (+6 more)

### Community 87 - "timeoutPolicy"
Cohesion: 0.14
Nodes (14): type, caller, readiness, server, timeoutPolicy, type, type, additionalProperties (+6 more)

### Community 88 - "required"
Cohesion: 0.19
Nodes (14): required, name, path, required, bootstrapPath, cookieName, failureStatus, headerName (+6 more)

### Community 89 - "Severity-1.1.0/package.json"
Cohesion: 0.14
Nodes (13): express, author, dependencies, express, description, keywords, license, main (+5 more)

### Community 90 - "auth"
Cohesion: 0.15
Nodes (13): additionalProperties, properties, required, type, auth, required, schemes, const (+5 more)

### Community 91 - "properties"
Cohesion: 0.15
Nodes (13): const, minLength, type, properties, const, minLength, type, bootstrapPath (+5 more)

### Community 92 - "diagnosis/config.py"
Cohesion: 0.19
Nodes (10): _env_list(), _env_truthy(), _load(), Settings adapter for the diagnosis module.  Single source of truth for every pre, Stable id this module advertises to Dashboard discovery.          Derived from `, ``/modules/<id>`` href the Dashboard descriptor points at.          Stays aligne, Read the env once at import time. Pure; never raises on absence —     every fiel, Comma-separated list env var. Empty / unset -> ``default``.      A single ``*`` (+2 more)

### Community 94 - "required"
Cohesion: 0.15
Nodes (13): approvals, clinicalScope, clinicalValidation, clinicalWorkflow, decisionGates, documentId, intendedUse, knowledgeAuthority (+5 more)

### Community 95 - "Severity-1.1.0/server.js"
Cohesion: 0.22
Nodes (9): app, clone(), createApp(), createJsonAssessmentStore(), createMemoryAssessmentStore(), DEFAULT_DATA_DIR, __dirname, __filename (+1 more)

### Community 96 - "contract.json"
Cohesion: 0.17
Nodes (11): basePath, compatibilityRoutes, dependencies, interfaceVersion, moduleId, moduleVersion, schemaVersion, timeoutPolicy (+3 more)

### Community 97 - "properties"
Cohesion: 0.17
Nodes (12): additionalProperties, type, minLength, type, const, properties, csrf, downstreamTrust (+4 more)

### Community 99 - "Medical-History-1.0.0/package.json"
Cohesion: 0.17
Nodes (11): description, engines, node, main, name, private, scripts, dev (+3 more)

### Community 100 - "properties"
Cohesion: 0.17
Nodes (12): pattern, type, format, type, format, type, properties, action (+4 more)

### Community 101 - "Add-New-Patient-1.1.0/app.js"
Cohesion: 0.25
Nodes (9): CLIENT_VALIDATION_MESSAGES, createAddNewPatientModule(), FIELD_INPUT_NAMES, generateBrowserPatientCode(), getRequiredElement(), isValidDob(), normalizePatientInput(), parseListInput() (+1 more)

### Community 102 - "properties"
Cohesion: 0.18
Nodes (11): type, type, properties, type, csrfFailure, disclosure, loginFailure, readinessFailure (+3 more)

### Community 103 - "auth-session.schema.json"
Cohesion: 0.18
Nodes (10): additionalProperties, $id, schemaVersion, required, $schema, type, authenticated, gates (+2 more)

### Community 104 - "gates"
Cohesion: 0.18
Nodes (11): type, additionalProperties, properties, required, type, type, disclaimerAccepted, gates (+3 more)

### Community 107 - "sessionCookie"
Cohesion: 0.20
Nodes (10): securityPolicy, downstreamTrust, jwks, sessionCookie, httpOnly, maxAgeSeconds, name, path (+2 more)

### Community 108 - "identifier"
Cohesion: 0.20
Nodes (10): value, additionalProperties, properties, required, type, identifier, what, additionalProperties (+2 more)

### Community 109 - "decisionGates"
Cohesion: 0.20
Nodes (10): type, clinicalValidation, maxItems, minItems, owners, regulatoryAssessment, type, type (+2 more)

### Community 110 - "SQLiteAdapter"
Cohesion: 0.36
Nodes (4): migrate_patients_to_identity_table(), now_iso(), Connection, SQLiteAdapter

### Community 111 - "required"
Cohesion: 0.22
Nodes (9): auth, required, schemes, required, csrf, csrf-double-submit, downstreamTrust, jwks (+1 more)

### Community 112 - "required"
Cohesion: 0.22
Nodes (9): additionalProperties, required, type, errorPolicy, csrfFailure, disclosure, loginFailure, readinessFailure (+1 more)

### Community 114 - "SQLiteAdapter"
Cohesion: 0.28
Nodes (3): Connection, SQLite adapter. Repository owns SQL, so Postgres can replace adapter later., SQLiteAdapter

### Community 116 - "test/server.test.js"
Cohesion: 0.22
Nodes (6): assert, fs, os, path, { spawn }, test

### Community 117 - "DatabaseAdapter"
Cohesion: 0.25
Nodes (5): DatabaseAdapter, Any, Protocol, IdempotencyConflict, Exception

### Community 118 - "properties"
Cohesion: 0.25
Nodes (8): minLength, type, displayName, username, properties, maxLength, minLength, type

### Community 119 - "roles"
Cohesion: 0.25
Nodes (8): enum, psychiatrist, roles, items, minItems, type, uniqueItems, admin

### Community 120 - "Dashboard-1.2.0/package.json"
Cohesion: 0.25
Nodes (7): name, private, scripts, start, test, type, version

### Community 121 - "storage-adapter.test.mjs"
Cohesion: 0.32
Nodes (4): browserStorageAdapter(), memoryStorageAdapter(), { browserStorageAdapter, memoryStorageAdapter }, require

### Community 122 - "auth-adapter.test.js"
Cohesion: 0.32
Nodes (5): createMemoryAuthAdapter(), parseCanonicalSession(), assert, canonical, { createMemoryAuthAdapter, parseCanonicalSession }

### Community 123 - "required"
Cohesion: 0.48
Nodes (7): clinicalSafetyOfficer, privacy, product, regulatory, psychiatrist, required, enum

### Community 124 - "items"
Cohesion: 0.25
Nodes (8): what, items, type, additionalProperties, properties, required, type, entity

### Community 125 - "EditLedgerTests"
Cohesion: 0.50
Nodes (3): EditLedgerTests, ledger(), primary_plan()

### Community 126 - "public_file_response"
Cohesion: 0.52
Nodes (7): embedded_module_shell(), public_file_response(), FileResponse, HTTPException, root(), serve_embedded_asset(), serve_static()

### Community 127 - "supportedClinicalScope"
Cohesion: 0.29
Nodes (7): supportedClinicalScope, additionalProperties, required, type, declaration, populations, workflows

### Community 128 - "id"
Cohesion: 0.29
Nodes (7): format, type, minLength, type, expiresAt, id, properties

### Community 129 - "user"
Cohesion: 0.20
Nodes (10): id, user, required, additionalProperties, required, type, displayName, expiresAt (+2 more)

### Community 131 - "enum"
Cohesion: 0.29
Nodes (7): approved, draft_pending_approval, rejected, superseded, unresolved, withdrawn, enum

### Community 132 - "who"
Cohesion: 0.29
Nodes (7): identifier, who, required, additionalProperties, properties, required, type

### Community 133 - "required"
Cohesion: 0.29
Nodes (7): outcome, recorded, resourceType, action, correlationId, id, required

### Community 134 - "test_auth_adapter.js"
Cohesion: 0.38
Nodes (4): createMemoryAuthAdapter(), parseCanonicalSession(), canonical, memory

### Community 135 - "compatibility"
Cohesion: 0.33
Nodes (6): compatibility, jwksPolicy, jwtPolicy, legacySession, legacySessionPolicy, sessionAuthority

### Community 136 - "properties"
Cohesion: 0.12
Nodes (17): minLength, type, additionalProperties, properties, type, AuditProvenance, minLength, type (+9 more)

### Community 137 - "agent"
Cohesion: 0.33
Nodes (6): who, additionalProperties, properties, required, type, agent

### Community 139 - "auth-contract.schema.json"
Cohesion: 0.40
Nodes (4): additionalProperties, $id, $schema, type

### Community 140 - "schemas"
Cohesion: 0.40
Nodes (5): pattern, schemas, items, type, uniqueItems

### Community 141 - "properties"
Cohesion: 0.25
Nodes (8): const, properties, authenticated, schemaVersion, session, const, additionalProperties, type

### Community 142 - "security-policy.schema.json"
Cohesion: 0.40
Nodes (4): additionalProperties, $id, $schema, type

### Community 143 - "writeMethods"
Cohesion: 0.40
Nodes (5): PATCH, POST, writeMethods, const, type

### Community 144 - "enum"
Cohesion: 0.40
Nodes (5): denied, failure, success, enum, outcome

### Community 145 - "audit-event.schema.json"
Cohesion: 0.40
Nodes (4): additionalProperties, $id, $schema, type

### Community 146 - "scope-matrix.schema.json"
Cohesion: 0.40
Nodes (4): $id, $schema, title, type

### Community 148 - "capabilities"
Cohesion: 0.50
Nodes (4): capabilities, account.manage, csrf.bootstrap, session.verify

### Community 149 - "schemas"
Cohesion: 0.50
Nodes (4): schemas, auth-contract, auth-session, securityPolicy

### Community 150 - "supportedClinicalScope"
Cohesion: 0.50
Nodes (4): supportedClinicalScope, declaration, populations, workflows

### Community 152 - "ui-source.test.mjs"
Cohesion: 0.50
Nodes (3): __dirname, __filename, projectRoot

### Community 154 - "audit-provenance.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 155 - "clinical-input-snapshot.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 156 - "final-plan.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 157 - "follow-up-delta.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 158 - "plan-edit.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 159 - "primary-plan.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 160 - "problem-details.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 161 - "recommendation-run.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 162 - "safety-finding.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 163 - "check_context_ownership.py"
Cohesion: 0.67
Nodes (3): evaluate(), main(), Validate unique ownership and REST-only cross-module relationship rules.

### Community 164 - "check_identifier_contract.py"
Cohesion: 0.67
Nodes (3): evaluate(), main(), Validate the shared TP-03 identifier and transport contract.

### Community 165 - "check_tp01_release_gate.py"
Cohesion: 0.67
Nodes (3): evaluate(), main(), Fail-closed TP-01 clinical release gate. Uses only the Python standard library.

### Community 169 - "recorded"
Cohesion: 0.67
Nodes (3): recorded, format, type

### Community 170 - "name"
Cohesion: 0.67
Nodes (3): minLength, type, name

## Knowledge Gaps
- **786 isolated node(s):** `CLIENT_VALIDATION_MESSAGES`, `FIELD_INPUT_NAMES`, `here`, `html`, `moduleId` (+781 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DiagnosisStore` connect `test_readiness.py` to `._cursor`, `diagnosis/__init__.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `SQLiteRepository` connect `SQLiteRepository` to `edit_ledger.py`, `ConfigurationError`, `MigrationRunner`, `PlanEditLedger`, `treatment_plan/app.py`, `PostgreSQLRepository`, `EditLedgerTests`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `AccessDenied` connect `AccessDenied` to `treatment_plan/app.py`, `Observability`, `RuntimeError`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `DdiMedicationChecker` (e.g. with `RecordingDdiPort` and `TP13DdiCheckTests`) actually correct?**
  _`DdiMedicationChecker` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `PlanEditLedger` (e.g. with `EditLedgerRouteTests` and `EditLedgerTests`) actually correct?**
  _`PlanEditLedger` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `PlanFinalizer` (e.g. with `BlockingPort` and `RecordingPort`) actually correct?**
  _`PlanFinalizer` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `SQLiteRepository` (e.g. with `ScaffoldTests` and `EditLedgerRouteTests`) actually correct?**
  _`SQLiteRepository` has 22 INFERRED edges - model-reasoned connections that need verification._