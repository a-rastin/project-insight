# Graph Report - /root/projects/insight/Modules/DDI-Checker-1.2.0  (2026-07-27)

## Corpus Check
- 38 files · ~2,859,154 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 403 nodes · 664 edges · 24 communities (20 shown, 4 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- KB Ingestion & RxNorm Map
- App Frontend Core
- SQLite Persistence Layer
- KB Validation Pipeline
- DDI Engine Core
- Browser Storage & Revisions
- Package Dependencies
- REST API Adapter
- Auth & Server Module
- Architecture Analyzer
- System Architecture Concepts
- KB Repair Tooling
- REST Contract Tests
- Authoritative Engine Tests
- SQLite Store Tests
- REST Endpoint Tests
- CNS Depressants KB Data
- Serotonin Drug Interactions
- Malformed Drug Test Fixtures
- Architecture Analysis Script
- Tour Analysis Script
- Architecture Documentation
- README Overview

## God Nodes (most connected - your core abstractions)
1. `validateKnowledgeBase()` - 22 edges
2. `SqliteKbStore` - 14 edges
3. `MemoryKbStore` - 12 edges
4. `createDdiServer()` - 11 edges
5. `clone()` - 11 edges
6. `loadBundledKbFromServer()` - 10 edges
7. `buildIndex()` - 10 edges
8. `parseReport()` - 10 edges
9. `scripts` - 9 edges
10. `renderReviewList()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `validateDrugIdentities()` --indirect_call--> `label()`  [INFERRED]
  scripts/ingest.mjs → src/kb-validator.cjs
- `validateDrugIdentities()` --indirect_call--> `normalizeDrugName()`  [INFERRED]
  scripts/ingest.mjs → src/report-parser.js
- `buildKnowledgeBase()` --calls--> `validateKnowledgeBase()`  [EXTRACTED]
  scripts/ingest.mjs → src/kb-validator.cjs
- `runCli()` --calls--> `validateKnowledgeBase()`  [EXTRACTED]
  scripts/validate-kb.mjs → src/kb-validator.cjs
- `startServer()` --calls--> `createDdiServer()`  [EXTRACTED]
  test/ddi-rest-contract.test.mjs → src/ddi-rest-adapter.cjs

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Browser Loader Dependency Chain** — index, src_styles, src_report_parser, src_ddi_engine, src_kb_persistence, src_storage_adapter, src_app, data_active_kb_js, browser_local_storage [EXTRACTED 1.00]
- **Ingestion Pipeline** — scripts_ingest, src_report_parser, rxnorm_seed_map, medscape_report_format, data_active_kb_json, data_active_kb_js [EXTRACTED 1.00]
- **Test Suite** — test_ddi_engine_test, test_ingest_test, test_ui_source_test, test_kb_persistence_test [EXTRACTED 1.00]
- **Design Rationales** — kb_version_identity, medication_identity_resolution, fail_closed_identity_resolution, medication_instance_invariant, clinical_alert_safety_gate, one_way_write_cli_to_browser, versioned_local_revision_envelope, storage_adapter_seam, kb_validation_gate, override_rationale_mechanism, local_kb_upgrade_conflict [INFERRED 0.95]
- **Runtime Checker Flow** — src_app, src_ddi_engine, function_resolvedrug, function_checkinteractions, function_buildindex, function_createauditentry, knowledge_base, browser_local_storage [INFERRED 0.95]
- **Admin Workflow** — admin_review_workflow, upload_report_workflow, src_report_parser, src_kb_persistence, browser_local_storage, knowledge_base [INFERRED 0.95]

## Communities (24 total, 4 thin omitted)

### Community 0 - "KB Ingestion & RxNorm Map"
Cohesion: 0.09
Nodes (42): Active KB JS (data/active-kb.js), Medscape Text/MD Report Format, One-Way Write CLI to Browser KB, RxNorm Terminology System, RxNorm Seed Map, addDoseSuggestions(), buildKnowledgeBase(), compareRelativePaths() (+34 more)

### Community 1 - "App Frontend Core"
Cohesion: 0.12
Nodes (38): activateRevision(), addDrugToKb(), addInteraction(), checkNow(), clearStorageFailure(), currentResultsExport(), escapeHtml(), exportAudit() (+30 more)

### Community 2 - "SQLite Persistence Layer"
Cohesion: 0.11
Nodes (15): ADMIN_ACTIONS, applyReviewEdits(), clinicalActivationErrors(), clone(), ensureReviewer(), findInteraction(), fs, MemoryKbStore (+7 more)

### Community 3 - "KB Validation Pipeline"
Cohesion: 0.09
Nodes (26): Active KB JSON (data/active-kb.json), KB Validation Gates, here, require, runCli(), { validateKnowledgeBase }, CONFIDENCE, fingerprint() (+18 more)

### Community 4 - "DDI Engine Core"
Cohesion: 0.15
Nodes (24): addDoseSuggestions(), addIdentityCandidate(), assignMedicationInstanceIds(), buildIndex(), checkInteractions(), cleanReportLine(), createEmptyIndex(), createParsedInteraction() (+16 more)

### Community 5 - "Browser Storage & Revisions"
Cohesion: 0.09
Nodes (18): index.html Browser Entry Point, Local KB Upgrade and Conflict Resolution, createRevision(), rebase(), reviewChanges(), revisionFromLegacy(), browserStorageAdapter(), memoryStorageAdapter() (+10 more)

### Community 6 - "Package Dependencies"
Cohesion: 0.08
Nodes (23): better-sqlite3, dependencies, better-sqlite3, description, keywords, license, name, private (+15 more)

### Community 7 - "REST API Adapter"
Cohesion: 0.11
Nodes (14): buildCandidate(), buildCoverage(), buildOutcome(), buildPersistenceResponse(), { createRequire }, crypto, engine, fs (+6 more)

### Community 8 - "Auth & Server Module"
Cohesion: 0.11
Nodes (17): createHttpAuthAdapter(), createMemoryAuthAdapter(), bundledKb, createAuth(), { createDdiServer }, { createHttpAuthAdapter, createMemoryAuthAdapter }, { createKbSqliteStore, createMemoryKbStore, migrateKbIntoStore }, __dirname (+9 more)

### Community 9 - "Architecture Analyzer"
Cohesion: 0.11
Nodes (16): assigned, fileTypes, finalGraph, fs, graph, inter, issues, layers (+8 more)

### Community 10 - "System Architecture Concepts"
Cohesion: 0.12
Nodes (17): Admin Review Workflow, Audit Capture System, Browser Local Storage, Clinical Alert Safety Gate, DDI-Checker Module, Fail-Closed Identity Resolution, buildIndex, checkInteractions (+9 more)

### Community 11 - "KB Repair Tooling"
Cohesion: 0.13
Nodes (14): before, canonicalById, canonicals, __dirname, engine, __filename, kb, kbPath (+6 more)

### Community 12 - "REST Contract Tests"
Cohesion: 0.19
Nodes (11): buildOpenapiDocument(), createDdiServer(), ddiContractPayload(), pivotalProblem(), adminAuth(), { createDdiServer, ddiContractPayload }, engine, fixtureKb (+3 more)

### Community 13 - "Authoritative Engine Tests"
Cohesion: 0.18
Nodes (8): engine, ENGINE_FUNCTIONS, ENGINE_VALUES, fixtureDir, here, reportParser, repoScripts, require

### Community 14 - "SQLite Store Tests"
Cohesion: 0.20
Nodes (8): adminPrincipal, { createKbSqliteStore, createMemoryKbStore, migrateKbIntoStore }, __dirname, draftKb(), engine, __filename, require, rxnormSeeded()

### Community 15 - "REST Endpoint Tests"
Cohesion: 0.22
Nodes (6): { createDdiServer }, engine, fixtureKb, memoryStorage(), require, startServer()

### Community 16 - "CNS Depressants KB Data"
Cohesion: 0.67
Nodes (3): Sedative CNS Depressants, Lefamulin, Quetiapine

### Community 17 - "Serotonin Drug Interactions"
Cohesion: 0.67
Nodes (3): Amitriptyline, Fluoxetine, Pimozide

### Community 18 - "Malformed Drug Test Fixtures"
Cohesion: 0.67
Nodes (3): Invalid Drug Heading Candidate, Mysterydrug, Validdrug

## Ambiguous Edges - Review These
- `Mysterydrug` → `Invalid Drug Heading Candidate`  [AMBIGUOUS]
  test/fixtures/reports/malformed.txt · relation: conceptually_related_to

## Knowledge Gaps
- **140 isolated node(s):** `fs`, `fs`, `path`, `require`, `persistence` (+135 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Mysterydrug` and `Invalid Drug Heading Candidate`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `validateKnowledgeBase()` connect `KB Validation Pipeline` to `KB Ingestion & RxNorm Map`, `SQLite Persistence Layer`, `KB Repair Tooling`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `index.html Browser Entry Point` connect `Browser Storage & Revisions` to `KB Ingestion & RxNorm Map`, `App Frontend Core`, `DDI Engine Core`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `DDI-Checker Module` connect `System Architecture Concepts` to `KB Ingestion & RxNorm Map`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **What connects `fs`, `fs`, `path` to the rest of the system?**
  _140 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `KB Ingestion & RxNorm Map` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._
- **Should `App Frontend Core` be split into smaller, more focused modules?**
  _Cohesion score 0.12195121951219512 - nodes in this community are weakly interconnected._