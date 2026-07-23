# Graph Report - Add-New-Patient-1.1.0  (2026-07-22)

## Corpus Check
- 22 files · ~298,846 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 377 nodes · 741 edges · 20 communities (15 shown, 5 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f90336c8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Backend Test Suite
- Config and CSRF Helpers
- API and Module Documentation
- Auth Module
- Database Adapter and Repository
- Clinical Data Models
- Design System Rationale
- Frontend App Logic
- SQLite Migration Utilities
- Frontend HTML Shell
- Frontend Test Harness
- Package Init
- Image 1
- Image 2
- Python Dependencies
- Add New Patient API Contract
- Repository Handoff — Add New Patient Module
- DESIGN.md
- File Map
- Add New Patient Module

## God Nodes (most connected - your core abstractions)
1. `AddNewPatientServer` - 46 edges
2. `request_json()` - 43 edges
3. `Add New Patient Module Handoff` - 31 edges
4. `valid_payload()` - 30 edges
5. `csrf_headers()` - 29 edges
6. `AddNewPatientBackendTest` - 29 edges
7. `Add New Patient API Contract` - 22 edges
8. `PatientRepository` - 16 edges
9. `AuthBoundaryTest` - 14 edges
10. `fetch_auth_identity()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `REST-Only Communication Rule` --semantically_similar_to--> `Carbon Health Design System`  [INFERRED] [semantically similar]
  handoff.md → DESIGN.md
- `White Space as Clinical Instrument` --semantically_similar_to--> `REST-Only Communication Rule`  [INFERRED] [semantically similar]
  DESIGN.md → handoff.md
- `Add New Patient Module Handoff` --conceptually_related_to--> `Repository Handoff`  [EXTRACTED]
  docs/add-new-patient-handoff.md → handoff.md
- `Stable Patient Identifier Contract` --conceptually_related_to--> `Stable Patient Identifier Contract`  [EXTRACTED]
  docs/api-contract.md → handoff.md
- `Patient Code (6-char identifier)` --references--> `Stable Patient Identifier Contract`  [EXTRACTED]
  docs/patient-domain-glossary.md → handoff.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Five Clinical Status States** — design_md_urgent, design_md_warning, design_md_normal, design_md_follow_up, design_md_info [EXTRACTED 1.00]
- **Stable Patient Identifier System** — patient_stable_id, patient_code, docs_api_contract_stable_patient_identifier_contract, handoff_md_stable_identifier_contract, f1_1_stable_patient_identifier [EXTRACTED 1.00]
- **Add New Patient Module Architecture** — readme_md, readme_md_stack, handoff_md, handoff_md_core_architectural_rule, static_allowlist, docs_add_new_patient_handoff_add_new_patient_module_handoff, docs_api_contract_add_new_patient_api_contract, docs_patient_domain_glossary_patient_domain_glossary [EXTRACTED 1.00]

## Communities (20 total, 5 thin omitted)

### Community 0 - "Backend Test Suite"
Cohesion: 0.10
Nodes (18): AddNewPatientBackendTest, AddNewPatientServer, auth_payload(), AuthBoundaryTest, AuthIdentityNormalizationTest, canonical_encounter_payload(), canonical_patient_payload(), ConcurrencyTest (+10 more)

### Community 1 - "Config and CSRF Helpers"
Cohesion: 0.10
Nodes (38): Settings, csrf_error(), generate_csrf_token(), JSONResponse, Request, request_has_valid_csrf(), sign_csrf_token(), verify_csrf_token() (+30 more)

### Community 2 - "API and Module Documentation"
Cohesion: 0.05
Nodes (41): A0.1 Module Rebuild (Node to Python), GET /api/health, GET /internal/dashboard/module-routes/add-new-patient, B1.1 Auth REST Client, Dashboard Module, Defense-in-Depth Constraint, Add New Patient Module Handoff, Adding a Patient Field (+33 more)

### Community 3 - "Auth Module"
Cohesion: 0.18
Nodes (22): auth_session_url(), AuthSessionError, _blocked_auth_session(), _expiry(), fetch_auth_identity(), _fetch_json(), forwarded_auth_headers(), _has_blocked_status() (+14 more)

### Community 4 - "Database Adapter and Repository"
Cohesion: 0.15
Nodes (14): DatabaseAdapter, Any, canonical_suicidality(), compute_age(), _find_patient_id_row(), IdempotencyConflict, intake_row(), json_list() (+6 more)

### Community 5 - "Clinical Data Models"
Cohesion: 0.10
Nodes (10): create_canonical_encounter(), CanonicalEncounterCreate, CanonicalPatientCreate, ClinicalFlag, ClinicalSection, PatientDemographics, PatientIntake, Any (+2 more)

### Community 6 - "Design System Rationale"
Cohesion: 0.17
Nodes (13): Carbon Health Design System, Five-State Clinical Status System, Follow-up Status, Info Status, Normal Status, Skeleton Loaders, Teal as Clinical Trust, Typography Legibility as Patient Safety (+5 more)

### Community 7 - "Frontend App Logic"
Cohesion: 0.25
Nodes (9): CLIENT_VALIDATION_MESSAGES, createAddNewPatientModule(), FIELD_INPUT_NAMES, generateBrowserPatientCode(), getRequiredElement(), isValidDob(), normalizePatientInput(), parseListInput() (+1 more)

### Community 8 - "SQLite Migration Utilities"
Cohesion: 0.36
Nodes (4): migrate_patients_to_identity_table(), now_iso(), SQLiteAdapter, Connection

### Community 9 - "Frontend HTML Shell"
Cohesion: 0.50
Nodes (4): Patient Module HTML Shell, Dashboard View, Patient Form, Patient View

### Community 15 - "Add New Patient API Contract"
Cohesion: 0.06
Nodes (38): GET /api/patients, GET /api/patients/{idOrCode}, POST /api/patients, Auth Module, CSRF Endpoint GET /api/add-new-patient/csrf, Add New Patient API Contract, Add New Patient Owned Endpoints, Auth Contract (+30 more)

### Community 16 - "Repository Handoff — Add New Patient Module"
Cohesion: 0.14
Nodes (13): Current invariants (do not break), How to run, Known limitations (not bugs), Layout, Patient identifier contract (F1.1), Recent additions visible in current code but not in older docs, Repository Handoff — Add New Patient Module, Request payload shape (+5 more)

### Community 17 - "DESIGN.md"
Cohesion: 0.15
Nodes (12): 1. Visual Theme & Atmosphere, 2. Color System, 3. Typography, 4. Components & Patterns, 5. Spacing & Layout, 6. Motion & Interaction, Accessibility, Contrast Ratios (+4 more)

### Community 18 - "File Map"
Cohesion: 0.15
Nodes (13): `add_new_patient_backend/auth.py`, `add_new_patient_backend/config.py`, `add_new_patient_backend/db.py`, `add_new_patient_backend/main.py`, `add_new_patient_backend/models.py`, `add_new_patient_backend/repository.py`, `app.js`, Exception Handlers (+5 more)

### Community 19 - "Add New Patient Module"
Cohesion: 0.29
Nodes (6): Add New Patient Module, Embed Contract, REST API, Run, Stack, Tests

## Knowledge Gaps
- **103 isolated node(s):** `CLIENT_VALIDATION_MESSAGES`, `FIELD_INPUT_NAMES`, `here`, `html`, `Rationale` (+98 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Add New Patient Module Handoff` connect `API and Module Documentation` to `File Map`, `Design System Rationale`, `Add New Patient API Contract`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `normalize_authenticated_session()` connect `Auth Module` to `Backend Test Suite`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **What connects `CLIENT_VALIDATION_MESSAGES`, `FIELD_INPUT_NAMES`, `here` to the rest of the system?**
  _103 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Backend Test Suite` be split into smaller, more focused modules?**
  _Cohesion score 0.1010351966873706 - nodes in this community are weakly interconnected._
- **Should `Config and CSRF Helpers` be split into smaller, more focused modules?**
  _Cohesion score 0.10404040404040404 - nodes in this community are weakly interconnected._
- **Should `API and Module Documentation` be split into smaller, more focused modules?**
  _Cohesion score 0.047619047619047616 - nodes in this community are weakly interconnected._
- **Should `Database Adapter and Repository` be split into smaller, more focused modules?**
  _Cohesion score 0.14623655913978495 - nodes in this community are weakly interconnected._