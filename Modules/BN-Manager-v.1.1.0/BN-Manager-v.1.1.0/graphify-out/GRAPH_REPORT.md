# Graph Report - BN-Manager-v.1.1.0  (2026-07-22)

## Corpus Check
- 25 files · ~8,178 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 228 nodes · 628 edges · 13 communities (8 shown, 5 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b82b9358`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluation and Graph Model
- XML Compiler and Schema
- FastAPI Model Operations
- Authentication and CSRF
- Semantic Validation Tests
- Contract and Response Envelope
- Registry and API Tests
- XML Migration Architecture
- Authentication Integration Tests
- Configuration and Server
- Package Metadata
- Clozapine Suicide Risk Network
- Pharmacotherapy Network

## God Nodes (most connected - your core abstractions)
1. `ClinicalGraphModel` - 36 edges
2. `Node` - 25 edges
3. `ValidationMessage` - 24 edges
4. `compile_xmlbif()` - 24 edges
5. `create_app()` - 21 edges
6. `ValidateModelTests` - 21 edges
7. `validate_model()` - 20 edges
8. `XmlBifCompileError` - 20 edges
9. `SessionState` - 17 edges
10. `_make_node()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `AuthenticationGuardTests` --uses--> `SessionState`  [INFERRED]
  tests/test_auth_adapter.py → bn_manager_backend/auth_adapter.py
- `AdminSessionAdapter` --uses--> `SessionState`  [INFERRED]
  tests/test_bn_manager_backend.py → bn_manager_backend/auth_adapter.py
- `BnManagerBackendTests` --uses--> `SessionState`  [INFERRED]
  tests/test_bn_manager_backend.py → bn_manager_backend/auth_adapter.py
- `BnManagerHttpError` --uses--> `ClinicalGraphModel`  [INFERRED]
  bn_manager_backend/main.py → clinical_graph_models/model.py
- `ValidateModelTests` --uses--> `ClinicalGraphModel`  [INFERRED]
  tests/test_validation.py → clinical_graph_models/model.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Four Canonical XML Networks** — readme_pharmacotherapy, readme_treatment_setting, readme_involuntary_treatment_considerations, readme_clozapine_in_suicide_risk [EXTRACTED 1.00]
- **XML Model Processing Pipeline** — context_module_registry_file_boundary, readme_secure_xml_compilation, ubiquitous_language_structural_validation, ubiquitous_language_semantic_validation, ubiquitous_language_posterior_evaluation [EXTRACTED 1.00]

## Communities (13 total, 5 thin omitted)

### Community 0 - "Evaluation and Graph Model"
Cohesion: 0.15
Nodes (29): _enumerate_chance_assignments(), evaluate_expected_utilities(), evaluate_posterior(), EvaluationResult, _evidence_weight(), ClinicalGraphModel, Node, Potential (+21 more)

### Community 1 - "XML Compiler and Schema"
Cohesion: 0.20
Nodes (17): read_registry_schema(), _compile_definition(), _compile_variable(), compile_xmlbif(), _node_kind(), _parse_table(), _parse_xml_document(), _properties() (+9 more)

### Community 2 - "FastAPI Model Operations"
Cohesion: 0.10
Nodes (30): assert_csrf_token(), AuthenticationRestAdapter, CsrfError, Exception, Request, SessionAdapter, SessionState, BnManagerSettings (+22 more)

### Community 3 - "Authentication and CSRF"
Cohesion: 0.29
Nodes (12): _as_dict(), _blocked_reason(), _collect_roles(), _first_text(), _is_active(), _is_expired(), _normalize_role(), Any (+4 more)

### Community 4 - "Semantic Validation Tests"
Cohesion: 0.37
Nodes (3): _make_node(), _make_potential(), ValidateModelTests

### Community 5 - "Contract and Response Envelope"
Cohesion: 0.18
Nodes (9): contract_payload(), error_response(), _meta(), ok_response(), Any, RouteContract, TargetNodeContract, XmlBifTarget (+1 more)

### Community 6 - "Registry and API Tests"
Cohesion: 0.12
Nodes (3): TestClient, AuthenticationGuardTests, BnManagerBackendTests

### Community 7 - "XML Migration Architecture"
Cohesion: 0.08
Nodes (27): BN Manager XML Status UI, BN Manager Contract 2.0.0, Compact CPT Broadcast, Module Registry File-Loading Boundary, XML-Only Clinical BN Boundary, Legacy Workflow Removal, XML Bayesian Network Migration, API (+19 more)

## Knowledge Gaps
- **17 isolated node(s):** `clinical-graph-models`, `BN Manager Context`, `Canonical networks`, `Run`, `Validate a registry model` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ClinicalGraphModel` connect `Evaluation and Graph Model` to `XML Compiler and Schema`, `FastAPI Model Operations`, `Semantic Validation Tests`, `Contract and Response Envelope`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `compile_xmlbif()` connect `XML Compiler and Schema` to `Evaluation and Graph Model`, `FastAPI Model Operations`, `Contract and Response Envelope`, `Registry and API Tests`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `SessionState` connect `FastAPI Model Operations` to `Authentication and CSRF`, `Registry and API Tests`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `ClinicalGraphModel` (e.g. with `BnManagerHttpError` and `EvaluationResult`) actually correct?**
  _`ClinicalGraphModel` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `clinical-graph-models`, `BN Manager Context`, `Canonical networks` to the rest of the system?**
  _17 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `FastAPI Model Operations` be split into smaller, more focused modules?**
  _Cohesion score 0.1036077705827937 - nodes in this community are weakly interconnected._
- **Should `Registry and API Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.11904761904761904 - nodes in this community are weakly interconnected._