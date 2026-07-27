# Graph Report - .  (2026-07-27)

## Corpus Check
- Corpus is ~9,657 words - fits in a single context window. You may not need a graph.

## Summary
- 205 nodes · 318 edges · 14 communities (11 shown, 3 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Auth and Readiness
- Repository Layer
- Submission Model
- Auth Adapter and Retention
- Memory Repository
- Frontend Application
- Package Dependencies
- Server Tests
- Clinical Data Model
- Activation Flow
- Production Auth and Security
- Conditional UI
- Patient History Form
- Result Panel

## God Nodes (most connected - your core abstractions)
1. `clone()` - 16 edges
2. `MemoryMedicalHistoryRepository` - 16 edges
3. `SqliteMedicalHistoryRepository` - 16 edges
4. `MedicalHistorySubmissionStore` - 10 edges
5. `freeze()` - 9 edges
6. `migrateJsonToRepository()` - 9 edges
7. `createServer()` - 9 edges
8. `structureCondition()` - 6 edges
9. `restoreActivationFromUrl()` - 6 edges
10. `createMemoryMedicalHistoryRepository()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `submissionData()` --indirect_call--> `structureCondition()`  [INFERRED]
  server.js → medical-history-submission.js
- `submissionData()` --indirect_call--> `structureMedication()`  [INFERRED]
  server.js → medical-history-submission.js
- `createServer()` --calls--> `createDefaultMedicalHistoryRepository()`  [EXTRACTED]
  server.js → repository.js
- `HTML Form Structure` --references--> `Conditional UI Behavior`  [INFERRED]
  public/index.html → MEDICAL_HISTORY_HANDOFF.md
- `Clinical Questions UI` --references--> `Clozapine Contraindications`  [INFERRED]
  public/index.html → MEDICAL_HISTORY_HANDOFF.md

## Import Cycles
- None detected.

## Communities (14 total, 3 thin omitted)

### Community 0 - "Auth and Readiness"
Cohesion: 0.08
Nodes (31): createHttpAuthAdapter(), createReadinessProbe(), applyCorsHeaders(), asSecret(), { createHmac, randomBytes, timingSafeEqual }, createSecurity(), jsonError(), ANTIPSYCHOTIC_OPTIONS (+23 more)

### Community 1 - "Repository Layer"
Cohesion: 0.09
Nodes (18): assertArray(), createDefaultMedicalHistoryRepository(), createMemoryMedicalHistoryRepository(), createSqliteMedicalHistoryRepository(), fs, migrateJsonToRepository(), openSqlite(), path (+10 more)

### Community 2 - "Submission Model"
Cohesion: 0.11
Nodes (19): assertAuthor(), assertUuid(), calculateEtag(), clone(), crypto, isApprovedCoding(), isCanonicalUuid(), MedicalHistorySubmissionStore (+11 more)

### Community 3 - "Auth Adapter and Retention"
Cohesion: 0.11
Nodes (17): createMemoryAuthAdapter(), parseCanonicalSession(), applyRetentionPolicy(), assertRetentionPolicy(), REQUIRED_APPROVER_ROLES, RetentionApprovalRequired, assert, canonical (+9 more)

### Community 4 - "Memory Repository"
Cohesion: 0.21
Nodes (3): clone(), freeze(), MemoryMedicalHistoryRepository

### Community 5 - "Frontend Application"
Cohesion: 0.20
Nodes (15): activateFromCode(), addMedicationRow(), api(), clearError(), elements, escapeAttribute(), getCsrfToken(), isYes() (+7 more)

### Community 6 - "Package Dependencies"
Cohesion: 0.13
Nodes (14): better-sqlite3, dependencies, better-sqlite3, description, engines, node, main, name (+6 more)

### Community 7 - "Server Tests"
Cohesion: 0.22
Nodes (7): assert, { createMemoryMedicalHistoryRepository }, { createServer }, crypto, fs, path, test

### Community 8 - "Clinical Data Model"
Cohesion: 0.29
Nodes (7): Change Guidance Checklist, Clozapine Contraindications, Drug List Constraint, Submission Model v2, Clinical Questions UI, Internal REST API Routes, Collected Information Fields

### Community 9 - "Activation Flow"
Cohesion: 0.50
Nodes (4): Activation Code, Persistence and Testing, Activation Panel UI, Module Overview

### Community 10 - "Production Auth and Security"
Cohesion: 0.67
Nodes (3): Auth and CSRF, PHI Retention Policy, Production Requirements

## Knowledge Gaps
- **69 isolated node(s):** `crypto`, `name`, `version`, `private`, `description` (+64 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SqliteMedicalHistoryRepository` connect `Repository Layer` to `Memory Repository`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `MemoryMedicalHistoryRepository` connect `Memory Repository` to `Repository Layer`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `MedicalHistorySubmissionStore` connect `Submission Model` to `Auth and Readiness`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **What connects `crypto`, `name`, `version` to the rest of the system?**
  _69 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth and Readiness` be split into smaller, more focused modules?**
  _Cohesion score 0.07807807807807808 - nodes in this community are weakly interconnected._
- **Should `Repository Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.08901515151515152 - nodes in this community are weakly interconnected._
- **Should `Submission Model` be split into smaller, more focused modules?**
  _Cohesion score 0.1103448275862069 - nodes in this community are weakly interconnected._