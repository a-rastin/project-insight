# INSIGHT Treatment Plan Handoff

## Objective

Continue implementing the dependency-ordered Treatment Plan module while preserving standalone execution, REST-only module integration, schema-versioned data, immutable final plans, and fail-closed clinical safety gates.

## Source of Truth

- **Project Plan:** The authoritative plan and issue order are in an external planning document.
- **Module Documentation:** `README.md` in this repository.
- **Ownership Contract:** `CONTEXT-MAP.md`.
- **Governance Process:** `governance/TP-01-SCOPE-AND-RELEASE-GATES.md`.

Do not duplicate these documents; update or reference the authoritative files.

## Completed Work

This section provides a detailed history of the "Treatment Plan" (TP) development milestones.

- **TP-01 to TP-03:** Established foundational governance, architecture, and shared interface contracts.
- **TP-04:** Created a disposable, pure-reducer lifecycle prototype for demonstrating the plan lifecycle.
- **TP-05:** Published version `1.0.0` of all data contracts (JSON Schemas, OpenAPI).
- **TP-06:** Built the standalone application scaffold (FastAPI, React, repository pattern, Docker).
- **TP-07:** Integrated security with the central Authentication module.
- **TP-08:** Implemented the clinical context assembler for gathering data from upstream services.
- **TP-09:** Created the data quality and generation eligibility policy engine.
- **TP-10:** Implemented orchestration for Bayesian Network (BN) model evaluations.
- **TP-11:** Implemented the deterministic clinical safety policy engine.
- **TP-12:** Implemented deterministic Primary Plan synthesis from all inputs.
- **TP-13:** Implemented the Drug-Drug Interaction (DDI) check for proposed medications.
- **TP-14:** Developed the psychiatrist review workspace UI in React, following accessibility and design standards.
- **TP-15:** Built the append-only, attributable plan edit ledger with atomic concurrency control and authenticated routes.
- **TP-16:** Implemented fresh safety re-computation on finalization to ensure the latest data is used.
- **TP-17:** Hardened the finalization process with idempotency, server-owned context, exact source provenance, attributable overrides, and immutable database records.
- **TP-18:** Implemented the follow-up supersession seam (`PlanSuperseder`) that gathers a fresh snapshot, revalidates and explains every Primary Plan section, and records an immutable successor relationship without rewriting the signed prior Final Plan. A migration stores the immutable link.
- **TP-19:** Built the dialect-aware persistence layer: a single reversible migration set rendered for SQLite and PostgreSQL, `MigrationRunner`, SQLite `backup`/`restore` with integrity checks, `PostgreSQLRepository`, and approval-gated `RetentionPolicy` that redacts expired PHI while preserving the immutable edit ledger and clinical provenance.
- A detailed module `README.md` is available.

## Current State and Critical Constraint

The repository contains a robust architectural baseline and a functional application, but it is not yet cleared for production.

- **Clinical Release Blocked:** The `check_tp01_release_gate.py` script intentionally returns `BLOCKED`. This gate will only pass when all required clinical, regulatory, and privacy stakeholders provide sign-off. Do not invent stakeholder names or approvals.
- **Prototype Status:** The lifecycle prototype in `prototype/` is a throwaway research tool for discussion and should not be promoted to production code.
- **`graphify-out/` is generated:** It contains auto-generated knowledge graph artifacts from the `graphify` skill and is not authoritative documentation; treat it as a build artifact.
- **Persistence Fraud Controls:** TP-19 migrations enforce UUID, idempotency-key, foreign-key, and JSON-envelope constraints, plus SQLite triggers that abort any `UPDATE`/`DELETE` on `finalized_plans` and `plan_supersessions` (records stay immutable at the DB level). PostgreSQL achieves the same through table-level privileges and triggers.
- **Ownership:** Entity ownership is strictly partitioned. For example, the Diagnosis module owns diagnosis assessments. Treatment Plan owns the normalized snapshots and the final plan, but not the source data itself.

## Verification

From the root of the repository:

```powershell
# Run backend tests
.\test.ps1

# Run frontend tests
cd .\frontend
npm test
cd ..

# Run governance and contract checks
python .\scripts\check_context_ownership.py
python .\scripts\check_identifier_contract.py
python .\scripts\check_tp05_contracts.py
python .\scripts\check_tp01_release_gate.py

# Run the lifecycle prototype (for demonstration)
python .\prototype\run_lifecycle.py
```

All automated test suites and validation scripts should pass, with the exception of `check_tp01_release_gate.py`, which correctly reports `BLOCKED`.

`test_tp19_persistence.py` also runs the PostgreSQL repository contract test when `TP_TEST_POSTGRES_DSN` is set; otherwise that case is skipped.

## Recommended Next Work

1.  **Connect Frontend to Backend:** The highest priority is to connect the React components in the TP-14 review workspace to the authenticated backend APIs for reading and editing plans (TP-15) and finalization (TP-17).
2.  **Psychiatrist Walkthrough:** Run the `prototype\run_lifecycle.py` script with a psychiatrist to get feedback. Capture the outcome in `governance/ADR-TP-04-DISPOSABLE-LIFECYCLE-PROTOTYPE.md`. Adjust the prototype based on feedback.
3.  **Wire Remaining API Routes:** The OpenAPI contract in `contracts/openapi/` defines routes that are not yet wired in `treatment_plan/app.py`, including `POST /recommendation-runs` (start of the recommendation run), `GET /recommendation-runs/{runId}` (status), and `POST /plans/{planId}/supersede` (connect to `PlanSuperseder`). Implement these against their existing seams (`ClinicalContextAssembler`, `BnEvaluationOrchestrator`, `PrimaryPlanSynthesizer`, `DdiMedicationChecker`, `PlanSuperseder`).
4.  **Delete Prototype:** After the psychiatrist walkthrough is complete and findings are recorded, the `prototype/` directory should be deleted.

