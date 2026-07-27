# LLM / Agent Change Constraints Inventory

This document lists **files and code that constrain, block, or gate changes** an LLM or coding agent should not freely make—because of **security**, **clinical safety**, **health/PHI**, **registration/auth**, **policy**, **architecture**, or **release governance**.

These are not generic “best practices.” They are **hard constraints** encoded as:

- fail-closed scripts and CI-style gates
- frozen contracts and schemas
- runtime auth / disclaimer / role guards
- clinical safety and eligibility engines
- handoff docs with explicit “do not” rules
- PHI retention and redaction policies

> **How to use:** Before an agent rewrites auth, diagnosis criteria, severity bands, DDI KB identity, BN model approvals, Treatment Plan release status, or module boundaries, check the matching section below. Many gates intentionally return `BLOCKED` or fail tests if violated.

---

## 1. Repository-wide enforcement gates (fail closed)

These scripts **reject** architecture, contract, or deployment changes that break security or isolation rules.

| File | Constraint |
| --- | --- |
| `scripts/check_architecture.py` | **REST-only ownership.** Blocks cross-module imports (`CROSS_MODULE_IMPORT`), shared DBs (`CROSS_MODULE_DATABASE_PATH`), shared data dirs, shared runtime JSON, and clinical state in browser storage (`CLINICAL_BROWSER_STORAGE`). Modules may only share via `contracts.clients` / `contracts.adapters`. |
| `scripts/check_common_contracts.py` | Locks root `contracts/` package integrity, schema refs, and example validation—prevents ad-hoc API shape drift. |
| `scripts/check_deployment.py` | Validates `deployment/manifest.json` identity (module IDs, ports, paths); rejects invalid registration of modules. |
| `scripts/verify_unified_deployment.py` | Immutable image digests (`@sha256:`), loopback-only binding, no host-published module ports `8101–8109`, TLS/restart/volume policy, rollback drill that **must not fabricate clinical thresholds**. |
| `tests/test_architecture.py` | Unit tests locking architecture checker behavior. |
| `tests/test_common_contracts.py` | Locks common contract package rules. |
| `tests/test_common_contracts_node.mjs` | Node-side common contract checks. |
| `tests/test_deployment_contract.py` | Deployment contract suite. |
| `tests/test_unified_image.py` | Unified image contract. |
| `tests/test_gateway_readiness.py` | Gateway readiness contract. |
| `tests/test_tp22_unified_verification.py` | TP-22 unified verification. |
| `tests/test_tp22_rollback_drill.py` | Rollback drill; no fabricated clinical thresholds. |
| `tests/test_redaction_node.mjs` | Cross-cutting redaction behavior tests. |
| `contracts/package-policy.json` | **Package policy:** shared contracts package may only contain interface artifacts; executable code limited to `adapters/` and `clients/`. |
| `contracts/adapters/python/filesystem.py` | Reads **immutable** contract artifacts from disk; path/version validation. |
| `contracts/clients/python/common_contracts_client.py` | Generated client — **do not edit** (header comment). |
| `contracts/clients/node/common-contracts-client.mjs` | Generated Node client — treat as generated. |

### Root policy documentation

| File | Constraint |
| --- | --- |
| `README.md` | Integration rules: no cross-module imports/DBs; contract-first REST; browser URL policy; **Security and Clinical Safety** section (secrets, loopback, no published module ports, TP-01 gates, decision-support only). Notes Treatment Plan **blocked for clinical release**. |
| `deployment/HOST_RECOVERY.md` | Immutable image recovery contract. |
| `deployment/WINDOWS_DOCKER_DESKTOP.md` | Host/path constraints for Windows deployments. |
| `deployment/nginx.conf` / `deployment/nginx-vps.conf` | Gateway routing and TLS topology—must stay aligned with manifest. |
| `deployment/manifest.json` / `deployment/manifest.schema.json` | Authoritative module registration for the unified image. |
| `deployment/supervisor.py` | Process lifecycle; readiness/migration gating. |
| `deployment/gateway_readiness.py` | Gateway readiness aggregation. |
| `insight-share/README.md` | Demo bundle security notes (JWT secret, not for production hardening alone). |

---

## 2. Clinical release governance (Treatment Plan — intentionally BLOCKED)

These prevent packaging or treating the module as clinically released without multi-role human approval. An LLM **must not invent stakeholder names, signatures, or approvals**.

