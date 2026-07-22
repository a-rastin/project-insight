# Graph Report - Severity-1.1.0  (2026-07-22)

## Corpus Check
- 7 files · ~8,886 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 71 nodes · 71 edges · 7 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e60a821a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- server.js
- Severity Module
- HANDOFF — `severity` module
- 4. Backend — `server.js` (149 lines, the whole thing)
- 5. Frontend — `public/index.html` (830 lines, single file)

## God Nodes (most connected - your core abstractions)
1. `HANDOFF — `severity` module` - 13 edges
2. `Severity Module` - 9 edges
3. `5. Frontend — `public/index.html` (830 lines, single file)` - 7 edges
4. `4. Backend — `server.js` (149 lines, the whole thing)` - 5 edges
5. `4.3 Routes — only two exist` - 4 edges
6. `Run` - 4 edges
7. `createMemoryAssessmentStore()` - 3 edges
8. `createApp()` - 3 edges
9. `API contract` - 3 edges
10. `scripts` - 2 edges

## Surprising Connections (you probably didn't know these)
- `withServer()` --calls--> `createApp()`  [EXTRACTED]
  server.test.js → server.js

## Import Cycles
- None detected.

## Communities (7 total, 0 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.14
Nodes (13): express, author, dependencies, express, description, keywords, license, main (+5 more)

### Community 1 - "server.js"
Cohesion: 0.22
Nodes (9): app, clone(), createApp(), createJsonAssessmentStore(), createMemoryAssessmentStore(), DEFAULT_DATA_DIR, __dirname, __filename (+1 more)

### Community 2 - "Severity Module"
Cohesion: 0.13
Nodes (14): API contract, As a sub-module, Design compliance, Features, File layout, GET `/api/severity/:patient_code`, Intentionally deferred (ponytail ledger), PUT `/api/severity/:patient_code` (+6 more)

### Community 3 - "HANDOFF — `severity` module"
Cohesion: 0.17
Nodes (11): 10. The "ponytail" philosophy (context, not legal), 11. How to verify your change, 12. If you only read three things, 1. What this module is, 2. Repo layout (only 4 source files matter), 3. Stack & runtime, 6. Data model, 7. API contract (cheat sheet) (+3 more)

### Community 5 - "4. Backend — `server.js` (149 lines, the whole thing)"
Cohesion: 0.25
Nodes (8): 4.1 Boot sequence, 4.2 Helpers, 4.3 Routes — only two exist, 4.4 Where to make changes, 4. Backend — `server.js` (149 lines, the whole thing), Catch-all  (`server.js:134`), `GET /api/severity/:patient_code`  (`server.js:60`), `PUT /api/severity/:patient_code`  (`server.js:88`)

### Community 6 - "5. Frontend — `public/index.html` (830 lines, single file)"
Cohesion: 0.29
Nodes (7): 5.1 Page structure (top → bottom of body), 5.2 Constants, 5.3 State (module-scope `let`s, line 357), 5.4 Key functions, 5.5 `updateRealtimeCalculations()` — read this twice, 5.6 Where to make changes, 5. Frontend — `public/index.html` (830 lines, single file)

## Knowledge Gaps
- **47 isolated node(s):** `name`, `version`, `description`, `type`, `main` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HANDOFF — `severity` module` connect `HANDOFF — `severity` module` to `4. Backend — `server.js` (149 lines, the whole thing)`, `5. Frontend — `public/index.html` (830 lines, single file)`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `4. Backend — `server.js` (149 lines, the whole thing)` connect `4. Backend — `server.js` (149 lines, the whole thing)` to `HANDOFF — `severity` module`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `5. Frontend — `public/index.html` (830 lines, single file)` connect `5. Frontend — `public/index.html` (830 lines, single file)` to `HANDOFF — `severity` module`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _47 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `Severity Module` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._