## Technical Seams

The following sections describe the key technical interfaces ("seams") in the application. Adhering to these seams is critical for maintaining the modular architecture.

- **TP-06 Runtime Seam:** The persistence layer is abstracted via `treatment_plan.repository.Repository`.
- **TP-08 Clinical Context Seam:** Data gathering is centralized in `ClinicalContextAssembler`. Adapters are private and use REST only.
- **TP-05 Contract Seam:** The external REST interface is defined by the OpenAPI spec and JSON Schemas in `contracts/`.
- **TP-07 Security Seam:** Authorization is handled exclusively by `treatment_plan.security.Security`.
- **TP-09 Eligibility Seam:** The `GenerationEligibilityPolicy` provides a single interface for eligibility checks.
- **TP-10 BN Evaluation Seam:** Orchestration is handled by `BnEvaluationOrchestrator`; canonical immutable bundles persist via `RepositoryBnEvaluationStore`.
- **TP-11 Safety Policy Seam:** The `SafetyPolicy` provides the single interface for deterministic safety checks.
- **TP-12 Synthesis Seam:** `PrimaryPlanSynthesizer` is the pure interface for plan generation.
- **TP-13 DDI Seam:** `DdiMedicationChecker` is the single interface for DDI checks.
- **TP-14 UI Seam:** The `review-workspace.ts` module is the state management core for the React UI.
- **TP-15 Edit Ledger Seam:** `PlanEditLedger` is the sole interface for registering and editing plans.
- **TP-16 Finalization Seam:** `PlanFinalizer` is the single interface for the multi-step finalization process.
- **TP-18 Supersession Seam:** `PlanSuperseder` is the sole interface for follow-up supersession; it collaborates with a `FollowUpSnapshotProvider` and a `SuccessorPlanGenerator` and stores the immutable link through `PlanEditLedger`.
- **TP-19 Persistence Seam:** `MigrationRunner` renders the single ordered, reversible migration set for both SQLite and PostgreSQL; `SQLiteRepository` and `PostgreSQLRepository` implement the `Repository` Protocol, and `RetentionPolicy` is the single interface for approval-gated PHI redaction.
- **MH-04 Suicide-Risk Observation Seam:** `treatment_plan.suicide_risk_observations` is the sole interface for resolving Add New Patient and Medical History suicide-risk observations. Observations are source/time-stamped (`SuicideRiskObservation`), each module's own vocabulary is preserved verbatim (no fabricated cross-vocabulary mapping), and `SuicideRiskResolution` applies the approved resolution policy: disagreement (`CONTRADICT`), single-source signal (`SOLE_SOURCE`), and corroborated signal (`AGREE` on a non-default token) all route to the explicit safety pathway so neither module silently wins. `GenerationEligibilityPolicy._apply_suicide_risk_observations` is the only caller.

## Open MH-04 follow-up (clinical/schema decision required, not fabricated)

This packet adds the resolution policy and the observation seam; the two observation sources are read from the existing context inputs `riskFlags.suicidality` (Add New Patient) and `substantialSuicideRisk` (Medical History). Wiring the production cross-module REST path requires an approved downstream decision and is deliberately out of scope for MH-04:

- The TP-08 `_PatientAdapter` URL `/api/add-new-patient/v1/patients/{patientId}/encounters/{encounterId}` and the `_MedicalHistoryAdapter` URL `/api/medical-history/v1/patients/{patientId}/encounters/{encounterId}/latest` are *not yet implemented* by their owning modules. ANP currently exposes `GET /api/add-new-patient/v1/encounters/{encounterId}` (no patient/encounter combined route, and the response omits `observedAt`/`patientId`/`encounterId`/`resourceId` that TP's envelope validator requires). Medical History exposes `GET /api/internal/medical-history/submissions/latest?patientId=...&encounterId=...` whose payload omits `observedAt` and the `schemaVersion=1.0.0`/`patientId`/`encounterId` envelope TP validates.
- AGREE-with-signal is currently only reachable when both modules emit the *same normalized token*; with the real vocabularies (ANP `ideation`/`plan`/`attempt`; MH `substantial`/`none`) the observed happy case is AGREE-on-`none` (both default), and any joint signal resolves to `CONTRADICT` (the policy refuses to map MH's boolean into ANP's clinician-graded states without an approved clinical mapping). Records use the source's own token; no clinical threshold is invented here. Whenever ANP and MH both signal risk with differing tokens, the pathway still routes to safety review through the `CONTRADICT` finding because the rule is conservative. A future packet that introduces an approved cross-vocabulary mapping (e.g. `ideation/plan/attempt → substantial`) must be backed by a controlled clinical decision recorded in governance before it is merged.

## Sensitive-Data Note

Do not place patient information, credentials, API keys, signatures, or protected meeting records in source control. Governance files should reference authoritative controlled evidence rather than embedding it.