| File | Constraint |
| --- | --- |
| `Modules/Treatment-Plan/governance/TP-01-SCOPE-AND-RELEASE-GATES.md` | **BLOCKED FOR CLINICAL RELEASE.** Named Clinical Safety Officer required; DG-01–DG-08; change control forbids editing signed matrices in place. |
| `Modules/Treatment-Plan/governance/scope-matrix.v1.json` | Scope matrix currently `draft_pending_approval`; empty supported diagnoses/population; unresolved decision gates. |
| `Modules/Treatment-Plan/governance/scope-matrix.schema.json` | Schema for the matrix—structure is locked. |
| `Modules/Treatment-Plan/governance/context-ownership.v1.json` | Context ownership boundaries between modules. |
| `Modules/Treatment-Plan/governance/ADR-TP-04-DISPOSABLE-LIFECYCLE-PROTOTYPE.md` | Lifecycle prototype ADR—disposable research posture. |
| `Modules/Treatment-Plan/governance/clinical-validation/approvals.v1.json` | Clinical validation approvals evidence structure. |
| `Modules/Treatment-Plan/governance/clinical-validation/cases.v1.json` | Validation cases. |
| `Modules/Treatment-Plan/governance/clinical-validation/hazard-log.v1.json` | Hazard log. |
| `Modules/Treatment-Plan/governance/clinical-validation/observations.v1.json` | Validation observations. |
| `Modules/Treatment-Plan/scripts/check_tp01_release_gate.py` | **Fail-closed gate:** prints `TP-01 RELEASE GATE: BLOCKED` until matrix is fully approved with five named roles and CSO validation. |
| `Modules/Treatment-Plan/scripts/check_tp21_clinical_safety_case.py` | Clinical safety-case gate for TP-21. |
| `Modules/Treatment-Plan/scripts/check_context_ownership.py` | Enforces context ownership map. |
| `Modules/Treatment-Plan/scripts/check_identifier_contract.py` | Identifier/PHI transport contract checks. |
| `Modules/Treatment-Plan/scripts/check_tp05_contracts.py` | Contract package checks for TP. |
| `Modules/Treatment-Plan/scripts/package_release.py` | Release packaging blocked unless gates pass. |
| `Modules/Treatment-Plan/scripts/verify_deployment.py` | Deployment verification for TP. |
| `Modules/Treatment-Plan/tests/test_tp01_release_gate.py` | Expects/locks blocked release gate behavior. |
| `Modules/Treatment-Plan/tests/test_tp21_clinical_validation.py` | Locks clinical validation fail-closed rules. |
| `Modules/Treatment-Plan/HANDOFF.md` | Explicit: do not invent stakeholder approvals; no PHI/credentials/signatures in source control; fail-closed clinical safety gates. |
| `Modules/Treatment-Plan/README.md` | Documents blocked clinical release and dual-approval retention. |
| `Modules/Treatment-Plan/CONTEXT-MAP.md` | Module context ownership map. |

---

## 3. Authentication, registration, disclaimer, and session gates

These control **who may use the app** and **what clinical claims are allowed**. Agents must not bypass disclaimer, CSRF, role, or password gates.

### Auth module (authoritative)

