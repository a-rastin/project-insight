# Graph Report - /root/projects/insight  (2026-07-23)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 4621 nodes · 9229 edges · 265 communities (233 shown, 32 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 920 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `edbe0026`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BnEvaluationBundle
- Authentication-1.1.0/security.py
- clinical_context.py
- AddNewPatientServer
- router.py
- test_patient.py
- test_unittest.py
- treatment_plan/app.py
- AuthTestCase
- Diagnosis Module — REST API Contract
- bn_manager_backend/main.py
- src/app.js
- finalization.py
- edit_ledger.py
- FilesystemContractAdapter
- PlanEditLedger
- scope-matrix.v1.json
- check_architecture
- properties
- DdiMedicationChecker
- TestRestContract
- schemaVersion
- Add New Patient Module Handoff
- INSIGHT Authentication Module Handoff
- DashboardServer
- test_tp21_clinical_validation.py
- PatientRepository
- properties
- required
- add_new_patient_backend/main.py
- frontend/package.json
- properties
- properties
- properties
- ClinicalGraphModel
- test_readiness.py
- InMemoryPlanEditStore
- contracts/schemas/1.0.0/auth-session.schema.json
- identifiers.schema.json
- DashboardRepository
- dashboard_backend/main.py
- test_csrf.py
- dashboard.js
- Medical-History-1.0.0/server.js
- ProbabilisticRecommendation
- Any
- test_auth.py
- TestPatientIdentity
- test_config.py
- check_readiness
- properties
- PlanContent
- PrimaryTreatmentPlan
- compile_xmlbif
- HANDOFF — `severity` module
- properties
- SupersessionError
- ingest.mjs
- diagnosis/config.py
- ddi-engine.js
- TestCriteriaRules
- compilerOptions
- properties
- INSIGHT Authentication v1 Contract
- TestCSRF
- INSIGHT Treatment Plan
- properties
- check_tp05_contracts.py
- provenance.schema.json
- store.py
- severity
- review-workspace.ts
- ConfigurationError
- SQLiteRepository
- pagination.schema.json
- SQLiteAdapter
- ValidateModelTests
- diagnosis/csrf.py
- test_routes.py
- properties
- reduce
- properties
- fetch_auth_identity
- Add New Patient API Contract
- clinical_graph_models/__init__.py
- DDI-Checker-1.2.0/package.json
- sqlite_repository.py
- HttpContractAdapter
- MigrationRunner
- Dashboard — Module Handoff
- ua-finalize.cjs
- $defs
- enum
- required
- module-contract.json
- required
- resource-version.schema.json
- validate-kb.mjs
- HANDOFF — `diagnosis` module
- public/app.js
- request-metadata.schema.json
- report-parser.js
- required
- properties
- SQLitePlanEditStore
- properties
- type
- dashboard_backend/auth.py
- manifest.json
- items
- required
- properties
- TestPersistence
- Severity Module
- medicalHistory
- required
- .dashboard
- auth
- properties
- properties
- Severity-1.1.0/package.json
- Repository Handoff — Add New Patient Module
- csrf
- errorPolicy
- timeoutPolicy
- required
- Add-New-Patient-1.1.0/DESIGN.md
- properties
- Authentication-1.1.0/DESIGN.md
- TestClinicianAuthority
- Severity-1.1.0/server.js
- code
- required
- contract.json
- auth
- properties
- INSIGHT Authentication module
- BnManagerBackendTests
- Medical-History-1.0.0/package.json
- properties
- EditLedgerTests
- PostgreSQLRepository
- Add-New-Patient-1.1.0/app.js
- properties
- properties
- Authentication-1.1.0/contracts/schemas/1.0.0/auth-session.schema.json
- gates
- BN Manager
- Dashboard API Contract: INSIGHT Workspace
- Drug-Drug Interaction Checker
- SharedIdentifierContractTests
- package_release.py
- add_new_patient_backend/csrf.py
- sessionCookie
- ModuleRegistration
- DDI-Checker 1.1.0 — Architecture & Data Flow
- identifier
- decisionGates
- TP-01 — Intended use, clinical scope, and release gates
- INSIGHT Treatment Plan Handoff
- RuntimeError
- evaluation.py
- required
- required
- security-policy.schema.json
- ._client
- Dashboard Module
- test/server.test.js
- CommonContractsClient
- properties
- roles
- get_settings
- Dashboard Dataset Schema
- Dashboard-1.2.0/package.json
- storage-adapter.test.mjs
- auth-adapter.test.js
- items
- required
- SecurityTests
- Repository
- supportedClinicalScope
- Patient Domain Glossary
- Add New Patient Module
- supportedClinicalScope
- id
- user
- src/auth-adapter.js
- Medical History Module
- test_auth_adapter.js
- INSIGHT canonical identifiers, encounters, and transport interface v1
- required
- who
- CommonContractsClient
- compatibility
- session
- MEDICAL_HISTORY_HANDOFF.md
- agent
- ADR TP-04 - Disposable lifecycle prototype
- ContextOwnershipTests
- capabilities
- auth
- auth-contract.schema.json
- schemas
- properties
- writeMethods
- report-parser-parity.test.mjs
- Treatment-Plan/contracts/schemas/1.0.0/audit-event.schema.json
- enum
- scope-matrix.schema.json
- ReleaseGateTests
- RepositoryContractTests
- .format
- schemas
- supportedClinicalScope
- timeoutPolicy
- XML Bayesian Network Migration
- ddi-engine.test.mjs
- ui-source.test.mjs
- build-graph.py
- audit-provenance.schema.json
- clinical-input-snapshot.schema.json
- final-plan.schema.json
- follow-up-delta.schema.json
- plan-edit.schema.json
- primary-plan.schema.json
- Treatment-Plan/contracts/schemas/1.0.0/problem-details.schema.json
- recommendation-run.schema.json
- safety-finding.schema.json
- type
- check_context_ownership.py
- check_identifier_contract.py
- check_tp01_release_gate.py
- path
- replacement
- test_frontend.mjs
- ua-arch-analyze.js
- ua-tour-analyze.js
- correlationId
- python/__init__.py
- contracts/README.md
- add_new_patient_backend/__init__.py
- CONTEXT.md
- UBIQUITOUS_LANGUAGE.md
- dashboard_backend/__init__.py
- add-tests.py
- build-graph2.py
- ua-inline-validate.cjs
- SCHEMA-VERSIONING.md
- ROLLBACK.md
- TP-10-BN-MAPPING-COVERAGE.md
- treatment_plan/__init__.py
- migrations/__init__.py
- policies/__init__.py
- README.md
- clinical-graph-models

## God Nodes (most connected - your core abstractions)
1. `DdiMedicationChecker` - 69 edges
2. `PlanEditLedger` - 60 edges
3. `AddNewPatientServer` - 58 edges
4. `PlanFinalizer` - 56 edges
5. `request_json()` - 53 edges
6. `SQLiteRepository` - 53 edges
7. `Medication` - 42 edges
8. `AddNewPatientBackendTest` - 41 edges
9. `InMemoryPlanEditStore` - 40 edges
10. `SQLitePlanEditStore` - 40 edges

## Surprising Connections (you probably didn't know these)
- `contract_registry()` --calls--> `FilesystemContractAdapter`  [EXTRACTED]
  Modules/Diagnosis-1.2.0/diagnosis/contract.py → contracts/adapters/python/filesystem.py
