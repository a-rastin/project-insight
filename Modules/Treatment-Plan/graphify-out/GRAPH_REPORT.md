# Graph Report - .  (2026-07-27)

## Corpus Check
- 51 files · ~74,852 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1816 nodes · 4231 edges · 106 communities (84 shown, 22 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 698 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103

## God Nodes (most connected - your core abstractions)
1. `DdiMedicationChecker` - 69 edges
2. `PlanEditLedger` - 60 edges
3. `SQLiteRepository` - 52 edges
4. `PlanFinalizer` - 50 edges
5. `Settings` - 44 edges
6. `Medication` - 42 edges
7. `InMemoryPlanEditStore` - 40 edges
8. `SQLitePlanEditStore` - 40 edges
9. `BnModel` - 39 edges
10. `create_app()` - 35 edges

## Surprising Connections (you probably didn't know these)
- `PrimaryTreatmentPlan (treatment_plan/primary_plan.py)` --semantically_similar_to--> `PrimaryPlanSynthesizer (TP-12 seam)`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260714_163112_tp_14___build_psychiatrist_review_and_structured_e.md → HANDOFF.md
- `DdiCheckResult (treatment_plan/ddi_check.py)` --semantically_similar_to--> `DdiMedicationChecker (TP-13 seam)`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260714_163112_tp_14___build_psychiatrist_review_and_structured_e.md → HANDOFF.md
- `PlanEdit (treatment-plan schema)` --semantically_similar_to--> `PlanEditLedger (TP-15 seam)`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260714_163112_tp_14___build_psychiatrist_review_and_structured_e.md → HANDOFF.md
- `deployment/compose.unified.yaml (unified-image topology fragment)` --semantically_similar_to--> `compose.release.yaml (hardened release compose)`  [INFERRED] [semantically similar]
  deployment/compose.unified.yaml → compose.release.yaml
- `ScaffoldTests` --uses--> `Settings`  [INFERRED]
  tests/test_tp06_scaffold.py → treatment_plan/config.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **TP clinical safety gate chain (finalization immutability + image-only rollback)** — _handoff_concept_immutable_finalized_plans, _deployment_rollback_rationale_image_only_rollback, _handoff_concept_plan_finalizer [INFERRED 0.85]
- **TP-10 BN evidence mapping model set** — governance_tp_10_bn_mapping_coverage_model_treatment_setting, governance_tp_10_bn_mapping_coverage_model_pharmacotherapy, governance_tp_10_bn_mapping_coverage_model_involuntary_treatment, governance_tp_10_bn_mapping_coverage_model_clozapine_suicide_risk [EXTRACTED 1.00]
- **TP-14 review workspace minimal implementation surface (primary plan + recommendation + DDI + edit) consumed by React UI** — graphify_out_memory_query_20260714_163112_tp_14_concept_primary_treatment_plan, graphify_out_memory_query_20260714_163112_tp_14_concept_plan_recommendation, graphify_out_memory_query_20260714_163112_tp_14_concept_ddi_check_result, graphify_out_memory_query_20260714_163112_tp_14_concept_plan_edit, _handoff_concept_review_workspace [INFERRED 0.85]
- **Repository Protocol implementees** — readme_repository_protocol, readme_sqliterepository, readme_postgresqlrepository [EXTRACTED 0.95]
- **INSIGHT entity ownership model** — context_map_patient, context_map_encounter, context_map_assessment, context_map_medication_knowledge, context_map_recommendation, context_map_final_plan [EXTRACTED 1.00]

## Communities (106 total, 22 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (62): FailingDdiPort, TP13CheckerFailureTests, BlockingPort, command(), context(), primary_plan(), RecordingPort, TP16FinalizationTests (+54 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (61): AssessedRecommendation, SafetyPolicy, SafetyPolicyDecision, FakeEvaluator, TP10BnEvaluationTests, bundle(), evaluation(), facts() (+53 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (30): Collection, Dialect, PermissionError, RepositoryContractTests, RetentionPolicyTests, TP19BackupTests, TP19MigrationTests, Migration (+22 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (39): HTTPX, requirements.txt, TP11SafetyPolicyTests, primary_plan(), RecordingDdiPort, TP13DdiCheckTests, no_interaction_response(), TP13MedicationSetBindingTests (+31 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (29): _apply_pointer(), _canonical_json(), _editable_tokens(), EditLedgerError, _encode_token(), _etag(), _finding_for_pointer(), _has_active_urgent_recommendation() (+21 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (61): minLength, type, $ref, additionalProperties, properties, type, $ref, $ref (+53 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (33): ConcurrentSnapshotProvider, final_plan(), finalized_ledger(), follow_up_delta(), Generator, hash_json(), prior_primary_plan(), snapshot() (+25 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (39): CompletedProcess, RuntimeError, build(), clinical_release_gates(), image_digest(), immutable_image_reference(), main(), Path (+31 more)

### Community 8 - "Community 8"
Cohesion: 0.12
Nodes (33): evaluate_payloads(), _evidence_tests(), _items(), main(), Any, Fail-closed TP-21 clinical validation and safety-case gate., StrEnum, cases() (+25 more)

### Community 9 - "Community 9"
Cohesion: 0.04
Nodes (47): approvals, clinicalScope, appointmentPolicy, emergencyBehavior, planBreadth, supportedDiagnoses, supportedPopulation, clinicalValidation (+39 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (47): required, required, required, enum, required, required, required, required (+39 more)

### Community 11 - "Community 11"
Cohesion: 0.09
Nodes (19): Logger, LogRecord, TP20ObservabilityTests, configure_logging(), JsonFormatter, Any, _safe_fields(), AuditEvent (+11 more)

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (23): _observation(), MH-04: separate source/time-stamped suicide-risk observations and an approved re, SuicideRiskObservationTests, SuicideRiskResolutionPolicyTests, Dependency, Blocker, Eligibility, Enum (+15 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (22): Exception, _BnAdapter, _Circuit, ClinicalContextAssembler, _DdiAdapter, DependencyResult, _DiagnosisAdapter, _is_string() (+14 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (33): dependencies, react, react-dom, typescript, vite, @vitejs/plugin-react, vitest, devDependencies (+25 more)

### Community 15 - "Community 15"
Cohesion: 0.06
Nodes (33): minLength, type, $ref, additionalProperties, properties, type, $ref, AuditProvenance (+25 more)

### Community 16 - "Community 16"
Cohesion: 0.10
Nodes (28): items, items, type, items, type, additionalProperties, minLength, properties (+20 more)

### Community 17 - "Community 17"
Cohesion: 0.07
Nodes (28): PlanContent, pattern, type, additionalProperties, properties, required, type, additionalProperties (+20 more)

### Community 18 - "Community 18"
Cohesion: 0.17
Nodes (15): context(), TP09EligibilityPolicyTests, ClinicalContext, ContextError, ContextErrorCode, Enum, str, EligibilityDecision (+7 more)

### Community 19 - "Community 19"
Cohesion: 0.15
Nodes (14): FastAPI, Repository, bn_manager_client_factory(), CallerAdapterContractTests, BN-05 — Treatment Plan caller policy.  Asserts the caller-aware BN Manager adapt, RegistryEvidenceSchemaMappingTests, create_app(), BnManagerTreatmentPlanEvaluator (+6 more)

### Community 20 - "Community 20"
Cohesion: 0.08
Nodes (24): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+16 more)

### Community 21 - "Community 21"
Cohesion: 0.08
Nodes (25): type, type, minLength, type, type, type, type, properties (+17 more)

### Community 22 - "Community 22"
Cohesion: 0.18
Nodes (10): SecurityTests, AccessDenied, AuthenticationPort, AuthenticationUnavailable, Capability, datetime, Enum, Protocol (+2 more)

### Community 23 - "Community 23"
Cohesion: 0.08
Nodes (24): enum, type, $ref, $ref, minLength, type, $ref, minLength (+16 more)

### Community 24 - "Community 24"
Cohesion: 0.09
Nodes (23): PlanEdit, $ref, $ref, enum, type, pattern, type, additionalProperties (+15 more)

### Community 25 - "Community 25"
Cohesion: 0.21
Nodes (14): check_compatibility(), ContractError, lint_openapi(), load(), _pointer(), Path, ValueError, Offline TP-05 JSON Schema, example, compatibility, and OpenAPI conformance. (+6 more)

### Community 26 - "Community 26"
Cohesion: 0.15
Nodes (6): ScaffoldTests, _bool(), ConfigurationError, ValueError, main(), InMemoryRepository

### Community 27 - "Community 27"
Cohesion: 0.09
Nodes (22): minLength, type, minLength, type, instrument, interpretation, score, severity (+14 more)

### Community 28 - "Community 28"
Cohesion: 0.17
Nodes (18): App(), reviewCase, clonePlan(), compare(), Comparison, createReviewWorkspace(), Dose, fields (+10 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (11): main(), Run: python prototype/run_lifecycle.py (synthetic walkthrough only)., initial_state(), ValueError, THROWAWAY TP-04 lifecycle prototype. Not for clinical use or production import., Return a new state for one action; never mutate ``state``., reduce(), _require() (+3 more)

### Community 30 - "Community 30"
Cohesion: 0.11
Nodes (20): items, minLength, type, items, pattern, properties, type, minLength (+12 more)

### Community 31 - "Community 31"
Cohesion: 0.11
Nodes (19): compose.release.yaml (hardened release compose), read_only + no-new-privileges + cap_drop ALL hardening, deployment/compose.unified.yaml (unified-image topology fragment), authentication-session-url secret mount (TP-07 integration), Treatment Plan rollback procedure, Image-only rollback; never auto down-migrate immutable clinical records, INSIGHT Treatment Plan Handoff, BnEvaluationOrchestrator (TP-10 seam) (+11 more)

### Community 32 - "Community 32"
Cohesion: 0.11
Nodes (19): status, const, enum, minimum, type, acknowledged, confirmed, editing (+11 more)

### Community 33 - "Community 33"
Cohesion: 0.20
Nodes (7): RetentionPolicy, RetentionResult, RuntimeRecord, Connection, datetime, Path, SQLiteRepository

### Community 34 - "Community 34"
Cohesion: 0.12
Nodes (17): pattern, type, SourceReference, minLength, type, type, contentHash, etag (+9 more)

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (15): $defs, Instant, ProblemDetails, Uuid, Version, $id, format, type (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.14
Nodes (16): required, required, required, action, actorId, code, codeSystem, correlationId (+8 more)

### Community 37 - "Community 37"
Cohesion: 0.30
Nodes (10): EditLedgerRouteTests, EditLedgerTests, ledger(), primary_plan(), EditCategory, PolicyBound, str, A trusted policy constraint for one exact JSON Pointer. (+2 more)

### Community 38 - "Community 38"
Cohesion: 0.13
Nodes (15): items, type, uniqueItems, items, type, uniqueItems, additionalProperties, properties (+7 more)

### Community 39 - "Community 39"
Cohesion: 0.13
Nodes (15): minItems, type, FollowUpDelta, $ref, additionalProperties, properties, type, $ref (+7 more)

### Community 40 - "Community 40"
Cohesion: 0.16
Nodes (14): Add New Patient module, Assessment entity, Authentication module, BN Manager module, DDI Checker module, Diagnosis module, Encounter entity, Final Plan entity (+6 more)

### Community 41 - "Community 41"
Cohesion: 0.15
Nodes (13): minLength, pattern, type, enum, type, additionalProperties, properties, type (+5 more)

### Community 42 - "Community 42"
Cohesion: 0.15
Nodes (13): schemaVersion, required, approvals, clinicalScope, clinicalValidation, clinicalWorkflow, decisionGates, documentId (+5 more)

### Community 43 - "Community 43"
Cohesion: 0.17
Nodes (12): format, type, format, type, properties, correlationId, id, recorded (+4 more)

### Community 44 - "Community 44"
Cohesion: 0.17
Nodes (12): type, type, approvals, clinicalValidation, maxItems, minItems, owners, regulatoryAssessment (+4 more)

### Community 45 - "Community 45"
Cohesion: 0.18
Nodes (12): Clinical Context Assembly, CONTEXT-MAP.md, FastAPI backend, Idempotent Finalization, MigrationRunner, PostgreSQLRepository, React review workspace, Repository Protocol (+4 more)

### Community 47 - "Community 47"
Cohesion: 0.18
Nodes (11): required, id, status, behavior, case, decision, name, role (+3 more)

### Community 49 - "Community 49"
Cohesion: 0.20
Nodes (10): DdiMedicationChecker (TP-13 seam), PlanEditLedger (TP-15 seam), PlanSuperseder (TP-18 seam), PrimaryPlanSynthesizer (TP-12 seam), review-workspace.ts state core (TP-14 UI seam), graphify query: TP-14 Build psychiatrist review and structured editing UI, DdiCheckResult (treatment_plan/ddi_check.py), PlanEdit (treatment-plan schema) (+2 more)

### Community 50 - "Community 50"
Cohesion: 0.20
Nodes (10): additionalProperties, properties, required, type, agent, who, additionalProperties, properties (+2 more)

### Community 52 - "Community 52"
Cohesion: 0.22
Nodes (9): SafetyFinding, additionalProperties, required, type, category, detectedAt, findingId, severity (+1 more)

### Community 54 - "Community 54"
Cohesion: 0.25
Nodes (8): ClinicalContextAssembler (TP-08 seam), MigrationRunner reversible migrations (TP-19 seam), requirements.txt (Python runtime deps), fastapi>=0.115,<1, httpx>=0.27,<1, psycopg[binary]>=3.2,<4 (PostgreSQLRepository driver), pydantic>=2.10,<3, uvicorn[standard]>=0.30,<1

### Community 55 - "Community 55"
Cohesion: 0.25
Nodes (8): items, type, additionalProperties, properties, required, type, entity, what

### Community 56 - "Community 56"
Cohesion: 0.39
Nodes (8): required, role, enum, clinicalSafetyOfficer, privacy, product, psychiatrist, regulatory

### Community 57 - "Community 57"
Cohesion: 0.29
Nodes (7): action, correlationId, id, required, outcome, recorded, resourceType

### Community 58 - "Community 58"
Cohesion: 0.29
Nodes (7): what, additionalProperties, properties, required, type, required, identifier

### Community 59 - "Community 59"
Cohesion: 0.33
Nodes (6): encounterId UUID, Idempotency-Key, TP-03 identifier contract, patientCode alias, patientId UUID, Schema versioning contract

### Community 60 - "Community 60"
Cohesion: 0.33
Nodes (6): additionalProperties, properties, required, type, identifier, value

### Community 62 - "Community 62"
Cohesion: 0.40
Nodes (5): Clinical Decision Support, INSIGHT Logo, Neural Network Graph Visual, Open Door / Gateway Visual, Schizophrenia Care

### Community 63 - "Community 63"
Cohesion: 0.40
Nodes (4): additionalProperties, $id, $schema, type

### Community 64 - "Community 64"
Cohesion: 0.40
Nodes (5): enum, outcome, denied, failure, success

### Community 65 - "Community 65"
Cohesion: 0.40
Nodes (4): $id, $schema, title, type

### Community 66 - "Community 66"
Cohesion: 0.40
Nodes (5): enum, behavior, informational_only, reject_generation, safety_escalation

### Community 68 - "Community 68"
Cohesion: 0.50
Nodes (4): CONTEXT-MAP, Entity ownership rule, Prohibited cross-module coupling, Sole ownership rule

### Community 69 - "Community 69"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 70 - "Community 70"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 71 - "Community 71"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 72 - "Community 72"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 73 - "Community 73"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 74 - "Community 74"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 75 - "Community 75"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 76 - "Community 76"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 77 - "Community 77"
Cohesion: 0.50
Nodes (3): $id, $ref, $schema

### Community 78 - "Community 78"
Cohesion: 0.50
Nodes (4): type, decision, null, string

### Community 79 - "Community 79"
Cohesion: 0.67
Nodes (3): evaluate(), main(), Validate unique ownership and REST-only cross-module relationship rules.

### Community 80 - "Community 80"
Cohesion: 0.67
Nodes (3): evaluate(), main(), Validate the shared TP-03 identifier and transport contract.

### Community 81 - "Community 81"
Cohesion: 0.67
Nodes (3): evaluate(), main(), Fail-closed TP-01 clinical release gate. Uses only the Python standard library.

### Community 82 - "Community 82"
Cohesion: 0.67
Nodes (3): ANP vs Medical-History suicide-risk vocabulary mismatch (no fabricated mapping), GenerationEligibilityPolicy (TP-09 seam), SuicideRiskResolution MH-04 seam (CONTRADICT/SOLE_SOURCE/AGREE)

### Community 83 - "Community 83"
Cohesion: 0.67
Nodes (3): pattern, type, action

### Community 84 - "Community 84"
Cohesion: 0.67
Nodes (3): ADR TP-04 disposable lifecycle prototype, ADR TP-04 disposable reduce(state,action) reducer, ADR TP-04 psychiatrist agreement pending

### Community 85 - "Community 85"
Cohesion: 0.67
Nodes (3): signedAt, format, type

### Community 86 - "Community 86"
Cohesion: 0.67
Nodes (3): TP-01 scope and release gates, TP-01 clinical release BLOCKED, TP-01 eight decision gates

## Knowledge Gaps
- **497 isolated node(s):** `$schema`, `$id`, `type`, `additionalProperties`, `resourceType` (+492 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SQLiteRepository` connect `Community 33` to `Community 0`, `Community 2`, `Community 37`, `Community 6`, `Community 7`, `Community 19`, `Community 26`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `current_observability()` connect `Community 13` to `Community 0`, `Community 1`, `Community 4`, `Community 11`, `Community 12`, `Community 18`, `Community 22`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `BnModel` connect `Community 1` to `Community 0`, `Community 19`, `Community 53`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `DdiMedicationChecker` (e.g. with `RecordingDdiPort` and `TP13DdiCheckTests`) actually correct?**
  _`DdiMedicationChecker` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `PlanEditLedger` (e.g. with `EditLedgerRouteTests` and `EditLedgerTests`) actually correct?**
  _`PlanEditLedger` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `SQLiteRepository` (e.g. with `ScaffoldTests` and `EditLedgerRouteTests`) actually correct?**
  _`SQLiteRepository` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `PlanFinalizer` (e.g. with `BlockingPort` and `RecordingPort`) actually correct?**
  _`PlanFinalizer` has 16 INFERRED edges - model-reasoned connections that need verification._