| File | Constraint |
| --- | --- |
| `Modules/Authentication-1.1.0/disclaimer_contract.py` | **Research prototype disclaimer**—not a medical device; no autonomous diagnosis/prescribe; safety-critical decisions require clinician; privacy/AI data-sending warnings. Versioned (`CURRENT_DISCLAIMER_VERSION`). |
| `Modules/Authentication-1.1.0/security.py` | Sessions, JWT, bcrypt, CSRF cookies/headers, login lockout, secure cookie policy, disclaimer acceptance records, role gating. |
| `Modules/Authentication-1.1.0/router.py` | Auth HTTP routes including disclaimer accept/session. |
| `Modules/Authentication-1.1.0/main.py` | App entry; security wiring. |
| `Modules/Authentication-1.1.0/contract.py` | Auth module contract surface. |
| `Modules/Authentication-1.1.0/contracts/schemas/1.0.0/security-policy.schema.json` | Security policy schema (cookies, CSRF, JWKS, trust). |
| `Modules/Authentication-1.1.0/contracts/schemas/1.0.0/auth-contract.schema.json` | Auth contract schema. |
| `Modules/Authentication-1.1.0/contracts/schemas/1.0.0/auth-session.schema.json` | Session shape including gates. |
| `Modules/Authentication-1.1.0/contracts/openapi/1.0.0/authentication.openapi.json` | OpenAPI for auth. |
| `Modules/Authentication-1.1.0/contracts/examples/1.0.0/contract.json` | Example security/timeout/error policy. |
| `Modules/Authentication-1.1.0/docs/Authentication v1 Contract.md` | Contract documentation. |
| `Modules/Authentication-1.1.0/docs/Executive Summary.md` | Security/product summary. |
| `Modules/Authentication-1.1.0/README.md` | Disclaimer gate: psychiatrist cannot reach dashboard until acceptance for active version. |
| `Modules/Authentication-1.1.0/DESIGN.md` | Design constraints. |
| `Modules/Authentication-1.1.0/tests/test_security_behavior.py` | Security behavior locks. |
| `Modules/Authentication-1.1.0/tests/test_auth03_security.py` | Auth security suite. |
| `Modules/Authentication-1.1.0/tests/test_routes_auth.py` | Route-level auth gates. |
| `Modules/Authentication-1.1.0/tests/test_contract.py` | Contract freeze tests. |
| `Modules/Authentication-1.1.0/tests/test_auth_uuid_contract.py` | UUID identity contract. |
| `Modules/Authentication-1.1.0/tests/test_migrations.py` | Schema migration safety. |

### Downstream auth adapters (must reuse auth session contract)

| File | Constraint |
| --- | --- |
| `Modules/Dashboard-1.2.0/dashboard_backend/main.py` | Session + auth re-validation; disclaimer accept route (psychiatrist-only). |
| `Modules/Dashboard-1.2.0/dashboard_backend/repository.py` | `disclaimer_accepted_at` stamping. |
| `Modules/Dashboard-1.2.0/dashboard_backend/db.py` | Session schema with disclaimer column. |
| `Modules/Dashboard-1.2.0/dashboard_backend/discovery.py` | Role-scoped module registration discovery. |
| `Modules/Dashboard-1.2.0/dashboard_backend/config.py` | Module registry validation (roles, contract URLs). |
| `Modules/Dashboard-1.2.0/dashboard.js` | Frontend disclaimer gate disables module launch until accepted. |
| `Modules/Dashboard-1.2.0/api-contract.md` | Disclaimer-required/blocked states; no PHI in URLs. |
| `Modules/Dashboard-1.2.0/HANDOFF.md` | **Inviolable** internal REST boundary; do not weaken auth; blocked session statuses list. |
| `Modules/Dashboard-1.2.0/README.md` | Boundary rule + rejected auth session states. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/auth_adapter.py` | Session adapter; disclaimer/forced-password sessions blocked. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/main.py` | Role guards (`admin`, clinical roles); protected evaluation routes. |
| `Modules/Diagnosis-1.2.0/diagnosis/auth.py` | Auth adapter / fail-closed session checks. |
| `Modules/Diagnosis-1.2.0/diagnosis/csrf.py` | CSRF enforcement. |
| `Modules/Add-New-Patient-1.1.0/add_new_patient_backend/auth.py` | Auth adapter. |
| `Modules/Add-New-Patient-1.1.0/add_new_patient_backend/csrf.py` | CSRF. |
| `Modules/DDI-Checker-1.2.0/src/auth-adapter.js` | Auth adapter for DDI. |
| `Modules/Medical-History-1.0.0/auth-adapter.js` | Auth adapter. |
| `Modules/Medical-History-1.0.0/security.js` | CORS, CSRF, security headers. |
| `Modules/Severity-1.1.0/auth-adapter.js` | Auth adapter. |
| `Modules/Severity-1.1.0/security.js` | Security helpers. |
| `Modules/Treatment-Plan/treatment_plan/security.py` | TP security surface. |
| `Modules/Treatment-Plan/treatment_plan/bn_caller_policy.py` | Caller-aware BN call policy (session/CSRF forward; no spoofed identity). |
| `contracts/schemas/1.0.0/auth-session.schema.json` | Shared auth session schema. |
| `contracts/examples/1.0.0/auth-session.json` / `auth-denial.json` | Session and denial examples. |

---

## 4. Clinical safety engines, eligibility, and health policy code