- `install_common_routes()` --calls--> `install_common_routes()`  [EXTRACTED]
  Modules/Diagnosis-1.2.0/diagnosis/contract.py → contracts/adapters/python/fastapi.py
- `CommonContractTests` --uses--> `FilesystemContractAdapter`  [INFERRED]
  tests/test_common_contracts.py → contracts/adapters/python/filesystem.py
- `CommonContractTests` --uses--> `InMemoryContractAdapter`  [INFERRED]
  tests/test_common_contracts.py → contracts/adapters/python/memory.py
- `ArchitectureCheckerTests` --uses--> `FilesystemSourceAdapter`  [INFERRED]
  tests/test_architecture.py → scripts/check_architecture.py

## Import Cycles
- 3-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/dashboard.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 3-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 3-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/page.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 3-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/readiness.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/app.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/dashboard.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/dashboard.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/app.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Modules/Diagnosis-1.2.0/diagnosis/dashboard.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/app.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/page.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 4-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/page.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/app.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/dashboard.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/app.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Modules/Diagnosis-1.2.0/diagnosis/dashboard.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Modules/Diagnosis-1.2.0/diagnosis/dashboard.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/app.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/diagnosis_api.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/app.py -> Modules/Diagnosis-1.2.0/diagnosis/api.py -> Modules/Diagnosis-1.2.0/diagnosis/page.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`
- 5-file cycle: `Modules/Diagnosis-1.2.0/diagnosis/__init__.py -> Modules/Diagnosis-1.2.0/diagnosis/app.py -> Modules/Diagnosis-1.2.0/diagnosis/contract.py -> Modules/Diagnosis-1.2.0/diagnosis/readiness.py -> Modules/Diagnosis-1.2.0/diagnosis/deps.py -> Modules/Diagnosis-1.2.0/diagnosis/__init__.py`

## Communities (265 total, 32 thin omitted)

### Community 0 - "BnEvaluationBundle"
Cohesion: 0.06
Nodes (60): FakeEvaluator, TP10BnEvaluationTests, bundle(), evaluation(), facts(), TP12PrimaryPlanTests, BnEvaluationBundle, BnEvaluationOrchestrator (+52 more)

### Community 1 - "Authentication-1.1.0/security.py"
Cohesion: 0.06
Nodes (89): _active_admin_count(), active_disclaimer_version(), _canonical_uuid(), cfg(), cfg_bool(), cfg_int(), change_user_password(), _clock_skew_seconds() (+81 more)

### Community 2 - "clinical_context.py"
Cohesion: 0.06
Nodes (44): payloads(), TP08ContractTests, context(), TP09EligibilityPolicyTests, _BnAdapter, _Circuit, ClinicalContext, ClinicalContextAssembler (+36 more)

### Community 3 - "AddNewPatientServer"
Cohesion: 0.09
Nodes (19): AddNewPatientBackendTest, AddNewPatientServer, auth_payload(), AuthBoundaryTest, AuthIdentityNormalizationTest, canonical_encounter_payload(), canonical_patient_payload(), ConcurrencyTest (+11 more)

### Community 4 - "router.py"
Cohesion: 0.07
Nodes (77): contract_payload(), _load_json(), openapi_document(), Path, Authentication discovery artifacts and runtime security metadata., schema(), _schema_path(), contract() (+69 more)

### Community 5 - "test_patient.py"
Cohesion: 0.06
Nodes (63): Read ``static/index.html`` once per request (no build step)., _read_page(), _client(), _free_port(), _Handler, main(), BaseHTTPRequestHandler, HTTPServer (+55 more)

### Community 6 - "test_unittest.py"
Cohesion: 0.06
Nodes (47): API seam for the diagnosis module — the composed router.  The single ``router``, _AuthUnavailable, _fetch_session(), Exception, Canonical Authentication session adapter for Diagnosis., require_role(), Session, get_criteria() (+39 more)

### Community 7 - "treatment_plan/app.py"
Cohesion: 0.10
Nodes (26): Logger, ScaffoldTests, TP20ObservabilityTests, create_app(), FastAPI, Settings, Settings, configure_logging() (+18 more)

### Community 8 - "AuthTestCase"
Cohesion: 0.06
Nodes (11): assert_auth_schema(), assert_safe_session(), AuthTestCase, Auth03SecurityTests, AuthDiscoveryTests, AuthUuidContractTests, AuthContractTests, AuthMigrationTests (+3 more)

### Community 9 - "Diagnosis Module — REST API Contract"
Cohesion: 0.05
Nodes (51): 10. Configuration (env knobs → `Settings`), 11. Invariants — break these and you've changed the contract, 12. Patient identity (canonical id from "Add New Patient"), 13. Clinician Authority (the safety contract), 14. Source-of-truth tests, 1. Conventions, 2. Route catalogue, 3. Browser page — `GET /` (+43 more)

### Community 10 - "bn_manager_backend/main.py"
Cohesion: 0.09
Nodes (34): _problem(), Request, Reusable FastAPI transport adapter for the common module routes., assert_csrf_token(), AuthenticationRestAdapter, CsrfError, Any, Exception (+26 more)

### Community 11 - "src/app.js"
Cohesion: 0.09
Nodes (45): activateRevision(), addDrugToKb(), addInteraction(), checkNow(), clearStorageFailure(), currentResultsExport(), escapeHtml(), exportAudit() (+37 more)

### Community 12 - "finalization.py"
Cohesion: 0.13
Nodes (27): DdiCheckResult, PlanFinalized, PlanView, PreconditionFailed, PreconditionRequired, AuthoritativeContextUnavailable, FinalizationContext, FinalizationContextProvider (+19 more)

### Community 13 - "edit_ledger.py"
Cohesion: 0.11
Nodes (25): _apply_pointer(), _canonical_json(), _editable_tokens(), EditCategory, EditLedgerError, _encode_token(), _etag(), _finding_for_pointer() (+17 more)

### Community 14 - "FilesystemContractAdapter"
Cohesion: 0.08
Nodes (26): install_common_routes(), Mount common routes on an app; module handlers remain outside this adapter., install_common_routes(), FastAPI common route installer with built-in OpenAPI route disabled., FilesystemContractAdapter, Path, Production adapter that reads immutable contract artifacts from disk., Load common contract documents without importing module/domain code. (+18 more)

### Community 15 - "PlanEditLedger"
Cohesion: 0.14
Nodes (20): Settings, BlockingPort, command(), context(), primary_plan(), RecordingPort, TP16FinalizationTests, ConcurrentPort (+12 more)

### Community 16 - "scope-matrix.v1.json"
Cohesion: 0.04
Nodes (47): approvals, clinicalScope, appointmentPolicy, emergencyBehavior, planBreadth, supportedDiagnoses, supportedPopulation, clinicalValidation (+39 more)

### Community 17 - "check_architecture"
Cohesion: 0.10
Nodes (27): ArchitectureViolation, _canonical_path(), check_architecture(), _common_import_allowed(), _config_violations(), FilesystemSourceAdapter, InMemorySourceAdapter, _module_for_path() (+19 more)

### Community 18 - "properties"
Cohesion: 0.04
Nodes (44): additionalProperties, items, type, pattern, type, $ref, minLength, type (+36 more)

### Community 19 - "DdiMedicationChecker"
Cohesion: 0.13
Nodes (21): primary_plan(), RecordingDdiPort, TP13DdiCheckTests, FailingDdiPort, TP13CheckerFailureTests, no_interaction_response(), TP13MedicationSetBindingTests, TP13HttpAdapterTests (+13 more)

### Community 20 - "TestRestContract"
Cohesion: 0.05
Nodes (12): AssertionState, DiagnosisAssertion, Enum, str, ValueError, A clinician-authored assertion, independent of computed evidence., Explicit states for a clinician-authored diagnosis assertion., One TestClient for the class so the bypass-shimmed store is reset     between te (+4 more)

### Community 21 - "schemaVersion"
Cohesion: 0.13
Nodes (15): minItems, type, $ref, properties, $ref, $ref, changes, deltaId (+7 more)

### Community 22 - "Add New Patient Module Handoff"
Cohesion: 0.05
Nodes (38): `add_new_patient_backend/auth.py`, `add_new_patient_backend/config.py`, `add_new_patient_backend/db.py`, `add_new_patient_backend/models.py`, `add_new_patient_backend/repository.py`, Add New Patient Module Handoff, Adding a Patient Field, Adding Auth (+30 more)

### Community 23 - "INSIGHT Authentication Module Handoff"
Cohesion: 0.05
Nodes (38): Add a New Protected Auth Route, Add a Pending-Disclaimer Route, Add Audit Logging, Admin account management, `audit_log`, Browser UI Flow, Common Change Recipes, Configuration (+30 more)

### Community 24 - "DashboardServer"
Cohesion: 0.16
Nodes (10): auth_payload(), create_session(), DashboardBackendTest, DashboardServer, free_port(), future_iso(), MockAuthenticationServer, MockModuleServer (+2 more)

### Community 25 - "test_tp21_clinical_validation.py"
Cohesion: 0.14
Nodes (24): evaluate_payloads(), main(), Any, Fail-closed TP-21 clinical validation and safety-case gate., cases(), hazards(), observations(), protocol() (+16 more)

### Community 26 - "PatientRepository"
Cohesion: 0.13
Nodes (19): DatabaseAdapter, Protocol, canonical_suicidality(), compute_age(), _find_patient_id_row(), IdempotencyConflict, intake_row(), json_list() (+11 more)

### Community 27 - "properties"
Cohesion: 0.05
Nodes (36): $ref, $ref, additionalProperties, $ref, $ref, $id, $ref, action (+28 more)

### Community 28 - "required"
Cohesion: 0.07
Nodes (37): required, required, path, schemaVersion, version, required, required, required (+29 more)

### Community 29 - "add_new_patient_backend/main.py"
Cohesion: 0.15
Nodes (31): canonical_response(), create_canonical_encounter(), create_canonical_patient(), create_patient(), csrf_middleware(), embedded_module_shell(), ensure_patient_code(), get_canonical_encounter() (+23 more)

### Community 30 - "frontend/package.json"
Cohesion: 0.06
Nodes (33): jsdom, dependencies, react, react-dom, typescript, vite, @vitejs/plugin-react, vitest (+25 more)

### Community 31 - "properties"
Cohesion: 0.06
Nodes (35): minLength, type, additionalProperties, properties, type, $ref, AuditProvenance, ProblemDetails (+27 more)

### Community 32 - "properties"
Cohesion: 0.04
Nodes (62): minLength, type, $ref, additionalProperties, properties, type, $ref, $ref (+54 more)

### Community 33 - "properties"
Cohesion: 0.06
Nodes (32): additionalProperties, $ref, $ref, type, $id, $ref, correlationId, interfaceVersion (+24 more)

### Community 34 - "ClinicalGraphModel"
Cohesion: 0.19
Nodes (21): ClinicalGraphModel, Node, Potential, Any, ValidationMessage, expected_probability_value_count(), flatten_numbers(), parent_cardinality() (+13 more)

### Community 35 - "test_readiness.py"
Cohesion: 0.17
Nodes (30): DiagnosisStore, Persistence adapter for /diagnosis sessions + audit snapshots.      Thread-safe, _break_tmpdb(), _cleanup_tmpdb(), _free_port(), _fresh_tmpdb(), _Handler, _heal_tmpdb() (+22 more)

### Community 36 - "InMemoryPlanEditStore"
Cohesion: 0.21
Nodes (17): ConcurrentSnapshotProvider, final_plan(), finalized_ledger(), follow_up_delta(), Generator, hash_json(), prior_primary_plan(), snapshot() (+9 more)

### Community 37 - "contracts/schemas/1.0.0/auth-session.schema.json"
Cohesion: 0.06
Nodes (30): additionalProperties, type, type, additionalProperties, properties, required, type, $id (+22 more)

### Community 38 - "identifiers.schema.json"
Cohesion: 0.06
Nodes (30): additionalProperties, $ref, $ref, $defs, SemVer, StableCode, UtcTimestamp, Uuid (+22 more)

### Community 39 - "DashboardRepository"
Cohesion: 0.10
Nodes (10): DatabaseAdapter, Connection, Protocol, SQLite adapter. Repository owns SQL, so Postgres can replace adapter later., SQLiteAdapter, DashboardRepository, now_iso(), Any (+2 more)

### Community 40 - "dashboard_backend/main.py"
Cohesion: 0.18
Nodes (29): accept_disclaimer(), canonical_uuid(), create_dashboard_session(), create_workflow_context(), dashboard_index(), delete_dashboard_session(), discover_registered_module(), display_name_for() (+21 more)

### Community 41 - "test_csrf.py"
Cohesion: 0.15
Nodes (28): Test-only hook (mirrors ``auth.reset_auth_for_tests``). Pin a     known secret s, reset_secret_for_tests(), _client(), _free_port(), _Handler, main(), _mint_bad_token(), _mint_valid_token() (+20 more)

### Community 42 - "dashboard.js"
Cohesion: 0.15
Nodes (28): acceptDisclaimer(), activateDevRole(), api, app, buttonMeta(), clearUrl(), escapeHtml(), fmtDate() (+20 more)

### Community 43 - "Medical-History-1.0.0/server.js"
Cohesion: 0.15
Nodes (29): activateMedicalHistory(), ANTIPSYCHOTIC_OPTIONS, CLOZAPINE_CONTRAINDICATION_OPTIONS, COMORBIDITY_OPTIONS, crypto, ensureDataFiles(), ensureJsonFile(), fs (+21 more)

### Community 44 - "ProbabilisticRecommendation"
Cohesion: 0.18
Nodes (17): TP11SafetyPolicyTests, _Definition, EmergencyEscalation, _load_bundled_definition(), _normalized(), _normalized_set(), _parse_definition(), ProbabilisticRecommendation (+9 more)

### Community 45 - "Any"
Cohesion: 0.10
Nodes (10): date, CanonicalEncounterCreate, CanonicalPatientCreate, ClinicalFlag, ClinicalSection, generate_patient_code(), PatientDemographics, PatientIntake (+2 more)

### Community 46 - "test_auth.py"
Cohesion: 0.13
Nodes (25): _build_session(), _arm_with_csrf(), _client_for(), _exercise(), _free_port(), _Handler, main(), BaseHTTPRequestHandler (+17 more)

### Community 47 - "TestPatientIdentity"
Cohesion: 0.11
Nodes (17): _build_patient(), _fetch_patient(), Patient, _PatientNotFound, _PatientUnavailable, Exception, Patient identity adapter for the diagnosis module.  Aligns the diagnosis module', The registry responded 404 — the code is not a known patient. (+9 more)

### Community 48 - "test_config.py"
Cohesion: 0.26
Nodes (28): _clear_env(), main(), Settings-adapter tests for the diagnosis module.  Strategy:     - Exercise the `, When ``AUTH_BASE_URL`` is unset, ``auth.AUTH_BASE_URL`` defaults to     the sett, ``dashboard.MODULE_ID`` defaults to the settings-derived id; a     custom ``DIAG, ``app.py`` builds its CORS middleware from ``settings.cors_origins``     (no lon, ``__main__`` builds its ``--host`` / ``--port`` defaults from     ``settings`` (, Re-import ``diagnosis.config`` so ``_load`` re-runs against the     current env. (+20 more)

### Community 49 - "check_readiness"
Cohesion: 0.12
Nodes (23): Standalone FastAPI app for the diagnosis module.  Usage:     python -m diagnosis, common_readiness(), contract_payload(), contract_registry(), install_common_routes(), Common Insight contract and readiness adapter for the diagnosis module., Map module-local checks onto the common readiness vocabulary., Load the immutable common artifacts without importing domain code. (+15 more)

### Community 50 - "properties"
Cohesion: 0.10
Nodes (28): items, items, type, items, type, additionalProperties, minLength, properties (+20 more)

### Community 51 - "PlanContent"
Cohesion: 0.07
Nodes (28): PlanContent, pattern, type, additionalProperties, properties, required, type, additionalProperties (+20 more)

### Community 52 - "PrimaryTreatmentPlan"
Cohesion: 0.16
Nodes (11): DdiFailure, DdiInteraction, DdiMedicationIdentity, _DdiPort, _InvalidDdiResponse, Any, Protocol, ValueError (+3 more)

### Community 53 - "compile_xmlbif"
Cohesion: 0.20
Nodes (17): _Element, read_registry_schema(), _compile_definition(), _compile_variable(), compile_xmlbif(), _node_kind(), _parse_table(), _parse_xml_document() (+9 more)

### Community 54 - "HANDOFF — `severity` module"
Cohesion: 0.07
Nodes (26): 10. The "ponytail" philosophy (context, not legal), 11. How to verify your change, 12. If you only read three things, 1. What this module is, 2. Repo layout (only 4 source files matter), 3. Stack & runtime, 4.1 Boot sequence, 4.2 Helpers (+18 more)

### Community 55 - "properties"
Cohesion: 0.08
Nodes (24): enum, type, SafetyFinding, $ref, $ref, $ref, minLength, type (+16 more)

### Community 56 - "SupersessionError"
Cohesion: 0.22
Nodes (16): _await_if_needed(), FollowUpSnapshotProvider, _hash_json(), _instant(), _json_copy(), _nonblank(), _parse_instant(), Any (+8 more)

### Community 57 - "ingest.mjs"
Cohesion: 0.14
Nodes (22): addDoseSuggestions(), buildKnowledgeBase(), cleanLine(), compareRelativePaths(), createInteraction(), createRevisionId(), __dirname, drugIdFor() (+14 more)

### Community 58 - "diagnosis/config.py"
Cohesion: 0.10
Nodes (22): _http_selfcheck(), Run the REST-contract unittest cases under the bypass shim.      The inline ``as, _config_selfcheck(), _env_list(), _env_truthy(), _load(), Settings adapter for the diagnosis module.  Single source of truth for every pre, Stable id this module advertises to Dashboard discovery.          Derived from ` (+14 more)

### Community 59 - "ddi-engine.js"
Cohesion: 0.18
Nodes (21): addDoseSuggestions(), addIdentityCandidate(), assignMedicationInstanceIds(), buildIndex(), checkInteractions(), cleanReportLine(), createEmptyIndex(), createParsedInteraction() (+13 more)

### Community 60 - "TestCriteriaRules"
Cohesion: 0.13
Nodes (5): CriteriaEvaluation, evaluate(), Return computed evidence without any assertion fields., Pure function: given the clinician's checked criteria, return a     CriteriaEval, TestCriteriaRules

### Community 61 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+16 more)

### Community 62 - "properties"
Cohesion: 0.08
Nodes (24): enum, minLength, type, pattern, properties, minLength, type, behavior (+16 more)

### Community 63 - "INSIGHT Authentication v1 Contract"
Cohesion: 0.09
Nodes (22): Admin Account Lifecycle Boundaries, Admin Account Management, Cookie Policy, Current API Routes, Dashboard Redirect Behavior, Disclaimer Behavior, Downstream Verification Checklist, `GET /api/auth/admin/users` (+14 more)

### Community 64 - "TestCSRF"
Cohesion: 0.14
Nodes (4): _fake_request(), Minimal stand-in for ``fastapi.Request`` for dep-level unittests.     ``auth.req, TestAuthRejection, TestCSRF

### Community 65 - "INSIGHT Treatment Plan"
Cohesion: 0.09
Nodes (21): Context relationships, Entity ownership, INSIGHT System Context Map, Non-negotiable ownership rule, Ownership change control, Prohibited coupling, Relationship rules, 1. Development Mode (Recommended for UI work) (+13 more)

### Community 66 - "properties"
Cohesion: 0.09
Nodes (23): type, type, minLength, type, type, type, properties, additionalProperties (+15 more)

### Community 67 - "check_tp05_contracts.py"
Cohesion: 0.21
Nodes (14): check_compatibility(), ContractError, lint_openapi(), load(), _pointer(), Path, ValueError, Offline TP-05 JSON Schema, example, compatibility, and OpenAPI conformance. (+6 more)

### Community 68 - "provenance.schema.json"
Cohesion: 0.09
Nodes (21): additionalProperties, $id, recordedAt, sourceResourceId, properties, recordedAt, recordedBy, sourceModule (+13 more)

### Community 69 - "store.py"
Cohesion: 0.14
Nodes (12): Cursor, _canonical_timestamp(), _now_iso(), SQLite-backed repository adapter for diagnosis sessions.  Replaces the module-gl, Insert a new empty session. Returns ``True`` if created., Persist checked criteria + clinician decision. Returns the         full session, JSON snapshot for the Insight audit logger. Records every         successful put, Hard reset. Self-check / test fixture support only. (+4 more)

### Community 70 - "severity"
Cohesion: 0.09
Nodes (22): minLength, type, minLength, type, instrument, interpretation, score, severity (+14 more)

### Community 71 - "review-workspace.ts"
Cohesion: 0.17
Nodes (18): App(), reviewCase, clonePlan(), compare(), Comparison, createReviewWorkspace(), Dose, fields (+10 more)

### Community 72 - "ConfigurationError"
Cohesion: 0.16
Nodes (11): TP22DeploymentTests, _bool(), ConfigurationError, ValueError, main(), migration_gate(), Settings, Container startup and migration readiness gate (TP-22). (+3 more)

### Community 73 - "SQLiteRepository"
Cohesion: 0.16
Nodes (6): TP19MigrationTests, RuntimeRecord, Connection, datetime, Path, SQLiteRepository

### Community 74 - "pagination.schema.json"
Cohesion: 0.10
Nodes (20): additionalProperties, $id, oneOf, minimum, type, minimum, type, properties (+12 more)

### Community 75 - "SQLiteAdapter"
Cohesion: 0.22
Nodes (14): _empty_migration_report(), _is_uuid(), migrate_patients_to_identity_table(), now_iso(), _patient_code(), Any, Connection, _record_id() (+6 more)

### Community 76 - "ValidateModelTests"
Cohesion: 0.37
Nodes (3): _make_node(), _make_potential(), ValidateModelTests

### Community 77 - "diagnosis/csrf.py"
Cohesion: 0.13
Nodes (20): mint(), Request, Signed double-submit CSRF for the diagnosis module's write routes.  PUT /diagnos, FastAPI dependency. Fail closed (403) on any mismatch.      Mirrors ``auth.requi, Attach an HMAC-SHA256 signature to ``raw``. Returns ``raw.sig``., Constant-time check that ``token`` was signed by this secret., Mint a fresh signed token. Callers set it as the CSRF cookie and     surface it, Stamp the ``csrf`` cookie on ``response``. FastAPI's     ``set_cookie`` is the p (+12 more)

### Community 78 - "test_routes.py"
Cohesion: 0.17
Nodes (20): main(), _paths(), Route-seam split tests for the diagnosis module.  Issue: split public routes fro, Invariant 4: ``/_meta`` and ``/_csrf`` MUST match before     ``/{code}`` or Fast, The Dashboard discovery route lives in ``dashboard.py`` only —     invariant 10, The audit-log route lives in ``dashboard.py`` only — invariant 10     (seam spli, `MODULE_ID` is part of the discovery contract — Dashboard joins on     it and th, Tests + Insight callers import contract symbols from     ``diagnosis.api`` direc (+12 more)

### Community 79 - "properties"
Cohesion: 0.10
Nodes (21): $ref, PlanEdit, $ref, $ref, enum, type, pattern, type (+13 more)

### Community 80 - "reduce"
Cohesion: 0.22
Nodes (11): main(), Run: python prototype/run_lifecycle.py (synthetic walkthrough only)., initial_state(), ValueError, THROWAWAY TP-04 lifecycle prototype. Not for clinical use or production import., Return a new state for one action; never mutate ``state``., reduce(), _require() (+3 more)

### Community 81 - "properties"
Cohesion: 0.10
Nodes (19): additionalProperties, pattern, type, type, type, $id, $ref, $ref (+11 more)

### Community 82 - "fetch_auth_identity"
Cohesion: 0.22
Nodes (14): auth_session_url(), AuthSessionError, _expiry(), fetch_auth_identity(), _fetch_json(), forwarded_auth_headers(), normalize_authenticated_session(), normalize_psychiatrist_session() (+6 more)

### Community 83 - "Add New Patient API Contract"
Cohesion: 0.10
Nodes (19): Add New Patient API Contract, Add New Patient Owned Endpoints, Auth Contract, Boundary, CSRF Contract, Dashboard Launch Contract, Endpoints Covered, Future Seam: Follow-up module (+11 more)

### Community 84 - "clinical_graph_models/__init__.py"
Cohesion: 0.19
Nodes (9): contract_payload(), error_response(), _meta(), ok_response(), Any, RouteContract, TargetNodeContract, XmlBifTarget (+1 more)

### Community 85 - "DDI-Checker-1.2.0/package.json"
Cohesion: 0.10
Nodes (19): description, keywords, license, name, private, scripts, ingest, test (+11 more)

### Community 86 - "sqlite_repository.py"
Cohesion: 0.24
Nodes (12): Collection, RetentionPolicyTests, TP19BackupTests, PostgreSQL adapter for the Treatment Plan repository seam., apply_retention(), Any, datetime, Approval-gated PHI redaction with audit-record preservation. (+4 more)

### Community 87 - "HttpContractAdapter"
Cohesion: 0.15
Nodes (8): createCommonContractHandlers(), HttpContractAdapter, InMemoryContractAdapter, problem(), responseJson(), contract, openapi, problemSchema

### Community 88 - "MigrationRunner"
Cohesion: 0.20
Nodes (8): Dialect, Migration, MigrationRunner, _postgres_immutable_trigger(), Any, Path, Dialect-aware, reversible migrations for the repository adapters., Apply or reverse the same ordered migration set on SQLite/PostgreSQL.

### Community 89 - "Dashboard — Module Handoff"
Cohesion: 0.11
Nodes (18): 1. What this module is, 2. Current state of the working tree, 3. Architecture, 4. How to run, 5. Known gaps and things still owed, 6. Workspace button contracts (for reference), 7. Where to look first when changing something, 8. Etiquette for upstream changes (+10 more)

### Community 90 - "ua-finalize.cjs"
Cohesion: 0.11
Nodes (16): assigned, fileTypes, finalGraph, fs, graph, inter, issues, layers (+8 more)

### Community 91 - "$defs"
Cohesion: 0.09
Nodes (21): $defs, FollowUpDelta, Instant, RecommendationRun, Uuid, Version, additionalProperties, type (+13 more)

### Community 92 - "enum"
Cohesion: 0.13
Nodes (15): enum, acknowledged, confirmed, editing, evaluating, gathering-inputs, generated, generation-failed (+7 more)

### Community 93 - "required"
Cohesion: 0.12
Nodes (19): items, type, approvals, items, required, type, id, name (+11 more)

### Community 94 - "module-contract.json"
Cohesion: 0.11
Nodes (17): auth, required, schemes, basePath, capabilities, compatibilityRoutes, dependencies, interfaceVersion (+9 more)

### Community 95 - "required"
Cohesion: 0.12
Nodes (18): required, auth, basePath, capabilities, compatibilityRoutes, dependencies, deprecated, diagnosis (+10 more)

### Community 96 - "resource-version.schema.json"
Cohesion: 0.11
Nodes (17): additionalProperties, pattern, type, $id, version, properties, etag, updatedAt (+9 more)

### Community 97 - "validate-kb.mjs"
Cohesion: 0.18
Nodes (14): CONFIDENCE, fingerprint(), here, label(), object(), pair(), REQUIRED, runCli() (+6 more)

### Community 98 - "HANDOFF — `diagnosis` module"
Cohesion: 0.11
Nodes (17): 10. Gotchas that cost time if you don't know, 11. Glossary, 12. If you only read four files, 1. What this module is, 2. Repo layout, 3. The two layers and how to find things, 4. The web page (`static/index.html`), 5. Run it (+9 more)

### Community 99 - "public/app.js"
Cohesion: 0.22
Nodes (14): activateFromCode(), addMedicationRow(), api(), clearError(), elements, escapeAttribute(), isYes(), loadOptions() (+6 more)

### Community 100 - "request-metadata.schema.json"
Cohesion: 0.12
Nodes (16): additionalProperties, $ref, $ref, $id, correlationId, requestId, $ref, properties (+8 more)

### Community 101 - "report-parser.js"
Cohesion: 0.31
Nodes (16): cleanLine(), collectSections(), extractDoseSuggestions(), extractListDrugs(), inferMechanism(), inferMonitoring(), inferRecommendation(), isNoiseLine() (+8 more)

### Community 102 - "required"
Cohesion: 0.13
Nodes (17): required, diagnosis, enum, required, add-new-patient, bn-manager, capturedAt, category (+9 more)

### Community 103 - "properties"
Cohesion: 0.12
Nodes (17): pattern, type, SourceReference, minLength, type, type, contentHash, etag (+9 more)

### Community 104 - "SQLitePlanEditStore"
Cohesion: 0.26
Nodes (8): PlanAlreadyExists, StoredPlanEdits, _dump(), Any, Connection, Path, SQLite adapter for the TP-15 append-only Plan Edit store seam., SQLitePlanEditStore

### Community 105 - "properties"
Cohesion: 0.12
Nodes (16): const, const, const, const, pattern, type, properties, basePath (+8 more)

### Community 106 - "type"
Cohesion: 0.13
Nodes (16): items, type, uniqueItems, minLength, type, type, items, type (+8 more)

### Community 107 - "dashboard_backend/auth.py"
Cohesion: 0.26
Nodes (12): auth_session_url(), AuthSessionError, fetch_auth_identity(), _fetch_json(), forwarded_auth_headers(), normalize_auth_identity(), _parse_expiry(), Any (+4 more)

### Community 108 - "manifest.json"
Cohesion: 0.13
Nodes (14): audit-event.json, auth-denial.json, auth-session.json, idempotency-conflict.json, identifiers.json, module-contract.json, pagination.json, provenance.json (+6 more)

### Community 109 - "items"
Cohesion: 0.13
Nodes (15): items, type, const, additionalProperties, properties, required, deprecated, path (+7 more)

### Community 110 - "required"
Cohesion: 0.13
Nodes (15): auth, basePath, capabilities, compatibilityRoutes, dependencies, interfaceVersion, moduleId, moduleVersion (+7 more)

### Community 111 - "properties"
Cohesion: 0.13
Nodes (15): const, minimum, type, minLength, type, const, httpOnly, maxAgeSeconds (+7 more)

### Community 113 - "Severity Module"
Cohesion: 0.13
Nodes (14): API contract, As a sub-module, Design compliance, Features, File layout, GET `/api/severity/:patient_code`, Intentionally deferred (ponytail ledger), PUT `/api/severity/:patient_code` (+6 more)

### Community 114 - "medicalHistory"
Cohesion: 0.13
Nodes (15): items, type, uniqueItems, items, type, uniqueItems, additionalProperties, properties (+7 more)

### Community 115 - "required"
Cohesion: 0.15
Nodes (15): required, required, action, code, correlationId, detail, recordedAt, requestId (+7 more)

### Community 116 - ".dashboard"
Cohesion: 0.17
Nodes (4): AuditEvent, MetricPoint, opaque_id(), Any

### Community 117 - "auth"
Cohesion: 0.14
Nodes (14): additionalProperties, properties, required, type, minLength, required, schemes, auth (+6 more)

### Community 118 - "properties"
Cohesion: 0.19
Nodes (14): items, items, items, type, $ref, additionalProperties, properties, type (+6 more)

### Community 119 - "properties"
Cohesion: 0.14
Nodes (14): type, minLength, type, items, type, uniqueItems, criteriaSets, declaration (+6 more)

### Community 120 - "Severity-1.1.0/package.json"
Cohesion: 0.14
Nodes (13): express, author, dependencies, express, description, keywords, license, main (+5 more)

### Community 121 - "Repository Handoff — Add New Patient Module"
Cohesion: 0.14
Nodes (13): Current invariants (do not break), How to run, Known limitations (not bugs), Layout, Patient identifier contract (F1.1), Recent additions visible in current code but not in older docs, Repository Handoff — Add New Patient Module, Request payload shape (+5 more)

### Community 122 - "csrf"
Cohesion: 0.14
Nodes (14): bootstrapPath, cookieName, failureStatus, headerName, httpOnly, maxAgeSeconds, path, sameSite (+6 more)

### Community 123 - "errorPolicy"
Cohesion: 0.14
Nodes (14): message, status, errorPolicy, csrfFailure, disclosure, loginFailure, readinessFailure, validationFailure (+6 more)

### Community 124 - "timeoutPolicy"
Cohesion: 0.14
Nodes (14): type, caller, readiness, server, timeoutPolicy, type, type, additionalProperties (+6 more)

### Community 125 - "required"
Cohesion: 0.19
Nodes (14): required, name, path, required, bootstrapPath, cookieName, failureStatus, headerName (+6 more)

### Community 126 - "Add-New-Patient-1.1.0/DESIGN.md"
Cohesion: 0.15
Nodes (12): 1. Visual Theme & Atmosphere, 2. Color System, 3. Typography, 4. Components & Patterns, 5. Spacing & Layout, 6. Motion & Interaction, Accessibility, Contrast Ratios (+4 more)

### Community 127 - "properties"
Cohesion: 0.15
Nodes (13): const, minLength, type, properties, const, minLength, type, bootstrapPath (+5 more)

### Community 128 - "Authentication-1.1.0/DESIGN.md"
Cohesion: 0.15
Nodes (12): 1. Visual Theme & Atmosphere, 2. Color System, 3. Typography, 4. Components & Patterns, 5. Spacing & Layout, 6. Motion & Interaction, Accessibility, Contrast Ratios (+4 more)

### Community 130 - "Severity-1.1.0/server.js"
Cohesion: 0.22
Nodes (9): app, clone(), createApp(), createJsonAssessmentStore(), createMemoryAssessmentStore(), DEFAULT_DATA_DIR, __dirname, __filename (+1 more)

### Community 131 - "code"
Cohesion: 0.15
Nodes (13): minLength, pattern, type, enum, type, additionalProperties, properties, type (+5 more)

### Community 132 - "required"
Cohesion: 0.15
Nodes (13): schemaVersion, required, approvals, clinicalScope, clinicalValidation, clinicalWorkflow, decisionGates, documentId (+5 more)

### Community 133 - "contract.json"
Cohesion: 0.17
Nodes (11): basePath, capabilities, compatibilityRoutes, dependencies, interfaceVersion, moduleId, moduleVersion, schemaVersion (+3 more)

### Community 134 - "auth"
Cohesion: 0.17
Nodes (12): additionalProperties, properties, required, type, required, schemes, auth, required (+4 more)

### Community 135 - "properties"
Cohesion: 0.17
Nodes (12): additionalProperties, type, minLength, type, const, properties, csrf, downstreamTrust (+4 more)

### Community 136 - "INSIGHT Authentication module"
Cohesion: 0.17
Nodes (11): Admin account management, Contract, Design, Environment, INSIGHT Authentication module, Other modules register psychiatrists, Persistence, Roles (+3 more)

### Community 138 - "Medical-History-1.0.0/package.json"
Cohesion: 0.17
Nodes (11): description, engines, node, main, name, private, scripts, dev (+3 more)

### Community 139 - "properties"
Cohesion: 0.17
Nodes (12): pattern, type, format, type, properties, action, id, recorded (+4 more)

### Community 140 - "EditLedgerTests"
Cohesion: 0.32
Nodes (7): EditLedgerRouteTests, EditLedgerTests, ledger(), primary_plan(), PolicyBound, A trusted policy constraint for one exact JSON Pointer., ReasonRequired

### Community 141 - "PostgreSQLRepository"
Cohesion: 0.27
Nodes (4): PostgreSQLRepository, Any, datetime, Path

### Community 142 - "Add-New-Patient-1.1.0/app.js"
Cohesion: 0.25
Nodes (9): CLIENT_VALIDATION_MESSAGES, createAddNewPatientModule(), FIELD_INPUT_NAMES, generateBrowserPatientCode(), getRequiredElement(), isValidDob(), normalizePatientInput(), parseListInput() (+1 more)

### Community 143 - "properties"
Cohesion: 0.18
Nodes (11): properties, type, type, const, type, jwksPolicy, jwtPolicy, legacySession (+3 more)

### Community 144 - "properties"
Cohesion: 0.18
Nodes (11): type, type, properties, type, csrfFailure, disclosure, loginFailure, readinessFailure (+3 more)

### Community 145 - "Authentication-1.1.0/contracts/schemas/1.0.0/auth-session.schema.json"
Cohesion: 0.18
Nodes (10): additionalProperties, $id, authenticated, gates, schemaVersion, session, user, required (+2 more)

### Community 146 - "gates"
Cohesion: 0.18
Nodes (11): type, additionalProperties, properties, required, type, disclaimerAccepted, passwordChangeRequired, type (+3 more)

### Community 147 - "BN Manager"
Cohesion: 0.18
Nodes (10): API, Architecture outputs, BN Manager, Canonical networks, Evaluate a registry model, Model pipeline, Python API, Run (+2 more)

### Community 148 - "Dashboard API Contract: INSIGHT Workspace"
Cohesion: 0.18
Nodes (10): Auth Verification Contract, Create Dashboard Session, Dashboard API Contract: INSIGHT Workspace, Disclaimer Acceptance, Health And Readiness, INSIGHT Workspace Response, Primary INSIGHT Flow, Runtime Module Discovery (+2 more)

### Community 149 - "Drug-Drug Interaction Checker"
Cohesion: 0.18
Nodes (10): Browser storage failure behavior, Drug-Drug Interaction Checker, Knowledge-base validation, Local KB upgrades and conflicts, Medication Identity Resolution, Module Shape, Production Notes, Run (+2 more)

### Community 151 - "package_release.py"
Cohesion: 0.38
Nodes (9): CompletedProcess, build(), clinical_release_gates(), main(), Path, Cross-platform release image build, SBOM, scan, and human-gated promotion., run(), sbom() (+1 more)

### Community 152 - "add_new_patient_backend/csrf.py"
Cohesion: 0.27
Nodes (8): csrf_error(), generate_csrf_token(), JSONResponse, Request, request_has_valid_csrf(), sign_csrf_token(), verify_csrf_token(), csrf()

### Community 153 - "sessionCookie"
Cohesion: 0.20
Nodes (10): securityPolicy, downstreamTrust, jwks, sessionCookie, httpOnly, maxAgeSeconds, name, path (+2 more)

### Community 154 - "ModuleRegistration"
Cohesion: 0.42
Nodes (6): Settings, discover_module(), ModuleRegistration, Any, ready_url_for(), _request_json()

### Community 155 - "DDI-Checker 1.1.0 — Architecture & Data Flow"
Cohesion: 0.20
Nodes (9): 1. Module dependency & layering, 2. Runtime data-flow (the four layers described in the README), DDI-Checker 1.1.0 — Architecture & Data Flow, KB validation gate, Key relationships the diagrams capture, Knowledge-base revision identity, Potential follow-ups worth a look, Storage boundary (+1 more)

### Community 156 - "identifier"
Cohesion: 0.20
Nodes (10): additionalProperties, properties, required, type, identifier, what, additionalProperties, properties (+2 more)

### Community 157 - "decisionGates"
Cohesion: 0.20
Nodes (10): type, clinicalValidation, maxItems, minItems, owners, regulatoryAssessment, type, type (+2 more)

### Community 158 - "TP-01 — Intended use, clinical scope, and release gates"
Cohesion: 0.20
Nodes (9): Change control, Clinical validation and release rule, Current disposition, Emergency behavior, Not-supported cases, Regulatory assessment, Required decision meeting, Scope matrix completion rules (+1 more)

### Community 159 - "INSIGHT Treatment Plan Handoff"
Cohesion: 0.20
Nodes (9): Completed Work, Current State and Critical Constraint, INSIGHT Treatment Plan Handoff, Objective, Recommended Next Work, Sensitive-Data Note, Source of Truth, Technical Seams (+1 more)

### Community 160 - "RuntimeError"
Cohesion: 0.44
Nodes (9): available_port(), hardened_run_command(), main(), Independent standalone, unified-route, TLS, and recovery verification., request(), verify_container(), verify_http(), verify_tls() (+1 more)

### Community 161 - "evaluation.py"
Cohesion: 0.56
Nodes (8): Evidence, _enumerate_chance_assignments(), evaluate_expected_utilities(), evaluate_posterior(), EvaluationResult, _evidence_weight(), flat_table_cache(), table_value()

### Community 162 - "required"
Cohesion: 0.22
Nodes (9): additionalProperties, required, type, compatibility, jwksPolicy, jwtPolicy, legacySession, legacySessionPolicy (+1 more)

### Community 163 - "required"
Cohesion: 0.22
Nodes (9): additionalProperties, required, type, errorPolicy, csrfFailure, disclosure, loginFailure, readinessFailure (+1 more)

### Community 164 - "security-policy.schema.json"
Cohesion: 0.22
Nodes (8): additionalProperties, $id, required, $schema, type, csrf, downstreamTrust, jwks

### Community 166 - "Dashboard Module"
Cohesion: 0.22
Nodes (8): Dashboard Module, Files, Health, Module Interface, Postgres Upgrade Path, Run, Test, Workspace Rules

### Community 167 - "test/server.test.js"
Cohesion: 0.22
Nodes (6): assert, fs, os, path, { spawn }, test

### Community 168 - "CommonContractsClient"
Cohesion: 0.25
Nodes (3): CommonContractsClient, Generated from contracts/openapi/1.0.0/common.openapi.json; do not edit., Small generated client; transport is injected by the consuming module.

### Community 169 - "properties"
Cohesion: 0.25
Nodes (8): minLength, type, displayName, username, properties, maxLength, minLength, type

### Community 170 - "roles"
Cohesion: 0.25
Nodes (8): enum, psychiatrist, roles, items, minItems, type, uniqueItems, admin

### Community 171 - "get_settings"
Cohesion: 0.50
Nodes (3): BnManagerSettings, get_settings(), main()

### Community 172 - "Dashboard Dataset Schema"
Cohesion: 0.25
Nodes (7): Dashboard Dataset Schema, dashboard_sessions, Explicit Non-Owners, Module Route Placeholders, Tables, workspace_events, Workspace Strings

### Community 173 - "Dashboard-1.2.0/package.json"
Cohesion: 0.25
Nodes (7): name, private, scripts, start, test, type, version

### Community 174 - "storage-adapter.test.mjs"
Cohesion: 0.32
Nodes (4): browserStorageAdapter(), memoryStorageAdapter(), { browserStorageAdapter, memoryStorageAdapter }, require

### Community 175 - "auth-adapter.test.js"
Cohesion: 0.32
Nodes (5): createMemoryAuthAdapter(), parseCanonicalSession(), assert, canonical, { createMemoryAuthAdapter, parseCanonicalSession }

### Community 176 - "items"
Cohesion: 0.25
Nodes (8): items, type, additionalProperties, properties, required, type, entity, what

### Community 177 - "required"
Cohesion: 0.39
Nodes (8): psychiatrist, required, role, enum, clinicalSafetyOfficer, privacy, product, regulatory

### Community 179 - "Repository"
Cohesion: 0.25
Nodes (3): Protocol, Persistence seam used by the application and its tests., Repository

### Community 180 - "supportedClinicalScope"
Cohesion: 0.29
Nodes (7): declaration, populations, workflows, supportedClinicalScope, additionalProperties, required, type

### Community 181 - "Patient Domain Glossary"
Cohesion: 0.29
Nodes (6): ClinicalFlag, Contract Notes, IntakeRecord, Patient, Patient Domain Glossary, TreatmentHistory

### Community 182 - "Add New Patient Module"
Cohesion: 0.29
Nodes (6): Add New Patient Module, Embed Contract, REST API, Run, Stack, Tests

### Community 183 - "supportedClinicalScope"
Cohesion: 0.29
Nodes (7): declaration, populations, workflows, supportedClinicalScope, additionalProperties, required, type

### Community 184 - "id"
Cohesion: 0.29
Nodes (7): format, type, minLength, type, expiresAt, id, properties

### Community 185 - "user"
Cohesion: 0.29
Nodes (7): user, additionalProperties, required, type, displayName, roles, username

### Community 187 - "Medical History Module"
Cohesion: 0.29
Nodes (6): Collected information, Correlation and persistence, Internal REST API, Medical History Module, Production note, Run and test

### Community 188 - "test_auth_adapter.js"
Cohesion: 0.38
Nodes (4): createMemoryAuthAdapter(), parseCanonicalSession(), canonical, memory

### Community 189 - "INSIGHT canonical identifiers, encounters, and transport interface v1"
Cohesion: 0.29
Nodes (6): Canonical identifiers and aliases, Conformance, Encounter semantics, INSIGHT canonical identifiers, encounters, and transport interface v1, Request lineage and replay, Time, schemas, and optimistic concurrency

### Community 190 - "required"
Cohesion: 0.29
Nodes (7): action, correlationId, id, outcome, recorded, resourceType, required

### Community 191 - "who"
Cohesion: 0.29
Nodes (7): who, required, additionalProperties, properties, required, type, identifier

### Community 193 - "compatibility"
Cohesion: 0.33
Nodes (6): compatibility, jwksPolicy, jwtPolicy, legacySession, legacySessionPolicy, sessionAuthority

### Community 194 - "session"
Cohesion: 0.33
Nodes (6): id, session, additionalProperties, required, type, expiresAt

### Community 195 - "MEDICAL_HISTORY_HANDOFF.md"
Cohesion: 0.33
Nodes (5): Architecture, Change guidance, Conditional UI behavior, Persistence and testing, Submission model (v2)

### Community 196 - "agent"
Cohesion: 0.33
Nodes (6): additionalProperties, properties, required, type, agent, who

### Community 197 - "ADR TP-04 - Disposable lifecycle prototype"
Cohesion: 0.33
Nodes (5): ADR TP-04 - Disposable lifecycle prototype, Consequences, Context and decision, Provisional findings to agree with a psychiatrist, Six-scenario walkthrough record

### Community 199 - "capabilities"
Cohesion: 0.40
Nodes (5): items, type, uniqueItems, $ref, capabilities

### Community 200 - "auth"
Cohesion: 0.40
Nodes (5): auth, required, schemes, csrf-double-submit, sessionCookie

### Community 201 - "auth-contract.schema.json"
Cohesion: 0.40
Nodes (4): additionalProperties, $id, $schema, type

### Community 202 - "schemas"
Cohesion: 0.40
Nodes (5): pattern, schemas, items, type, uniqueItems

### Community 203 - "properties"
Cohesion: 0.40
Nodes (5): const, properties, authenticated, schemaVersion, const

### Community 204 - "writeMethods"
Cohesion: 0.40
Nodes (5): PATCH, POST, writeMethods, const, type

### Community 205 - "report-parser-parity.test.mjs"
Cohesion: 0.40
Nodes (3): engine, fixtureDir, require

### Community 206 - "Treatment-Plan/contracts/schemas/1.0.0/audit-event.schema.json"
Cohesion: 0.40
Nodes (4): additionalProperties, $id, $schema, type

### Community 207 - "enum"
Cohesion: 0.40
Nodes (5): denied, failure, success, enum, outcome

### Community 208 - "scope-matrix.schema.json"
Cohesion: 0.40
Nodes (4): $id, $schema, title, type

### Community 211 - ".format"
Cohesion: 0.50
Nodes (3): LogRecord, Any, _safe_fields()

### Community 212 - "schemas"
Cohesion: 0.50
Nodes (4): schemas, auth-contract, auth-session, securityPolicy

### Community 213 - "supportedClinicalScope"
Cohesion: 0.50
Nodes (4): supportedClinicalScope, declaration, populations, workflows

### Community 214 - "timeoutPolicy"
Cohesion: 0.50
Nodes (4): timeoutPolicy, caller, readiness, server

### Community 215 - "XML Bayesian Network Migration"
Cohesion: 0.50
Nodes (3): Decisions, Verification, XML Bayesian Network Migration

### Community 217 - "ddi-engine.test.mjs"
Cohesion: 0.50
Nodes (3): engine, fixtureKb, require

### Community 218 - "ui-source.test.mjs"
Cohesion: 0.50
Nodes (3): __dirname, __filename, projectRoot

### Community 220 - "audit-provenance.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 221 - "clinical-input-snapshot.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 222 - "final-plan.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 223 - "follow-up-delta.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 224 - "plan-edit.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 225 - "primary-plan.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 226 - "Treatment-Plan/contracts/schemas/1.0.0/problem-details.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 227 - "recommendation-run.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 228 - "safety-finding.schema.json"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 229 - "type"
Cohesion: 0.50
Nodes (4): type, decision, null, string

### Community 230 - "check_context_ownership.py"
Cohesion: 0.67
Nodes (3): evaluate(), main(), Validate unique ownership and REST-only cross-module relationship rules.

### Community 231 - "check_identifier_contract.py"
Cohesion: 0.67
Nodes (3): evaluate(), main(), Validate the shared TP-03 identifier and transport contract.

### Community 232 - "check_tp01_release_gate.py"
Cohesion: 0.67
Nodes (3): evaluate(), main(), Fail-closed TP-01 clinical release gate. Uses only the Python standard library.

### Community 233 - "path"
Cohesion: 0.67
Nodes (3): pattern, type, path

### Community 234 - "replacement"
Cohesion: 0.67
Nodes (3): replacement, pattern, type

### Community 238 - "correlationId"
Cohesion: 0.67
Nodes (3): format, type, correlationId

## Knowledge Gaps
- **1386 isolated node(s):** `Rationale`, `1. Visual Theme & Atmosphere`, `2. Color System`, `3. Typography`, `4. Components & Patterns` (+1381 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Security` connect `treatment_plan/app.py` to `AuthTestCase`, `SecurityTests`, `router.py`, `PlanEditLedger`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `_run_migrations()` connect `Authentication-1.1.0/security.py` to `RuntimeError`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `Settings` connect `PlanEditLedger` to `treatment_plan/app.py`, `ConfigurationError`, `EditLedgerTests`, `SecurityTests`, `add_new_patient_backend/csrf.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `DdiMedicationChecker` (e.g. with `RecordingDdiPort` and `TP13DdiCheckTests`) actually correct?**
  _`DdiMedicationChecker` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `PlanEditLedger` (e.g. with `EditLedgerRouteTests` and `EditLedgerTests`) actually correct?**
  _`PlanEditLedger` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `AddNewPatientServer` (e.g. with `SQLiteAdapter` and `PatientRepository`) actually correct?**
  _`AddNewPatientServer` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `PlanFinalizer` (e.g. with `BlockingPort` and `RecordingPort`) actually correct?**
  _`PlanFinalizer` has 22 INFERRED edges - model-reasoned connections that need verification._