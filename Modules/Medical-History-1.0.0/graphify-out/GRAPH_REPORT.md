# Graph Report - Medical-History-1.0.0  (2026-07-22)

## Corpus Check
- 9 files · ~3,481 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 118 nodes · 133 edges · 40 communities (6 shown, 34 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b82b9358`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Frontend app.js logic
- Server config & modules
- HTML UI panels
- package.json manifest
- Server internals docs
- Production hardening limits
- Activation flow
- README integration overview
- Activation & submission handlers
- Routing & JSON I/O
- Options & submission endpoints
- Activation Status Flow: active -> submitted / expired
- BASE_PATH Environment Variable
- Permissive Wildcard CORS
- Keep Schema In Sync With Code
- Standard Error Payload Shape
- Static File Path Traversal Guard
- GET /api/internal/medical-history/activation/{code}
- GET /api/internal/medical-history/health
- Internal REST API Boundary
- Local JSON File Persistence
- Known Limitations List
- launchUrl Response Field
- GET /api/internal/medical-history/submissions
- Medical History Handoff Document
- Medication Notes UI Gap
- Medication Row
- Zero-Dependency Node.js Server
- GET /api/internal/medical-history/options
- PHI Production Hardening Gaps
- Repeat Submission Limitation
- GET /api/internal/medical-history/schema
- Server.js Function Inventory
- 2-Hour Activation Session Expiry
- PowerShell Smoke Test
- Static Frontend Serving
- Default Port 4173
- Module Integration Pattern
- medical_history_entry_form
- README (Quick Start)

## God Nodes (most connected - your core abstractions)
1. `activateMedicalHistory()` - 9 edges
2. `submitMedicalHistory()` - 9 edges
3. `route()` - 9 edges
4. `getActivation()` - 8 edges
5. `sendJson()` - 7 edges
6. `sendError()` - 7 edges
7. `restoreActivationFromUrl()` - 6 edges
8. `readJson()` - 6 edges
9. `validateSubmission()` - 6 edges
10. `showError()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `History Form (HTML)` --references--> `POST /api/internal/medical-history/submissions`  [INFERRED]
  public/index.html → MEDICAL_HISTORY_HANDOFF.md
- `Three-State UI Flow` --references--> `Frontend URL ?code= Loader`  [INFERRED]
  public/index.html → MEDICAL_HISTORY_HANDOFF.md
- `Activation Panel (HTML)` --references--> `POST /api/internal/medical-history/activate`  [INFERRED]
  public/index.html → MEDICAL_HISTORY_HANDOFF.md
- `Comorbidities Multi-Select` --shares_data_with--> `Comorbidity Option List`  [INFERRED]
  public/index.html → MEDICAL_HISTORY_HANDOFF.md
- `Activation Code Input` --references--> `6-Character Alphanumeric Activation Code`  [INFERRED]
  public/index.html → MEDICAL_HISTORY_HANDOFF.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Activation Flow (activate endpoint, session, expiry, code validation, launchUrl, frontend loader)** — medical_history_handoff_activateendpoint, medical_history_handoff_activationsession, medical_history_handoff_sessionexpiry, medical_history_handoff_activationcodevalidation, medical_history_handoff_lauRL, medical_history_handoff_urlquerycodeloader, public_index_activationpanel [EXTRACTED 0.95]
- **Submission Flow (submit endpoint, submission record, comorbidity option, medication row, history-form)** — medical_history_handoff_submitendpoint, medical_history_handoff_medicalhistorysubmission, medical_history_handoff_comorbidityoption, medical_history_handoff_medicationrow, public_index_historyform [EXTRACTED 0.95]
- **Production Hardening Gaps (CORS wildcard, JSON persistence, PHI, repeat submissions)** — medical_history_handoff_corswildcard, medical_history_handoff_jsonpersistence, medical_history_handoff_phiproductiongaps, medical_history_handoff_repeatsubmissions, medical_history_handoff_cornotsecret [EXTRACTED 0.85]

## Communities (40 total, 34 thin omitted)

### Community 0 - "Frontend app.js logic"
Cohesion: 0.22
Nodes (14): activateFromCode(), addMedicationRow(), api(), clearError(), elements, escapeAttribute(), isYes(), loadOptions() (+6 more)

### Community 1 - "Server config & modules"
Cohesion: 0.15
Nodes (16): ANTIPSYCHOTIC_OPTIONS, CLOZAPINE_CONTRAINDICATION_OPTIONS, COMORBIDITY_OPTIONS, crypto, ensureDataFiles(), ensureJsonFile(), fs, http (+8 more)

### Community 2 - "HTML UI panels"
Cohesion: 0.13
Nodes (15): POST /api/internal/medical-history/activate, 6-Character Alphanumeric Activation Code, Comorbidity Option List, returnUrl / Back-to-Dashboard, POST /api/internal/medical-history/submissions, Frontend URL ?code= Loader, Activation Code Input, Activation Panel (HTML) (+7 more)

### Community 3 - "package.json manifest"
Cohesion: 0.17
Nodes (11): description, engines, node, main, name, private, scripts, dev (+3 more)

### Community 8 - "Activation & submission handlers"
Cohesion: 0.22
Nodes (6): assert, fs, os, path, { spawn }, test

### Community 9 - "Routing & JSON I/O"
Cohesion: 0.41
Nodes (13): activateMedicalHistory(), getActivation(), isValidCode(), listSubmissions(), normalizeCode(), parseBody(), readJson(), route() (+5 more)

## Knowledge Gaps
- **54 isolated node(s):** `name`, `version`, `private`, `description`, `main` (+49 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `name`, `version`, `private` to the rest of the system?**
  _54 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Server config & modules` be split into smaller, more focused modules?**
  _Cohesion score 0.14705882352941177 - nodes in this community are weakly interconnected._
- **Should `HTML UI panels` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._