Runtime logic that **blocks unsafe plans/actions** or enforces decision-support boundaries. Do not “simplify away” fail-closed paths.

### Treatment Plan

| File | Constraint |
| --- | --- |
| `Modules/Treatment-Plan/treatment_plan/safety_policy.py` | Deterministic safety overlay (allergies, contraindications, suicide risk, emergency escalation). |
| `Modules/Treatment-Plan/treatment_plan/policies/safety-policy.schizophrenia-research.v1.json` | Versioned safety policy rules. |
| `Modules/Treatment-Plan/treatment_plan/policies/primary-plan-synthesis.schizophrenia-research.v1.json` | Versioned synthesis policy. |
| `Modules/Treatment-Plan/treatment_plan/policies/__init__.py` | Policy package entry. |
| `Modules/Treatment-Plan/treatment_plan/eligibility.py` | **Generation eligibility** — hard/soft/safety blockers; pathway policy for schizophrenia research. |
| `Modules/Treatment-Plan/treatment_plan/clinical_validation.py` | Fail-closed safety-case release decision; required clinician/CSO approvals. |
| `Modules/Treatment-Plan/treatment_plan/clinical_context.py` | Clinical context dependencies. |
| `Modules/Treatment-Plan/treatment_plan/ddi_check.py` | DDI findings integration (high-severity can block). |
| `Modules/Treatment-Plan/treatment_plan/finalization.py` | Finalization gates; immutable finalized plans. |
| `Modules/Treatment-Plan/treatment_plan/primary_plan.py` | Primary plan synthesis under policy. |
| `Modules/Treatment-Plan/treatment_plan/edit_ledger.py` | Immutable edit ledger. |
| `Modules/Treatment-Plan/treatment_plan/supersession.py` | Supersession without mutating finalized plans. |
| `Modules/Treatment-Plan/treatment_plan/retention.py` | **Approval-gated PHI redaction** — requires `privacy_officer` + `clinical_safety_officer`. |
| `Modules/Treatment-Plan/treatment_plan/suicide_risk_observations.py` | Suicide-risk observation handling. |
| `Modules/Treatment-Plan/treatment_plan/bn_evaluation.py` | BN evaluation adapter; hash/model validation. |
| `Modules/Treatment-Plan/treatment_plan/observability.py` | Label allowlists; no PHI in metrics labels. |
| `Modules/Treatment-Plan/treatment_plan/logging.py` | Logging redaction constraints. |
| `Modules/Treatment-Plan/treatment_plan/migrations/0004_immutable_finalized_plans.sql` | DB immutability for finalized plans. |
| `Modules/Treatment-Plan/treatment_plan/migrations/0004_immutable_finalized_plans.down.sql` | Down migration. |
| `Modules/Treatment-Plan/treatment_plan/migrations/0005_plan_supersessions.sql` | Supersession tables. |
| `Modules/Treatment-Plan/treatment_plan/migrations/0006_tp19_persistence.sql` | Persistence + retention-related schema. |
| `Modules/Treatment-Plan/contracts/IDENTIFIERS-ENCOUNTERS-AND-TRANSPORT.md` | Identifier transport / no PHI in wrong places. |
| `Modules/Treatment-Plan/contracts/identifier-transport-contract.v1.json` | Machine-readable identifier contract. |
| `Modules/Treatment-Plan/contracts/SCHEMA-VERSIONING.md` | Schema versioning rules. |
| `Modules/Treatment-Plan/contracts/manifest.v1.0.0.json` | Contract manifest. |
| `Modules/Treatment-Plan/contracts/openapi/treatment-plan.openapi.v1.0.0.json` | OpenAPI surface. |
| `Modules/Treatment-Plan/tests/test_tp07_security.py` | Security tests. |
| `Modules/Treatment-Plan/tests/test_tp09_eligibility.py` | Eligibility blockers. |
| `Modules/Treatment-Plan/tests/test_tp11_safety_policy.py` | Safety policy locks. |
| `Modules/Treatment-Plan/tests/test_tp12_primary_plan.py` | Plan synthesis under policy. |
| `Modules/Treatment-Plan/tests/test_tp15_edit_ledger.py` | Ledger immutability. |
| `Modules/Treatment-Plan/tests/test_tp16_finalization.py` / `test_tp17_finalization_versioning.py` | Finalization gates. |
| `Modules/Treatment-Plan/tests/test_tp18_supersession.py` | Supersession rules. |
| `Modules/Treatment-Plan/tests/test_tp19_persistence.py` | PHI retention dual approval. |
| `Modules/Treatment-Plan/tests/test_tp20_observability.py` | Observability allowlists. |
| `Modules/Treatment-Plan/tests/test_tp23_suicide_risk_resolution.py` | Suicide risk pathway. |
| `Modules/Treatment-Plan/tests/test_tp_bn_caller_policy.py` | BN caller policy. |

