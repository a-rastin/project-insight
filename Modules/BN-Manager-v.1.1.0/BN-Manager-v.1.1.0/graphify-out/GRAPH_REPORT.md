# Graph Report - .  (2026-07-27)

## Corpus Check
- 16 files · ~13,571 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 385 nodes · 1089 edges · 14 communities (11 shown, 3 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 132 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Authentication and CSRF
- Model Governance and Approvals
- Evaluation Store and Records
- Graph Evaluation Core
- Model Registry and Schema
- Contract and Response Envelope
- README Domain Concepts
- Backend Integration Tests
- Semantic Validation Tests
- XML Migration Architecture
- Evidence Schema and Validation
- Ubiquitous Language
- Package Metadata
- Protocol

## God Nodes (most connected - your core abstractions)
1. `ClinicalGraphModel` - 33 edges
2. `SignedApproval` - 33 edges
3. `BnManagerBackendTests` - 31 edges
4. `create_app()` - 30 edges
5. `Node` - 25 edges
6. `InMemoryEvaluationStore` - 25 edges
7. `ClinicalStatus` - 25 edges
8. `ValidationMessage` - 24 edges
9. `BnManagerHttpError` - 24 edges
10. `SessionState` - 22 edges

## Surprising Connections (you probably didn't know these)
- `ValidateModelTests` --uses--> `ClinicalGraphModel`  [INFERRED]
  tests/test_validation.py → clinical_graph_models/model.py
- `BnManagerBackendTests` --uses--> `SessionState`  [INFERRED]
  tests/test_bn_manager_backend.py → bn_manager_backend/auth_adapter.py
- `AuthenticationGuardTests` --uses--> `InMemoryEvaluationStore`  [INFERRED]
  tests/test_auth_adapter.py → bn_manager_backend/evaluation_store.py
- `FakeSessionAdapter` --uses--> `InMemoryEvaluationStore`  [INFERRED]
  tests/test_auth_adapter.py → bn_manager_backend/evaluation_store.py
- `AdminSessionAdapter` --uses--> `InMemoryEvaluationStore`  [INFERRED]
  tests/test_bn_manager_backend.py → bn_manager_backend/evaluation_store.py

## Import Cycles
- None detected.

## Communities (14 total, 3 thin omitted)

### Community 0 - "Authentication and CSRF"
Cohesion: 0.07
Nodes (38): assert_csrf_token(), AuthenticationRestAdapter, CsrfError, Any, Exception, Protocol, Request, session_from_payload() (+30 more)

### Community 1 - "Model Governance and Approvals"
Cohesion: 0.07
Nodes (33): _approval_from_json(), _canonical_payload(), clinical_status_for(), ClinicalStatus, InMemoryGovernanceStore, MissingGovernanceKey, ModelGovernanceStore, ModelNotApproved (+25 more)

### Community 2 - "Evaluation Store and Records"
Cohesion: 0.10
Nodes (27): build_canonical_evaluation(), CanonicalEvaluationRecord, compute_binding_hash(), _dump(), EvaluationStore, IdempotencyConflict, InMemoryEvaluationStore, _jsonable() (+19 more)

### Community 3 - "Graph Evaluation Core"
Cohesion: 0.16
Nodes (29): _enumerate_chance_assignments(), evaluate_expected_utilities(), evaluate_posterior(), EvaluationResult, _evidence_weight(), ClinicalGraphModel, Node, Potential (+21 more)

### Community 4 - "Model Registry and Schema"
Cohesion: 0.15
Nodes (22): list_registry_entries(), Path, read_owned_registry_file(), read_registry_model(), read_registry_schema(), resolve_owned_registry_file(), _compile_definition(), _compile_variable() (+14 more)

### Community 5 - "Contract and Response Envelope"
Cohesion: 0.13
Nodes (10): contract_payload(), error_response(), _governance_permission_paths(), _meta(), ok_response(), Any, RouteContract, TargetNodeContract (+2 more)

### Community 6 - "README Domain Concepts"
Cohesion: 0.11
Nodes (21): Authentication, BIF 0.3 XML Schema, BN Manager, bnm.clozapine-suicide-risk, bnm.involuntary-treatment-considerations, bnm.pharmacotherapy, bnm.treatment-setting, ClinicalGraphModel (+13 more)

### Community 8 - "Semantic Validation Tests"
Cohesion: 0.37
Nodes (3): _make_node(), _make_potential(), ValidateModelTests

### Community 9 - "XML Migration Architecture"
Cohesion: 0.20
Nodes (11): BN Manager XML Status UI, BN Manager Contract 2.0.0, Compact CPT Broadcast, Module Registry File-Loading Boundary, XML-Only Clinical BN Boundary, Legacy Workflow Removal, XML Bayesian Network Migration, Canonical XML BN (+3 more)

### Community 10 - "Evidence Schema and Validation"
Cohesion: 0.42
Nodes (8): build_evidence_schema(), _evidence_node_payload(), _is_required(), Any, ClinicalGraphModel, Expose allowed evidence nodes/states, required/optional membership, target, vers, _semantic_meaning(), Node

### Community 11 - "Ubiquitous Language"
Cohesion: 0.67
Nodes (3): Clinical Safety Boundary, Posterior Evaluation, Chance Target Node

## Knowledge Gaps
- **16 isolated node(s):** `Registry Entry`, `Chance Target Node`, `Structural Validation`, `clinical-graph-models`, `BIF 0.3 XML Schema` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `Authentication and CSRF` to `Model Governance and Approvals`, `Evaluation Store and Records`, `Model Registry and Schema`, `Contract and Response Envelope`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `BnManagerBackendTests` connect `Backend Integration Tests` to `Authentication and CSRF`, `Model Governance and Approvals`, `Evaluation Store and Records`, `Model Registry and Schema`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `SignedApproval` connect `Model Governance and Approvals` to `Authentication and CSRF`, `Evidence Schema and Validation`, `Backend Integration Tests`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `ClinicalGraphModel` (e.g. with `EvaluationResult` and `XmlBifCompileError`) actually correct?**
  _`ClinicalGraphModel` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `SignedApproval` (e.g. with `BnManagerHttpError` and `AdminSessionAdapter`) actually correct?**
  _`SignedApproval` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `BnManagerBackendTests` (e.g. with `SessionState` and `InMemoryEvaluationStore`) actually correct?**
  _`BnManagerBackendTests` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `create_app()` (e.g. with `BnManagerHttpError` and `contract_payload()`) actually correct?**
  _`create_app()` has 2 INFERRED edges - model-reasoned connections that need verification._