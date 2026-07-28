# Graph Report - .  (2026-07-28)

## Corpus Check
- Corpus is ~13,672 words - fits in a single context window. You may not need a graph.

## Summary
- 105 nodes · 152 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.95)
- Token cost: 156,419 input · 4,595 output

## Community Hubs (Navigation)
- Severity Module Overview
- Auth & Server Infrastructure
- Severity Assessment Engine
- Package Dependencies
- Auth Adapter & Testing
- Assessment Repository
- Workflow Tests
- Risk & UI Integration
- API Tests
- Workflow JS Tests

## God Nodes (most connected - your core abstractions)
1. `Severity Module` - 13 edges
2. `createApp()` - 8 edges
3. `createMemoryAssessmentStore()` - 5 edges
4. `migrateAssessmentsJson()` - 5 edges
5. `computePanssScores()` - 5 edges
6. `applyPanssScores()` - 5 edges
7. `Ponytail Philosophy` - 5 edges
8. `assertMap()` - 4 edges
9. `createJsonAssessmentStore()` - 4 edges
10. `createSqliteAssessmentStore()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Severity Module` --references--> `Suicide Risk Module`  [EXTRACTED]
  HANDOFF.md → README.md
- `createApp()` --calls--> `computePanssScores()`  [EXTRACTED]
  server.js → severity-assessment.js
- `withServer()` --calls--> `createApp()`  [EXTRACTED]
  server.test.js → server.js
- `Severity Module` --references--> `API Contract`  [EXTRACTED]
  HANDOFF.md → README.md
- `Severity Module` --references--> `Insight Platform`  [EXTRACTED]
  HANDOFF.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Severity Module Core Architecture** — modules_severity_1_1_0_handoff_severity_module, modules_severity_1_1_0_handoff_server_js, modules_severity_1_1_0_handoff_index_html, modules_severity_1_1_0_handoff_test_api_js, modules_severity_1_1_0_handoff_json_persistence [EXTRACTED 1.00]
- **Clinical Decision Support Flow** — modules_severity_1_1_0_handoff_clinical_interpretation, modules_severity_1_1_0_public_index_update_realtime_calculations, modules_severity_1_1_0_public_index_severity_bands, modules_severity_1_1_0_readme_suicide_risk_module, modules_severity_1_1_0_public_index_suicide_risk_integration [INFERRED 0.85]
- **Ponytail Design Governance** — modules_severity_1_1_0_handoff_ponytail_philosophy, modules_severity_1_1_0_handoff_deferred_ledger, modules_severity_1_1_0_handoff_sharp_edges, modules_severity_1_1_0_handoff_test_api_js [INFERRED 0.85]

## Communities (10 total, 2 thin omitted)

### Community 0 - "Severity Module Overview"
Cohesion: 0.15
Nodes (19): Clinical Interpretation Logic, Intentionally Deferred Ponytail Ledger, Design Contract (DESIGN.md), public/index.html Frontend, JSON File Persistence, PANSS (Positive and Negative Syndrome Scale), Ponytail Philosophy, server.js Backend (+11 more)

### Community 1 - "Auth & Server Infrastructure"
Cohesion: 0.17
Nodes (11): createHttpAuthAdapter(), createReadinessProbe(), asSecret(), createSecurity(), app, createApp(), DEFAULT_DATA_DIR, __dirname (+3 more)

### Community 2 - "Severity Assessment Engine"
Cohesion: 0.24
Nodes (12): applyPanssScores(), AssessmentError, clone(), computePanssScores(), PANSS_ITEM_CODES, requireUtcTimestamp(), requireUuid(), scoresForItems() (+4 more)

### Community 3 - "Package Dependencies"
Cohesion: 0.14
Nodes (13): express, author, dependencies, express, description, keywords, license, main (+5 more)

### Community 4 - "Auth Adapter & Testing"
Cohesion: 0.25
Nodes (6): createMemoryAuthAdapter(), parseCanonicalSession(), assessmentMetadata, panssItems, canonical, memory

### Community 5 - "Assessment Repository"
Cohesion: 0.31
Nodes (8): assertMap(), clone(), createJsonAssessmentStore(), createMemoryAssessmentStore(), createSqliteAssessmentStore(), migrateAssessmentsJson(), SQLITE_SCRIPT, createDefaultAssessmentStore()

### Community 6 - "Workflow Tests"
Cohesion: 0.20
Nodes (8): calls, failedPersistenceCalls, failedPersistenceWorkflow, html, interruptedWorkflow, missingCodeCalls, missingCodeWorkflow, workflow

### Community 7 - "Risk & UI Integration"
Cohesion: 0.67
Nodes (4): CSRF Token Handling, submitAssessment Function, Suicide Risk Integration Functions, Suicide Risk Module

## Knowledge Gaps
- **35 isolated node(s):** `name`, `version`, `description`, `type`, `main` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Severity Module` connect `Severity Module Overview` to `Risk & UI Integration`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `Suicide Risk Module` connect `Risk & UI Integration` to `Severity Module Overview`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `createApp()` connect `Auth & Server Infrastructure` to `Severity Assessment Engine`, `Auth Adapter & Testing`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _35 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Package Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._