### Diagnosis (clinician authority)

| File | Constraint |
| --- | --- |
| `Modules/Diagnosis-1.2.0/diagnosis/criteria.py` | DSM-5-TR research paraphrase; **decision support only**; clinician-authority invariant. |
| `Modules/Diagnosis-1.2.0/diagnosis/diagnosis_api.py` | REST contract; clinician can assert even if checklist unmet (bypass path intentional). |
| `Modules/Diagnosis-1.2.0/diagnosis/contract.py` | Module contract. |
| `Modules/Diagnosis-1.2.0/diagnosis/deps.py` | Fail-closed dependencies. |
| `Modules/Diagnosis-1.2.0/diagnosis/patient.py` | Patient adapter; no inventing identity. |
| `Modules/Diagnosis-1.2.0/diagnosis/readiness.py` | Health must not echo URLs/paths/secrets. |
| `Modules/Diagnosis-1.2.0/diagnosis/config.py` | Frozen settings; single env snapshot. |
| `Modules/Diagnosis-1.2.0/HANDOFF.md` | **§6 Clinician-authority rule (do not violate)**; route-order invariants; CSRF; readiness MUST NOT raise or echo paths. |
| `Modules/Diagnosis-1.2.0/README.md` | Auth boundary; do-not-regress contract. |
| `Modules/Diagnosis-1.2.0/docs/api-contract.md` | API contract. |
| `Modules/Diagnosis-1.2.0/test_unittest.py` | Includes `TestClinicianAuthority`. |
| `Modules/Diagnosis-1.2.0/test_auth.py` / `test_csrf.py` / `test_readiness.py` | Gate tests. |

### Severity (clinical bands)

| File | Constraint |
| --- | --- |
| `Modules/Severity-1.1.0/severity-assessment.js` | Severity bands + clinician disclaimer narrative. |
| `Modules/Severity-1.1.0/HANDOFF.md` | **Do NOT silently change severity bands** (clinical meaning); no DELETE route unless required; do not touch `node_modules`. |
| `Modules/Severity-1.1.0/README.md` | Clinician-control disclaimer. |
| `Modules/Severity-1.1.0/server.js` / `security.js` / `readiness.js` | Auth and readiness boundaries. |

### DDI Checker (knowledge base + clinical interaction safety)

| File | Constraint |
| --- | --- |
| `HANDOFF_DDI-01.md` | Work packet: do not invent auth contracts; do not break cross-module consumer contract; do not stage graphify noise; clinical/schema decisions frozen. |
| `Modules/DDI-Checker-1.2.0/src/ddi-engine.js` | Authoritative DDI evaluation engine. |
| `Modules/DDI-Checker-1.2.0/src/kb-validator.cjs` | KB validation; activation blocked with zero approved interactions. |
| `Modules/DDI-Checker-1.2.0/src/kb-sqlite.cjs` | KB store identity. |
| `Modules/DDI-Checker-1.2.0/src/ddi-rest-adapter.cjs` | REST contract surface. |
| `Modules/DDI-Checker-1.2.0/src/auth-adapter.js` | Auth. |
| `Modules/DDI-Checker-1.2.0/data/active-kb.json` | Active knowledge base identity (do not casually rewrite). |
| `Modules/DDI-Checker-1.2.0/scripts/validate-kb.mjs` | KB validation script. |
| `Modules/DDI-Checker-1.2.0/scripts/ingest.mjs` | Deterministic ingestion / version identity. |
| `Modules/DDI-Checker-1.2.0/README.md` | Reproducible KB identity; activation blocked rules. |
| `Modules/DDI-Checker-1.2.0/graphs/architecture.md` | Architecture boundaries. |
| `Modules/DDI-Checker-1.2.0/test/ci-contract.test.mjs` | CI contract. |
| `Modules/DDI-Checker-1.2.0/test/ddi-rest-contract.test.mjs` | REST contract freeze. |
| `Modules/DDI-Checker-1.2.0/test/ddi-05-identity-evidence.test.mjs` | Identity/evidence rules. |
| `Modules/DDI-Checker-1.2.0/test/ddi-authoritative-engine.test.mjs` | Engine authority. |

### BN Manager (model governance + clinical safety wording)

| File | Constraint |
| --- | --- |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/UBIQUITOUS_LANGUAGE.md` | **Clinical Safety Boundary**: decision support only—not diagnosis/prescription/treatment order; module boundary. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/CONTEXT.md` | Registry path safety; no caller-controlled filesystem paths; contract freeze context. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/model_governance.py` | Clinical status (`unvalidated`/`approved`/`retired`); signed approvals fail closed without governance key; **validity ≠ clinical safety**; CPT broadcast limitations. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/model_registry.py` | Path-safe model registry (relative paths only). |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/contract.py` | Frozen contract types / decision IDs. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/validation.py` | Semantic validation; notes clinical safety not implied. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/main.py` | Role-protected routes; evaluation through frozen contract. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/evaluation_store.py` | Evaluation evidence constraints. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_contract.py` | Frozen decision IDs and module identity. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_bn_manager_backend.py` | Dimensional validity must not imply clinical safety. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_auth_adapter.py` | Disclaimer/forced-password sessions blocked. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/README.md` | Module boundary documentation. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/docs/XML-BN-MIGRATION.md` | Migration policy for network formats. |

### Medical History (PHI retention)

| File | Constraint |
| --- | --- |
| `Modules/Medical-History-1.0.0/retention.js` | Dual approval (`privacy_officer`, `clinical_safety_officer`) required for PHI retention/redaction. |
| `Modules/Medical-History-1.0.0/security.js` | CORS/CSRF/security. |
| `Modules/Medical-History-1.0.0/repository.js` | Persistence boundaries. |
| `Modules/Medical-History-1.0.0/medical-history-submission.js` | Submission validation. |
| `Modules/Medical-History-1.0.0/data/medical_history_schema.json` | Schema constraints. |
| `Modules/Medical-History-1.0.0/MEDICAL_HISTORY_HANDOFF.md` | Handoff constraints. |
| `Modules/Medical-History-1.0.0/README.md` | Encrypted volumes + dual-approval retention for production PHI. |
| `Modules/Medical-History-1.0.0/test/security.test.js` / `test/auth-adapter.test.js` | Security locks. |

### Add New Patient

| File | Constraint |
| --- | --- |
| `Modules/Add-New-Patient-1.1.0/add_new_patient_backend/main.py` | Auth/CSRF protected patient registration APIs. |
| `Modules/Add-New-Patient-1.1.0/add_new_patient_backend/models.py` | Domain validation. |
| `Modules/Add-New-Patient-1.1.0/schema/add-new-patient.schema.json` | Patient schema. |
| `Modules/Add-New-Patient-1.1.0/docs/api-contract.md` | API contract. |
| `Modules/Add-New-Patient-1.1.0/docs/patient-domain-glossary.md` | Domain vocabulary (do not invent terms). |
| `Modules/Add-New-Patient-1.1.0/docs/add-new-patient-handoff.md` / `handoff.md` | Handoff constraints. |
| `Modules/Add-New-Patient-1.1.0/DESIGN.md` | Design boundaries. |
| `Modules/Add-New-Patient-1.1.0/test_auth_adapter_contract.py` | Auth adapter contract. |

---

## 5. Module registration and discovery

Changing these without coordinated updates breaks registration, role access, or gateway routing.

| File | Constraint |
| --- | --- |
| `deployment/manifest.json` | Unified deployment module registry (ids, ports, paths, health). |
| `deployment/manifest.schema.json` | Manifest schema. |
| `Modules/*/module-config.json` | Per-module `dataDirectory` / `databasePath` (must stay inside module root; checked by architecture). |
| `Modules/Dashboard-1.2.0/dashboard_backend/config.py` | Runtime module registry validation for workspace buttons/roles. |
| `Modules/Dashboard-1.2.0/dashboard_backend/discovery.py` | Discovers registered module routes by role. |
| `Modules/Diagnosis-1.2.0/diagnosis/` dashboard discovery routes | Module-routes discovery for embed; order invariants in HANDOFF. |

---

## 6. Shared contracts that freeze integration shapes

Editing these without versioning and consumer updates is a policy violation.

| Path | Constraint |
| --- | --- |
| `contracts/package-policy.json` | Limits what may live in the contracts package. |
| `contracts/schemas/1.0.0/*.schema.json` | Common schemas (auth-session, audit-event, provenance, problem-details, identifiers, etc.). |
| `contracts/openapi/1.0.0/common.openapi.json` | Common OpenAPI. |
| `contracts/examples/1.0.0/*` | Canonical examples (auth denial, validation error, provenance, etc.). |
| `contracts/README.md` | Package usage rules. |
| `Modules/Authentication-1.1.0/contracts/**` | Auth-owned contract freeze. |
| `Modules/Treatment-Plan/contracts/**` | TP identifier/transport and OpenAPI freeze. |

---

## 7. Handoff and design docs that instruct agents not to change certain things

These are the primary **human/agent policy surfaces** (even when not enforced by a script).

| File | Notable “do not / must not” themes |
| --- | --- |
| `README.md` | Cross-module isolation; clinical safety checklist; TP blocked. |
| `HANDOFF_DDI-01.md` | Auth reuse; no fabricated clinical decisions; no graphify commits; packet order. |
| `Modules/Dashboard-1.2.0/HANDOFF.md` | Inviolable REST boundary; do not weaken auth; no PHI in URLs. |
| `Modules/Diagnosis-1.2.0/HANDOFF.md` | Clinician authority; settings singleton; readiness silence; route order. |
| `Modules/Severity-1.1.0/HANDOFF.md` | Severity bands clinical meaning; no silent threshold changes; no DELETE. |
| `Modules/Treatment-Plan/HANDOFF.md` | No invented approvals; no PHI in repo; release gate stays BLOCKED until real sign-off. |
| `Modules/Medical-History-1.0.0/MEDICAL_HISTORY_HANDOFF.md` | PHI retention and security posture. |
| `Modules/Add-New-Patient-1.1.0/handoff.md` / `docs/add-new-patient-handoff.md` | Patient domain and API constraints. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/UBIQUITOUS_LANGUAGE.md` | Clinical safety wording. |
| `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/CONTEXT.md` | Registry path safety and contract freeze. |
| `Modules/*/DESIGN.md` | Design-level non-negotiables (Auth, Add-New-Patient, etc.). |

---

## 8. Summary: highest-impact “do not casually change” targets

If an LLM is about to edit any of the following, treat it as **policy-sensitive** and require explicit human intent:

1. **Disclaimer / clinical claims** — `disclaimer_contract.py`, Dashboard disclaimer UI/API, root README clinical safety wording  
2. **Auth, CSRF, roles, session gates** — `security.py`, auth adapters, session schemas  
3. **Cross-module boundaries** — `scripts/check_architecture.py`, module handoffs  
4. **Clinical release status** — TP-01 scope matrix, `check_tp01_release_gate.py` (must stay BLOCKED without real approvals)  
5. **Safety / eligibility / finalization** — `safety_policy.py`, `eligibility.py`, finalization + immutable plan migrations  
6. **Clinician authority in Diagnosis** — `criteria.py`, HANDOFF §6, `TestClinicianAuthority`  
7. **Severity clinical bands** — Severity HANDOFF + scoring function  
8. **DDI KB identity / approval** — `active-kb.json`, validators, identity tests  
9. **BN model governance** — `model_governance.py`, frozen contract tests  
10. **PHI retention dual approval** — Treatment Plan `retention.py`, Medical History `retention.js`  
11. **Deployment hardening** — immutable digests, no host module ports, secrets, `verify_unified_deployment.py`  
12. **Shared contracts package policy** — `contracts/package-policy.json` + schema freeze  

---

## 9. What this inventory is *not*

- **Not** every file containing the word “security” or “health” (e.g. HTTP health endpoints alone).  
- **Not** generated `graphify-out/**` artifacts (non-authoritative).  
- **Not** `node_modules/**` or `.venv/**` third-party code.  
- **Not** ordinary application features without a policy/safety gate.

---

*Generated from a static scan of the INSIGHT repository for architecture gates, clinical governance, auth/disclaimer registration, PHI retention, frozen contracts, and handoff “do not change” rules.*
