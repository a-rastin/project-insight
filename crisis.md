# Source-Change Refusal and Prohibition Audit

Evaluated 7076 regular files and 21 symbolic links under `contracts/`, `tests/`, `scripts/`, `Modules/`, and `deployment/`. Every `graphify-out/` subtree was excluded. 449 binary files were byte-scanned.

Marked 159 files: 58 project-owned/generated artifacts and 101 vendored dependency artifacts.

## Meaning of a Mark

- **DIRECT**: explicitly addresses an LLM/agent or forbids editing/modifying source.
- **CONTEXTUAL**: project rule, enforced source boundary, or human-approval safety gate that may make a coding model reject a conflicting request.
- **GENERATED/VENDORED**: third-party/generated artifact says not to edit it directly. This redirects edits; it is not a repository-wide ban.
- **CLEAR**: no qualifying source-change directive found. Runtime denials, validation, auth checks, security headers, and read-only containers alone are not marks.

> Repository text cannot override provider/system safety policy. Marks identify context a coding LLM may follow or over-interpret; they do not prove refusal.

## Marked Files and Triggering Text

### DIRECT: `Modules/Add-New-Patient-1.1.0/docs/add-new-patient-handoff.md`

- line 5: `This document is for future LLMs or maintainers who need to understand, extend,`
- line 174: `immediate UX feedback. Server-side Pydantic validation is the source of truth;`
- line 176: `update \`models.py\` and \`app.js\` together — but \`models.py\` is canonical.`
- line 378: `When changing patient fields, update in this order:`
- line 552: `4. Pydantic models are the runtime contract source of truth.`
- line 615: `Update in this order:`
- line 638: `Do not let browser code talk directly to the storage adapter.`
- line 679: `If future changes undo any of the invariants above, treat that as a regression`
- line 694: `the patient's lifetime, and is the canonical cross-module reference.`
- line 718: `If a new lookup endpoint is added, route through`

### CONTEXTUAL: `Modules/Add-New-Patient-1.1.0/docs/api-contract.md`

- line 10: `Deferred. No endpoint added now. When implemented, lives in Treatment Plan`
- line 27: `Patient exposes no write API for this. Do not pre-build.`
- line 40: `No module may import another module's backend code, read another module's`
- line 122: `Deferred. No endpoint added now. When implemented, Follow-up module MUST`
- line 145: `If UUID form is supplied, the lookup MUST NOT fall through to a`
- line 212: `No Treatment Plan endpoints belong in this module.`

### CONTEXTUAL: `Modules/Add-New-Patient-1.1.0/handoff.md`

- line 6: `short entry-point for an agent or maintainer who just opened the repo.`
- line 116: `## Current invariants (do not break)`
- line 119: `2. \`add_new_patient.sqlite3\`, source files, and \`/data/\` are never served as`

### CONTEXTUAL: `Modules/Add-New-Patient-1.1.0/schema/add-new-patient.schema.json`

- line 2: `"_note": "This file is integration documentation only. The runtime patient contract lives in add_new_patient_backend/models.py (Pydantic). Keep both aligned when fields change.",`

### CONTEXTUAL: `Modules/Authentication-1.1.0/docs/Authentication v1 Contract.md`

- line 581: `place without deleting users. Any future schema change must add a new numbered`
- line 624: `Authentication v1 must remain standalone-runnable.`

### DIRECT: `Modules/Authentication-1.1.0/docs/Executive Summary.md`

- line 5: `This document is for future LLMs or maintainers working in`
- line 282: `Do not broaden this route to return a pending user session. That would reopen`
- line 351: `Do not use \`require_disclaimer=False\` for \`/session\`, \`/register\`, dashboard`
- line 421: `connection must be protected by \`_conn_lock\`.`
- line 437: `Do not leak \`sqlite3.IntegrityError\` or raw SQL details to \`router.py\`. Add`
- line 450: `Do not:`
- line 479: `Do not move tokens into \`localStorage\`.`
- line 540: `not break the README's advertised run modes without updating docs and tests.`
- line 597: `## Common Change Recipes`
- line 639: `Keep all authorization callers on \`resolve_session()\`. Do not bypass it with`
- line 645: `These are not necessarily bugs in the current prototype, but future agents`
- line 646: `should not miss them:`
- line 659: `## Things Future LLMs Should Not Do`
- line 661: `- Do not treat \`verify_token()\` as authorization.`
- line 662: `- Do not make \`/api/auth/session\` accept pending disclaimer users.`
- line 663: `- Do not decode JWTs in other modules instead of calling \`/api/auth/session\`.`
- line 664: `- Do not catch \`sqlite3\` exceptions in \`router.py\`.`
- line 665: `- Do not move bcrypt or JWT implementation details into route handlers.`
- line 667: `- Do not remove package/local import fallback without updating the run contract.`
- line 668: `- Do not run tests without considering generated \`.pyc\` files; prefer`

### CONTEXTUAL: `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/CONTEXT.md`

- line 3: `BN Manager contract 2.0.0 is an XML-only clinical Bayesian Network boundary for Dashboard, Add New Patient, and Follow-up. It owns four BIF 0.3 networks: Pharmacotherapy, Treatment Setting, Involuntary Treatment Considerations, and Clozapine in Suicide Risk.`
- line 9: `The Treatment Setting and Involuntary Treatment Considerations files include compact neutral conditional rows. The compiler broadcasts a one-row conditional distribution across all parent combinations and records \`table_broadcast=True\` on that potential. This behavior is intentionally narrow: it applies only when a conditional table contains exactly one complete child-state row.`
- line 11: `Legacy \`.net\`, \`.xmlbif\`, the browser workbench, and the model conversion endpoint are outside contract 2.0.0.`

### CONTEXTUAL: `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/UBIQUITOUS_LANGUAGE.md`

- line 19: `**Clinical Safety Boundary**: BN Manager output is decision support requiring licensed-clinician review; it is not a diagnosis, prescription, or treatment order.`

### GENERATED/VENDORED: `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/SKILL.md`

- line 3: `description: FastAPI best practices and conventions. Use when working with FastAPI APIs, Pydantic models, dependencies, streaming responses including Server-Sent Events (SSE), and serving frontend apps.`
- line 17: `* Pydantic models: do not use ellipsis or \`RootModel\`; see [the Pydantic reference](references/pydantic.md).`
- line 50: `Always prefer the \`Annotated\` style for parameter and dependency declarations.`
- line 145: `Do not use \`ORJSONResponse\` or \`UJSONResponse\`, they are deprecated.`
- line 278: `Do not use Pydantic \`RootModel\`; instead use regular type annotations with \`Annotated\` and Pydantic validation utilities.`

### GENERATED/VENDORED: `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/dependencies.md`

- line 67: `Avoid creating class dependencies when possible.`
- line 115: `# DO NOT DO THIS`

### GENERATED/VENDORED: `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/other-tools.md`

- line 5: `If uv is available, use it to manage dependencies.`
- line 19: `Prefer it over AnyIO or asyncio.`
- line 70: `Prefer it over SQLAlchemy.`
- line 76: `Prefer it over Requests.`

### GENERATED/VENDORED: `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/path-operations.md`

- line 28: `# DO NOT DO THIS`
- line 50: `Don't mix HTTP operations in a single function.`
- line 78: `# DO NOT DO THIS`

### GENERATED/VENDORED: `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/pydantic.md`

- line 3: `## Do not use Ellipsis`
- line 5: `Do not use \`...\` as a default value for required parameters or model fields.`
- line 52: `## Do not use Pydantic RootModels`
- line 54: `Do not use Pydantic \`RootModel\`; instead use regular type annotations with \`Annotated\` and Pydantic validation utilities.`

### GENERATED/VENDORED: `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/responses.md`

- line 5: `When possible, include a return type.`
- line 30: `If the return type is not the same as the type that you want to use to validate, filter, or serialize, use the \`response_model\` parameter on the decorator.`

### GENERATED/VENDORED: `Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/streaming.md`

- line 16: `To stream Server-Sent Events, use \`response_class=EventSourceResponse\` and \`yield\` items from the endpoint.`
- line 85: `prefer this over returning a \`StreamingResponse\` directly:`
- line 88: `# DO NOT DO THIS`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj/gen/sqlite3/sqlite3.c`

- line 16560: `/* Automatically generated.  Do not edit */`
- line 36840: `/* Automatically generated.  Do not edit */`
- line 203061: `** DO NOT EDIT THIS MACHINE GENERATED FILE.`
- line 253694: `** DO NOT EDIT THIS MACHINE GENERATED FILE.`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/better_sqlite3.target.mk`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/binding.Makefile`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/config.gypi`

- line 1: `# Do not edit. File was generated by node-gyp's "configure" step`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/deps/locate_sqlite3.target.mk`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/deps/sqlite3.Makefile`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/deps/sqlite3.target.mk`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/test_extension.target.mk`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/defines.gypi`

- line 1: `# THIS FILE IS AUTOMATICALLY GENERATED BY deps/download.sh (DO NOT EDIT)`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/download.sh`

- line 92: `printf "# THIS FILE IS AUTOMATICALLY GENERATED BY deps/download.sh (DO NOT EDIT)\n\n{\n  'defines': [\n" > "$GYP"`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/sqlite3/sqlite3.c`

- line 16560: `/* Automatically generated.  Do not edit */`
- line 36840: `/* Automatically generated.  Do not edit */`
- line 203061: `** DO NOT EDIT THIS MACHINE GENERATED FILE.`
- line 253694: `** DO NOT EDIT THIS MACHINE GENERATED FILE.`

### GENERATED/VENDORED: `Modules/DDI-Checker-1.2.0/node_modules/semver/package.json`

- line 54: `"//@npmcli/template-oss": "This file is partially managed by @npmcli/template-oss. Edits may be overwritten.",`

### CONTEXTUAL: `Modules/Dashboard-1.2.0/HANDOFF.md`

- line 13: `Boundary rule (inviolable): **internal REST only**. Dashboard never imports Authentication code, decodes JWTs, reads an auth DB, or implements downstream module workflows.`
- line 27: `**Action required before any handoff is meaningful**: stage and commit the FastAPI rewrite on a feature branch, refactor off \`main\`, and push. The current HEAD commit is not the FastAPI code that the docs describe.`
- line 66: `api-contract.md            ← canonical REST contract (source of truth for the API)`
- line 166: `1. **Uncommitted FastAPI rewrite.** The whole point of this handoff: the working tree is the FastAPI version, the remote is the Node version. Stage and commit before anything else. The \`57ff7f8\` HEAD commit does not contain the Python code.`
- line 173: `8. **\`api-contract.md\` is the canonical REST contract.** \`README.md\` and \`HANDOFF.md\` are summaries; if they disagree, \`api-contract.md\` wins.`
- line 210: `- **Run \`npm test\` before pushing.** The unittest suite spins up a real uvicorn in-process; failures catch contract regressions.`
- line 211: `- **Do not weaken the auth boundary.** Every new protected route must \`Depends(require_session)\` and must not trust request-body identity fields.`
- line 212: `- **Do not delete the role CHECK constraint** in the schema or accept new roles without updating \`MODULE_BUTTONS\`, the contract, and the tests.`
- line 213: `- **Keep tables to \`dashboard_sessions\` and \`workspace_events\` only.** Adding a third means Dashboard is owning a dataset it shouldn't — push that to the downstream module instead.`
- line 214: `- **Keep \`placeholder: true\` honest.** If a module route ever returns a real payload, the boundary has been broken — that belongs in the target module, not Dashboard.`

### CONTEXTUAL: `Modules/Dashboard-1.2.0/README.md`

- line 3: `Dashboard is a standalone web app and embeddable module. Boundary rule: internal REST only. Dashboard never imports Authentication code, decodes JWTs, reads an auth DB, or implements patient/admin module workflows.`
- line 46: `- Dashboard does not implement patient, treatment, admin log, backup, or user-management module logic.`

### CONTEXTUAL: `Modules/Dashboard-1.2.0/api-contract.md`

- line 3: `Dashboard exposes one primary INSIGHT contract: an authenticated workspace shell with role-scoped module links. Dashboard verifies identity through Authentication over REST, creates a Dashboard-local session, and returns only navigation metadata. Dashboard does not import Authentication code, decode JWTs, read Authentication storage, or implement patient, treatment, logs, backup, user-management, guideline, Bayesian model, or downstream module workflows.`
- line 5: `Backend: Python FastAPI. Local state: Dashboard sessions plus optional workspace events. Dashboard does not duplicate Authentication users or profiles. Standalone mock auth is in-memory dev/test behavior, not persisted schema.`
- line 254: `- Target module owns data, mutations, permissions beyond entry, UI, and workflow implementation.`
- line 255: `- Dashboard returns no module payload in route discovery.`

### CONTEXTUAL: `Modules/Dashboard-1.2.0/dataset-schema.md`

- line 3: `Dashboard is a workspace router. It stores only Dashboard-owned session and workspace-event state. It does not store Authentication users, Authentication profile copies, clinical patient records, treatment data, admin oversight data, guideline data, Bayesian model data, backup payloads, or downstream module data.`
- line 34: `Dashboard does not own or store these datasets:`
- line 67: `The discovery endpoint returns \`/modules/{moduleId}\` with \`placeholder: true\`. Target module owns implementation and data.`

### DIRECT: `Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783731063.47775/assembled-graph.json`

- line 203: `"summary": "Settings adapter: single source of truth for every integration knob (db_path, auth_url, patient_url, cors_origins, mock_auth, csrf_secret, module_base_path, host, port). Frozen Settings dataclass read once at import. Only place to add a new env knob.",`
- line 973: `"summary": "Canonical REST API contract: route shapes, request/response bodies, error codes, auth, CSRF, route discovery, invariants. Locked against the live router by test_unittest.TestRestContract.test_api_contract_doc_lists_every_live_route. If code and document disagree, the code wins.",`
- line 989: `"summary": "Deep-module handoff guide for future LLMs or humans. Maps the codebase architecture, design decisions, seam layout, env knobs, self-check chain, and the clinician-authority invariant.",`
- line 2251: `"description": "SQLite repository (WAL journal, thread-safe DiagnosisStore), patient identity adapter (canonical INSIGHT registry lookup), HMAC-SHA256 CSRF token, auth service delegation (Insight session + role enforcement), and the frozen settings adapter (only place to add a new env knob).",`
- line 2301: `"description": "Canonical REST API contract (locked against live router), deep-module handoff guide for future LLMs/humans, and user-facing README.",`
- line 2313: `"description": "Start with the README to understand the project: a DSM-5-TR schizophrenia criteria checklist for the Insight clinical decision support tool. Clinician-controlled \u00e2\u20ac\u201d the psychiatrist confirms or bypasses; the model never decides. Read HANDOFF.md for the architectural narrative and design decisions.",`
- line 2374: `"description": "auth.py delegates trust to the central Insight auth service (GET /api/auth/session with Cookie). CSRF protection uses HMAC-SHA256 signed double-submit tokens. config.py is the single settings adapter \u00e2\u20ac\u201d frozen Settings dataclass read once at import, only place to add a new env knob. Every consumer reads settings.* instead of scattering os.environ.get calls.",`

### DIRECT: `Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/assembled-graph.json`

- line 183: `"summary": "Settings adapter: single source of truth for every integration knob (db_path, auth_url, patient_url, cors_origins, mock_auth, csrf_secret, module_base_path, host, port). Frozen Settings dataclass read once at import. Only place to add a new env knob.",`
- line 953: `"summary": "Canonical REST API contract: route shapes, request/response bodies, error codes, auth, CSRF, route discovery, invariants. Locked against the live router by test_unittest.TestRestContract.test_api_contract_doc_lists_every_live_route. If code and document disagree, the code wins.",`
- line 969: `"summary": "Deep-module handoff guide for future LLMs or humans. Maps the codebase architecture, design decisions, seam layout, env knobs, self-check chain, and the clinician-authority invariant.",`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/batch-2.json`

- line 54: `"summary": "Settings adapter: single source of truth for every integration knob (db_path, auth_url, patient_url, cors_origins, mock_auth, csrf_secret, module_base_path, host, port). Frozen Settings dataclass read once at import. Only place to add a new env knob.",`

### DIRECT: `Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/batch-5.json`

- line 185: `"summary": "Canonical REST API contract: route shapes, request/response bodies, error codes, auth, CSRF, route discovery, invariants. Locked against the live router by test_unittest.TestRestContract.test_api_contract_doc_lists_every_live_route. If code and document disagree, the code wins.",`
- line 201: `"summary": "Deep-module handoff guide for future LLMs or humans. Maps the codebase architecture, design decisions, seam layout, env knobs, self-check chain, and the clinician-authority invariant.",`

### DIRECT: `Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/build-graph.py`

- line 104: `summary="Settings adapter: single source of truth for every integration knob (db_path, auth_url, patient_url, cors_origins, mock_auth, csrf_secret, module_base_path, host, port). Frozen Settings dataclass read once at import. The only place to add a new env knob.",`
- line 444: `summary="Canonical REST API contract: route shapes, request/response bodies, error codes, auth, CSRF, route discovery, invariants. Locked against the live router by test_unittest.TestRestContract.test_api_contract_doc_lists_every_live_route. If the code and this document disagree, the code wins.",`
- line 448: `summary="Deep-module handoff guide for future LLMs or humans. Maps the codebase architecture, design decisions, seam layout, env knobs, self-check chain, and the clinician-authority invariant.",`

### DIRECT: `Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/build-graph2.py`

- line 115: `"summary": "Settings adapter: single source of truth for every integration knob (db_path, auth_url, patient_url, cors_origins, mock_auth, csrf_secret, module_base_path, host, port). Frozen Settings dataclass read once at import. Only place to add a new env knob.",`
- line 456: `"summary": "Canonical REST API contract: route shapes, request/response bodies, error codes, auth, CSRF, route discovery, invariants. Locked against the live router by test_unittest.TestRestContract.test_api_contract_doc_lists_every_live_route. If code and document disagree, the code wins.",`
- line 460: `"summary": "Deep-module handoff guide for future LLMs or humans. Maps the codebase architecture, design decisions, seam layout, env knobs, self-check chain, and the clinician-authority invariant.",`

### DIRECT: `Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/full-graph.json`

- line 203: `"summary": "Settings adapter: single source of truth for every integration knob (db_path, auth_url, patient_url, cors_origins, mock_auth, csrf_secret, module_base_path, host, port). Frozen Settings dataclass read once at import. Only place to add a new env knob.",`
- line 973: `"summary": "Canonical REST API contract: route shapes, request/response bodies, error codes, auth, CSRF, route discovery, invariants. Locked against the live router by test_unittest.TestRestContract.test_api_contract_doc_lists_every_live_route. If code and document disagree, the code wins.",`
- line 989: `"summary": "Deep-module handoff guide for future LLMs or humans. Maps the codebase architecture, design decisions, seam layout, env knobs, self-check chain, and the clinician-authority invariant.",`
- line 2251: `"description": "SQLite repository (WAL journal, thread-safe DiagnosisStore), patient identity adapter (canonical INSIGHT registry lookup), HMAC-SHA256 CSRF token, auth service delegation (Insight session + role enforcement), and the frozen settings adapter (only place to add a new env knob).",`
- line 2301: `"description": "Canonical REST API contract (locked against live router), deep-module handoff guide for future LLMs/humans, and user-facing README.",`
- line 2313: `"description": "Start with the README to understand the project: a DSM-5-TR schizophrenia criteria checklist for the Insight clinical decision support tool. Clinician-controlled \u00e2\u20ac\u201d the psychiatrist confirms or bypasses; the model never decides. Read HANDOFF.md for the architectural narrative and design decisions.",`
- line 2374: `"description": "auth.py delegates trust to the central Insight auth service (GET /api/auth/session with Cookie). CSRF protection uses HMAC-SHA256 signed double-submit tokens. config.py is the single settings adapter \u00e2\u20ac\u201d frozen Settings dataclass read once at import, only place to add a new env knob. Every consumer reads settings.* instead of scattering os.environ.get calls.",`

### DIRECT: `Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/layers.json`

- line 62: `"description": "SQLite repository (WAL journal, thread-safe DiagnosisStore), patient identity adapter (canonical INSIGHT registry lookup), HMAC-SHA256 CSRF token, auth service delegation (Insight session + role enforcement), and the frozen settings adapter (only place to add a new env knob).",`
- line 112: `"description": "Canonical REST API contract (locked against live router), deep-module handoff guide for future LLMs/humans, and user-facing README.",`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/tour.json`

- line 5: `"description": "Start with the README to understand the project: a DSM-5-TR schizophrenia criteria checklist for the Insight clinical decision support tool. Clinician-controlled — the psychiatrist confirms or bypasses; the model never decides. Read HANDOFF.md for the architectural narrative and design decisions.",`
- line 66: `"description": "auth.py delegates trust to the central Insight auth service (GET /api/auth/session with Cookie). CSRF protection uses HMAC-SHA256 signed double-submit tokens. config.py is the single settings adapter — frozen Settings dataclass read once at import, only place to add a new env knob. Every consumer reads settings.* instead of scattering os.environ.get calls.",`

### DIRECT: `Modules/Diagnosis-1.2.0/.understand-anything/knowledge-graph.json`

- line 203: `"summary": "Settings adapter: single source of truth for every integration knob (db_path, auth_url, patient_url, cors_origins, mock_auth, csrf_secret, module_base_path, host, port). Frozen Settings dataclass read once at import. Only place to add a new env knob.",`
- line 973: `"summary": "Canonical REST API contract: route shapes, request/response bodies, error codes, auth, CSRF, route discovery, invariants. Locked against the live router by test_unittest.TestRestContract.test_api_contract_doc_lists_every_live_route. If code and document disagree, the code wins.",`
- line 989: `"summary": "Deep-module handoff guide for future LLMs or humans. Maps the codebase architecture, design decisions, seam layout, env knobs, self-check chain, and the clinician-authority invariant.",`
- line 2251: `"description": "SQLite repository (WAL journal, thread-safe DiagnosisStore), patient identity adapter (canonical INSIGHT registry lookup), HMAC-SHA256 CSRF token, auth service delegation (Insight session + role enforcement), and the frozen settings adapter (only place to add a new env knob).",`
- line 2301: `"description": "Canonical REST API contract (locked against live router), deep-module handoff guide for future LLMs/humans, and user-facing README.",`
- line 2313: `"description": "Start with the README to understand the project: a DSM-5-TR schizophrenia criteria checklist for the Insight clinical decision support tool. Clinician-controlled \u00e2\u20ac\u201d the psychiatrist confirms or bypasses; the model never decides. Read HANDOFF.md for the architectural narrative and design decisions.",`
- line 2374: `"description": "auth.py delegates trust to the central Insight auth service (GET /api/auth/session with Cookie). CSRF protection uses HMAC-SHA256 signed double-submit tokens. config.py is the single settings adapter \u00e2\u20ac\u201d frozen Settings dataclass read once at import, only place to add a new env knob. Every consumer reads settings.* instead of scattering os.environ.get calls.",`

### DIRECT: `Modules/Diagnosis-1.2.0/HANDOFF.md`

- line 3: `A guide for any future LLM (or human) that needs to read, extend, or integrate`
- line 70: `├── config.py               <- settings adapter: one \`\`Settings\`\` frozen dataclass + \`\`settings\`\` singleton sourced from the env (DB path, auth URL, patient URL, CORS origins, mock-auth flag, CSRF secret/secure, module base path, host/port). The only place to add a new integration knob; every other module reads \`\`settings.*\`\` rather than scattering \`\`os.environ.get\`\`. \`\`_config_selfcheck\`\` is run by the boot chain.`
- line 202: `(\`{code}\`) — do not reorder the \`for _sub in (...)\` tuple.`
- line 289: `the server never starts. Don't bypass this.`
- line 312: `no DB imports, no primitives-app imports. Read this before touching any`
- line 365: `are the authoritative safety net — and the boot shim still fail-fast`
- line 507: `accepted by PUT** — that's the bypass path. Do not add a server-side`
- line 576: `| Add/edit a DSM criterion | \`criteria.py :: CRITERIA\` | Update the matching case in \`test_unittest.py::TestCriteriaRules\` in the same change. The \`id\` strings are part of the API contract and the JS data-id bindings. \`criteria._demo\` is now a thin shim that runs those \`unittest\` cases — edit the cases, not the shim. |`
- line 577: `| Change a rule (e.g. duration threshold) | \`criteria.py :: evaluate()\` | Update docstring AND the matching \`test_unittest.py::TestCriteriaRules\` cases. If the rule edit adds a new *dimension* the UI's optimistic display surfaces, expose its primitive in \`criteria.meta_contract()\` AND extend \`test_meta_rules_match_engine_every_subset\` in the same change (see §9.12). The HTML \`renderLocalEvaluation\` consumes \`meta_contract\` via \`/diagnosis/_meta\` — never reimplement the rule in JS. |`
- line 579: `| Swap the persistence layer | \`store.py :: DiagnosisStore\` — add methods, keep the \`init\`/\`get\`/\`put\`/\`audit_snapshot\`/\`reset\` surface intact. | The router contract (path, request/response shape) must not change — Insight callers depend on it. Keep \`RESULT_FIELDS\`. Point at a new DB location with the \`DIAGNOSIS_DB_PATH\` env var. |`
- line 581: `| Add persistence to bypass/confirmed | Already persists in \`DiagnosisStore\` as \`decision\`, with timestamps (\`created_at\`/\`updated_at\`) and audit snapshots. As of the audit-event-seam issue \`diagnosis_api.put_session\` ALSO calls \`_dump_for_audit(code)\` after each \`store.put\` so the local \`audit\` table accumulates a chronological trail per code; the dashboard seam's \`GET /internal/diagnosis/audit/{code}\` exposes that trail to the future Insight Logs module (read-only). Update \`_store_selfcheck()\` in the same change so the contract is locked in; mirror any audit-shape change into \`TestAuditSeam\`. | The \`_dump_for_audit\` hook returns the JSON snapshot AND inserts it into the \`audit\` table via \``
- line 582: `| Add / change an integration knob | \`config.py :: Settings\` + \`\`_load\`\` — the frozen dataclass + env read is the single source for DB path, auth URL, patient URL, CORS origins, mock-auth flag, CSRF secret/secure, module base path, host/port. | Every other module reads \`\`settings.*\`\` instead of scattering \`\`os.environ.get\`\`. DO NOT add a fresh \`\`os.environ.get\`\` in another module — extend \`\`Settings\`\` + \`\`_load\`\` and re-point the consumer at it. The \`\`reset_*_for_tests\`\` hooks on \`\`auth\`\` / \`\`patient\`\` / \`\`csrf\`\` mutate *their* module globals (not the singleton) so the test surface keeps working. Update \`_config_selfcheck\` + \`test_config.py\` in the same change so the snapshot + consumer wiri`
- line 583: `| Add a Python tests beyond the self-checks | The repository already has \`test_unittest.py\` (stdlib \`\`unittest\`\`, no new deps): \`TestCriteriaRules\` (rules), \`TestRestContract\` (REST contract + persistence + patient-identity-disabled short under the bypass shim), \`TestAuditSeam\` (audit event seam — every decision-bearing PUT persists a local audit event + the dashboard \`GET /internal/diagnosis/audit/{code}\` route exposes the chronological trail, oldest first; init alone does NOT audit), \`TestClinicianAuthority\` (model-never-decides invariant, HANDOFF §6.1 — loaded by boot self-check; covers bypass-on-met AND on-unmet plus the no-auto-confirmation-from-met cases), \`TestAuthRejection\` / \`TestCS`
- line 584: `| Add / change a readiness check | \`readiness.py :: _check_<name>\` returns \`{ok: bool, ...}\` — add the key to the \`checks\` dict in \`check_readiness()\` and \`__all__\` is fine to extend. The HTTP route in \`app.py\` wraps whatever \`check_readiness()\` returns. | NEVER call a live service from readiness (it would block + leak). NEVER echo a URL / path / token / host name in the response. NEVER raise from the probe — a fault must collapse to \`{ok: False}\`. Update \`_readiness_selfcheck\` + \`test_readiness.py\` in the same change so the no-leak + no-raise contracts stay locked. Update \`__init__\` re-export + HANDOFF §9.11. |`
- line 589: `| Enforce canonical patient identity (link to Add New Patient registry) | \`patient.py :: resolve_patient\` — already wired into \`init_session\` + \`put_session\`. Flip the env \`DIAGNOSIS_PATIENT_LOOKUP=1\` at deploy; point at the registry with \`PATIENT_BASE_URL\`. (\`Settings.patient_url\` + \`Settings.patient_lookup\` surface the same values; \`patient.py\` keeps the mutable module globals for the test reset hook.) | REST contract is unchanged: \`{code}\` stays the local session key; only the row's \`patient_id\` column becomes canonical. Don't write to \`sessions.patient_id\` from outside \`resolve_patient\` — that re-introduces the diagnosis-local free-text bug. Update \`_patient_selfcheck\` + \`test_patient.py`
- line 609: `precedes it for the literal-before-parameterized invariant. Do NOT pre-nest with`
- line 618: `the server boots. Don't disable them in \`__main__.py\`. \`criteria._demo\``
- line 639: `Don't drop or rename keys without bumping the Insight integration.`
- line 643: `exempt. Don't add a new state-mutating route without wiring`
- line 665: `role/CSRF deps live ONLY in \`deps.py\` — never instantiate`
- line 692: `projection of that contract + the checked ids — it MUST NOT reimplement`
- line 697: `\`meta_contract\` and extend that test in the same change.`
- line 705: `placeholder. Don't bake a standalone shell, topbar, or \`\`Back to`
- line 744: `guard ids + thresholds all come from the server. Don't add a new DSM rule to`
- line 817: `imports cleanly and the package boots. Don't refactor to chase the`
- line 846: `\`reset_*_for_tests\` hooks — they do NOT rebuild the singleton. Don't add a`
- line 851: `- **Don't scatter \`os.environ.get\` in consumer modules.** \`config.py\` is the`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/README.md`

- line 209: `- \`{boolean}      embedded\`    — when true, the module emits no \`Insight / .dm-topbar\` header (the host dashboard already shows its own) and never mutates \`history\`.`
- line 212: `Contract the module preserves (do NOT regress):`
- line 214: `for the optimistic display — the JS NEVER reimplements the DSM logic`
- line 221: `- The module NEVER mutates the host URL, NEVER bakes a host topbar,`
- line 238: `truth, the browser never reimplements them in JS), \`GET /diagnosis/_csrf\`,`
- line 276: `\`os.environ.get\` — this is the only place to add a new integration`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/diagnosis/api.py`

- line 60: `# (parameterized \`\`/{code}\`\` family). Do not reorder.`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/diagnosis/config.py`

- line 53: `This file is the only place to add a new integration knob. Anything that`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/diagnosis/dashboard.py`

- line 98: `\`\`test_unittest.py\`\` against every id subset. Do NOT reimplement the`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/diagnosis/diagnosis_api.py`

- line 24: `evaluation objects. Don't drop or rename keys without bumping the`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/diagnosis/readiness.py`

- line 34: `Response shape (stable; do not drop keys without coordinating with the`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/docs/api-contract.md`

- line 7: `this document disagree, **the code wins** — file an issue and update`
- line 83: `not collide with \`/{code}\`. Don't reorder the \`for _sub in ()\` tuple in`
- line 186: `\`evaluate()\` reads — the UI MUST NOT reimplement the DSM logic in JS`
- line 409: `Don't drop or rename keys without bumping the Insight integration`
- line 585: `and never learns a CSRF token exists. Don't reorder them (HANDOFF`
- line 608: `without re-importing. Don't add a fresh \`os.environ.get\` in another`
- line 656: `boot. Don't disable them in \`__main__.py\`.`
- line 662: `\`evaluation\` objects. Don't drop / rename keys without bumping the`
- line 677: `owns the shared store + role/CSRF deps. Don't re-instantiate`
- line 687: `MUST NOT reimplement the DSM logic in JS — it projects from`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/test_embed.py`

- line 113: `owns navigation now; the embedded module must NOT bake any host`
- line 124: `# the guard so a future edit doesn't silently leak host URL mutations.`
- line 128: `# history.replaceState must be gated by \`\`!embedded\`\` (the host case).`
- line 138: `# The fn must early-return when embedded so the host URL is preserved.`
- line 276: `must equal the raw bytes _read_page() returns, so a future edit that`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/test_routes.py`

- line 181: `\`\`diagnosis.api\`\` directly. The split must keep them."""`

### CONTEXTUAL: `Modules/Diagnosis-1.2.0/test_unittest.py`

- line 287: `# met == (not failures). Definitional; do not add side logic.`
- line 300: `# \`\`meta_contract\`\` FIRST, not a JS constant.`
- line 470: `# updated in the same change, this fails — the README summary is`
- line 476: `"— it must ship alongside the code")`

### CONTEXTUAL: `Modules/Medical-History-1.0.0/MEDICAL_HISTORY_HANDOFF.md`

- line 27: `\`GET /api/internal/medical-history/options\` returns disease, antipsychotic, and contraindication lists. Server validation is authoritative; do not rely only on conditional UI visibility.`
- line 52: `When changing a collected field, keep these synchronized:`
- line 65: `Do not rename the internal REST routes without coordinating every parent-module integration.`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj/gen/sqlite3/sqlite3.c`

- line 16560: `/* Automatically generated.  Do not edit */`
- line 36840: `/* Automatically generated.  Do not edit */`
- line 203061: `** DO NOT EDIT THIS MACHINE GENERATED FILE.`
- line 253694: `** DO NOT EDIT THIS MACHINE GENERATED FILE.`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/better_sqlite3.target.mk`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/binding.Makefile`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/config.gypi`

- line 1: `# Do not edit. File was generated by node-gyp's "configure" step`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/deps/locate_sqlite3.target.mk`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/deps/sqlite3.Makefile`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/deps/sqlite3.target.mk`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/test_extension.target.mk`

- line 1: `# This file is generated by gyp; do not edit.`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/defines.gypi`

- line 1: `# THIS FILE IS AUTOMATICALLY GENERATED BY deps/download.sh (DO NOT EDIT)`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/download.sh`

- line 92: `printf "# THIS FILE IS AUTOMATICALLY GENERATED BY deps/download.sh (DO NOT EDIT)\n\n{\n  'defines': [\n" > "$GYP"`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/sqlite3/sqlite3.c`

- line 16560: `/* Automatically generated.  Do not edit */`
- line 36840: `/* Automatically generated.  Do not edit */`
- line 203061: `** DO NOT EDIT THIS MACHINE GENERATED FILE.`
- line 253694: `** DO NOT EDIT THIS MACHINE GENERATED FILE.`

### GENERATED/VENDORED: `Modules/Medical-History-1.0.0/node_modules/semver/package.json`

- line 54: `"//@npmcli/template-oss": "This file is partially managed by @npmcli/template-oss. Edits may be overwritten.",`

### CONTEXTUAL: `Modules/Severity-1.1.0/HANDOFF.md`

- line 3: `> Read this first. Everything you need to use, modify, or extend this module is below. If a section doesn't answer your question, the source file named in that section will.`
- line 36: `- Everything else in \`node_modules/\` is transitive Express deps. **Do not touch.**`
- line 66: `Read it end-to-end before editing. It is small on purpose.`
- line 123: `> ⚠ **There is no DELETE route.** To wipe a patient's record, edit \`data/assessments.json\` by hand. Do not add one unless the parent app genuinely needs it (see §9).`
- line 128: `- **Validation lives inline in the route**, not in a middleware. Don't extract a validator unless you have 3+ routes.`
- line 156: `There is **no state library.** Re-render is full (\`renderForm()\`) on every score click. It's cheap at 30 rows; do not optimize unless profiling says otherwise.`
- line 192: `> ⚠ **Severity bands are a clinical convention, not a law.** They live inline in this function. If a clinician asks to retune thresholds, this is the only place to edit. Do NOT silently change these — they have clinical meaning.`
- line 257: `10. **\`node_modules/\` is committed in this repo** (per \`git ls-files\`). Not normal for a real project. Don't add to it; don't prune it in a PR without asking — it may be intentional for the standalone deployment story.`
- line 275: `**To upgrade any of these:** make the smallest change that holds, leave a \`ponytail:\` comment naming what was skipped and the trigger to revisit, and don't refactor surrounding code in the same change.`
- line 289: `When you extend this module, **match the style**: read the file fully, find the smallest change that holds, leave a \`ponytail:\` comment if you cut a corner, and don't add a dependency. README §"Intentionally deferred" mirrors this ledger — keep the two in sync if you change the deferral set.`
- line 311: `3. **§9 ledger above** — before adding *anything*, check whether it's already on the deferred list and what the trigger is. Don't pay down deferrals speculatively; don't add new ones silently.`

### CONTEXTUAL: `Modules/Severity-1.1.0/README.md`

- line 29: `> **Ponytail note:** Deliberately minimal. SQLite, build tooling, and auth are intentionally deferred — add when concurrent writes, bundle size, or multi-user identity actually demand them. Each is a one-rung jump, not a rewrite.`
- line 161: `- **Clinician control** — every recommendation is followed by a psychiatrist action. Labels read \`Decision-support recommendation. Psychiatrist final review required.\` Never \`App decision\` / \`AI prescription\`.`
- line 166: `## Intentionally deferred (ponytail ledger)`
- line 168: `| Skip | Why | Add when |`

### GENERATED/VENDORED: `Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/sbcs-data-generated.js`

- line 3: `// Generated data for sbcs codec. Don't edit manually. Regenerate using generation/gen-sbcs.js script.`

### CONTEXTUAL: `Modules/Treatment-Plan/CONTEXT-MAP.md`

- line 9: `Every persisted entity instance has exactly one owning module. The owner defines its canonical identifier, schema, lifecycle, validation rules, persistence, and authoritative REST representation. Other modules may retain a versioned snapshot or cache a stable reference, but **must not read, write, migrate, attach to, or otherwise access another module's database or files**.`
- line 33: `Adding an assessment type requires updating this table before release. A type cannot be registered to two modules. Treatment Plan owns only its immutable \`ClinicalInputSnapshot\`; normalizing an assessment does not transfer ownership of the source assessment.`
- line 75: `## Prohibited coupling`

### CONTEXTUAL: `Modules/Treatment-Plan/HANDOFF.md`

- line 5: `Continue implementing the dependency-ordered Treatment Plan module while preserving standalone execution, REST-only module integration, schema-versioned data, immutable final plans, and fail-closed clinical safety gates.`
- line 43: `- **Clinical Release Blocked:** The \`check_tp01_release_gate.py\` script intentionally returns \`BLOCKED\`. This gate will only pass when all required clinical, regulatory, and privacy stakeholders provide sign-off. Do not invent stakeholder names or approvals.`
- line 72: `All automated test suites and validation scripts should pass, with the exception of \`check_tp01_release_gate.py\`, which correctly reports \`BLOCKED\`.`

### CONTEXTUAL: `Modules/Treatment-Plan/deployment/ROLLBACK.md`

- line 3: `Rollback changes only the container image. Never run down-migrations automatically: finalized plans, supersession links, edits, and provenance are immutable clinical records.`
- line 5: `Before deployment, record the current immutable image digest and create a verified database backup. Deploy only after the migration gate, standalone smoke/recovery checks, unified-route check, SBOM scan, TP-01 gate, and TP-21 human-sign-off gate pass.`
- line 7: `If health or integration checks fail, stop the new container, restore the prior image digest in \`/etc/insight/treatment-plan/container.env\`, and restart \`treatment-plan-container.service\`. Re-run readiness, unified-route, TLS/security-header, and recovery checks. Restore a database backup only after an approved data-recovery decision; an image rollback normally keeps the forward-compatible migrated database. Record the incident, image digests, schema versions, checks, approver, and timestamps in the controlled operations record.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/@oxc-project/types/types.d.ts`

- line 1: `// Auto-generated code, DO NOT EDIT DIRECTLY!`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/README.md`

- line 52: `<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->`
- line 130: `<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/README.md`

- line 55: `<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->`
- line 449: `<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/types/lexer.minimal.d.ts`

- line 2: `// Auto-generated by build/gen-min-dts.mjs — do not edit.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/is-potential-custom-element-name/index.js`

- line 1: `// Generated using \`npm run build\`. Do not edit.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/event-sets.js`

- line 1: `// This file is generated by scripts/generate-event-sets.js. Do not edit.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/flags.js`

- line 1: `// This file is autogenerated by build-prefixes.js. DO NOT EDIT!`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/targets.d.ts`

- line 1: `// This file is autogenerated by build-prefixes.js. DO NOT EDIT!`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/picomatch/README.md`

- line 722: `_(This project's readme.md is generated by [verb](https://github.com/verbose/verb-generate-readme), please don't edit the readme directly. Any changes to the readme must be made in the [.verb.md](.verb.md) readme template.)_`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/react-dom/client.js`

- line 16: `// Don't change the message. React DevTools relies on it. Also make sure`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/react-dom/index.js`

- line 16: `// Don't change the message. React DevTools relies on it. Also make sure`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/react-dom/profiling.js`

- line 16: `// Don't change the message. React DevTools relies on it. Also make sure`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/source-map-js/README.md`

- line 41: `<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/source-node.js`

- line 19: `// the source-map library are loaded. This MUST NOT CHANGE across`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/tldts/dist/cjs/index.js`

- line 950: `// Auto-generated flat public-suffix trie. Do not edit.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/tldts/dist/cjs/src/data/trie.js`

- line 4: `// Auto-generated flat public-suffix trie. Do not edit.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/tldts/dist/es6/src/data/trie.js`

- line 1: `// Auto-generated flat public-suffix trie. Do not edit.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/tldts/src/data/trie.ts`

- line 1: `// Auto-generated flat public-suffix trie. Do not edit.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/encoder.generated.js`

- line 1: `// Code generated by _scripts/generate-encoder.ts. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.generated.js`

- line 1: `// Code generated by _scripts/generate-encoder.ts. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/protocol.generated.js`

- line 1: `// Code generated by _scripts/generate-encoder.ts. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/api.js`

- line 3: `// !!! THIS FILE IS AUTO-GENERATED - DO NOT EDIT !!!`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/ast.generated.js`

- line 1: `// Code generated by _scripts/generate-ts-ast.ts. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/factory.generated.js`

- line 1: `// Code generated by _scripts/generate-ts-ast.ts. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/is.generated.js`

- line 1: `// Code generated by _scripts/generate-ts-ast.ts. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/visitor.generated.js`

- line 1: `// Code generated by _scripts/generate-ts-ast.ts. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/lsp/lsproto/lsp_generated.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/lsp/lsproto/lsp_generated.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/diagnostics/diagnostics.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/diagnostics/diagnostics.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/symbol.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/symbol.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/modifierflags.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/modifierflags.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/core/compileroptions.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/nodebuilder/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/nodebuilder/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/nodeflags.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/nodeflags.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/utilities.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/utilities.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/symbolflags.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/symbolflags.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/kind_generated.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/kind_generated.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/tokenflags.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/ast/tokenflags.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.enum.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.js`

- line 1: `// Code generated by Herebyfile.mjs generate:enums from internal/checker/types.go. DO NOT EDIT.`

### GENERATED/VENDORED: `Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/acorn.B2iPLyUM.js`

- line 1: `// This file was generated. Do not modify manually!`
- line 4: `// This file was generated. Do not modify manually!`
- line 7: `// This file was generated. Do not modify manually!`
- line 10: `// This file was generated. Do not modify manually!`

### CONTEXTUAL: `Modules/Treatment-Plan/governance/ADR-TP-04-DISPOSABLE-LIFECYCLE-PROTOTYPE.md`

- line 8: `TP-01 remains blocked for clinical release. Keep this executable conversation aid under \`prototype/\`, use synthetic data, and expose one deep module interface: \`reduce(state, action) -> new_state\`. The pure reducer has no I/O and does not mutate its input. Run its terminal adapter with \`python prototype/run_lifecycle.py\`; it prints full state after every accepted or rejected action.`
- line 10: `Delete \`prototype/\` after the walkthrough unless a later issue explicitly preserves it as research evidence. Production code must not import it.`
- line 25: `Do not fabricate acceptance. Complete after the actual session:`
- line 35: `The reducer concentrates policy behind a small test surface. It deliberately omits persistence, clocks, REST, authentication, clinical knowledge, and production adapters. Future implementation must start from approved governance, not promote this prototype mechanically.`

### CONTEXTUAL: `Modules/Treatment-Plan/governance/TP-01-SCOPE-AND-RELEASE-GATES.md`

- line 5: `**BLOCKED FOR CLINICAL RELEASE.** This package records the decisions and evidence required for release; it does not represent stakeholder approval. Architecture and research prototyping may continue only if they cannot be mistaken for clinical use.`
- line 11: `The Clinical Safety Officer must be a named individual with authority to stop release. A team name, vacancy, or generic mailbox does not satisfy the gate.`
- line 28: `Every excluded diagnosis, population, workflow, and data-quality condition must be listed in \`notSupported\`. Each entry defines observable behavior. Unsupported input must never fall through to a plausible-looking plan. Until the list is approved, the system must be treated as supporting no clinical cases.`
- line 32: `The approved matrix must define emergency triggers, user-visible instructions, generation/finalization behavior, escalation ownership, and documentation requirements. Treatment Plan must not imply that it contacts emergency services unless a separately validated integration actually does so.`
- line 40: `Clinical release is prohibited unless all of the following are true:`
- line 56: `Any approved matrix change creates a new document version and new signatures. Never edit a signed matrix in place. Signature records must bind to a canonical SHA-256 hash and point to the authoritative signing evidence.`

### CONTEXTUAL: `Modules/Treatment-Plan/governance/TP-10-BN-MAPPING-COVERAGE.md`

- line 4: `Fixture status: **synthetic candidate; BN-owner and clinical-owner approval pending**`
- line 6: `The mapper consumes only normalized snapshot facts. It never derives a clinical state from free text, scores, medication names, or missing data. A missing fact is omitted from evidence and listed in runtime coverage. A present value outside the table is also omitted and creates a typed \`unsupported-evidence-state\` finding.`
- line 21: `- Required controlled evidence before acceptance: BN owner approval of model IDs/node/state spellings and clinical owner approval that each normalized fact maps without changing meaning.`
- line 23: `No approval names, dates, or evidence references were present when TP-10 was implemented. This artifact therefore records coverage but does not claim clinical validation or release readiness.`

### CONTEXTUAL: `Modules/Treatment-Plan/governance/clinical-validation/approvals.v1.json`

- line 4: `"approvals": []`

### CONTEXTUAL: `Modules/Treatment-Plan/governance/scope-matrix.v1.json`

- line 5: `"status": "draft_pending_approval",`
- line 49: `"approvals": [],`

### CONTEXTUAL: `Modules/Treatment-Plan/scripts/check_tp01_release_gate.py`

- line 29: `failures.append("missing valid approvals: " + ", ".join(sorted(REQUIRED_ROLES - approved_roles)))`
- line 52: `failures.append("clinical validation and Clinical Safety Officer approval are required")`
- line 63: `print("TP-01 RELEASE GATE: BLOCKED")`

### CONTEXTUAL: `Modules/Treatment-Plan/scripts/check_tp21_clinical_safety_case.py`

- line 185: `print("TP-21 CLINICAL SAFETY GATE: BLOCKED")`
- line 191: `print("TP-21 CLINICAL SAFETY GATE: " + ("PASSED" if decision.approved else "BLOCKED"))`

### CONTEXTUAL: `Modules/Treatment-Plan/treatment_plan/clinical_validation.py`

- line 282: `failures.append("missing human approvals: " + ", ".join(missing))`
- line 286: `failures.append(f"{role} approval is incomplete")`
- line 288: `failures.append(f"{role} approval is not bound to this report")`
- line 294: `failures.append("psychiatrist reviewer and Clinical Safety Officer must be distinct")`

### CONTEXTUAL: `contracts/README.md`

- line 5: `Python/Node clients. Executable code is limited to reusable adapters and`
- line 6: `generated clients; domain behavior stays in each module.`

### DIRECT: `contracts/clients/node/common-contracts-client.mjs`

- line 1: `// Generated from contracts/openapi/1.0.0/common.openapi.json; do not edit.`

### DIRECT: `contracts/clients/python/common_contracts_client.py`

- line 1: `"""Generated from contracts/openapi/1.0.0/common.openapi.json; do not edit."""`

### CONTEXTUAL: `contracts/package-policy.json`

- line 3: `"description": "Shared interface artifacts only; executable code is limited to adapters and generated clients.",`
- line 4: `"allowedCodeDirectories": ["adapters", "clients"]`

### CONTEXTUAL: `deployment/WINDOWS_DOCKER_DESKTOP.md`

- line 11: `\`127.0.0.1:8080:8080\`. Do not publish module ports \`8101-8109\`.`
- line 18: `Mutable tags (\`:latest\`, \`:0.1.0\`) are rejected by verification tools.`
- line 40: `required; Desktop must allow tmpfs.`

### CONTEXTUAL: `scripts/check_architecture.py`

- line 234: `violations.append(ArchitectureViolation("CROSS_MODULE_DATABASE_PATH", uses[0][1], f"{canonical} is configured by multiple modules"))`
- line 259: `ArchitectureViolation("CROSS_MODULE_IMPORT", path, f"{source_module} imports {target}")`
- line 268: `"browser storage cannot own clinical integration state",`
- line 286: `"CROSS_MODULE_DATABASE_PATH",`
- line 297: `"SHARED_RUNTIME_JSON",`

### CONTEXTUAL: `scripts/check_common_contracts.py`

- line 171: `raise ContractError(f"domain implementation is outside allowed adapter/client roots: {relative}")`

### CONTEXTUAL: `scripts/check_deployment.py`

- line 70: `raise DeploymentContractError(f"browser source contains hard-coded localhost URL: {path}")`
- line 76: `raise DeploymentContractError(f"browser source contains hard-coded localhost URL: {path}")`

### CONTEXTUAL: `tests/test_architecture.py`

- line 34: `def test_python_cross_module_import_is_rejected(self):`
- line 44: `self.assertTrue(any(item.code == "CROSS_MODULE_IMPORT" for item in violations))`
- line 46: `def test_node_cross_module_import_is_rejected(self):`
- line 56: `self.assertTrue(any(item.code == "CROSS_MODULE_IMPORT" for item in violations))`
- line 69: `self.assertFalse(any(item.code == "CROSS_MODULE_IMPORT" for item in violations))`
- line 71: `def test_reused_sqlite_path_is_rejected(self):`
- line 82: `self.assertTrue(any(item.code == "CROSS_MODULE_DATABASE_PATH" for item in violations))`
- line 84: `def test_same_working_directory_sqlite_path_is_rejected(self):`
- line 95: `self.assertTrue(any(item.code == "CROSS_MODULE_DATABASE_PATH" for item in violations))`
- line 97: `def test_shared_runtime_json_is_rejected(self):`
- line 108: `self.assertTrue(any(item.code == "SHARED_RUNTIME_JSON" for item in violations))`
- line 110: `def test_clinical_browser_storage_is_rejected(self):`
- line 122: `self.assertTrue(any(item.code == "CLINICAL_BROWSER_STORAGE" for item in violations))`

### CONTEXTUAL: `tests/test_common_contracts.py`

- line 56: `def test_shared_package_static_rule_rejects_domain_code(self):`

### CONTEXTUAL: `tests/test_deployment_contract.py`

- line 55: `def test_browser_sources_cannot_contain_hard_coded_localhost_urls(self):`

## Complete Evaluated-File Ledger

Every regular file appears once.

```text
[CLEAR]  Modules/Add-New-Patient-1.1.0/.gitignore
[CLEAR]  Modules/Add-New-Patient-1.1.0/DESIGN.md
[CLEAR]  Modules/Add-New-Patient-1.1.0/README.md
[CLEAR]  Modules/Add-New-Patient-1.1.0/__pycache__/test_add_new_patient_backend.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/__pycache__/test_auth_adapter_contract.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/__init__.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/__pycache__/auth.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/__pycache__/config.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/__pycache__/csrf.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/__pycache__/db.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/__pycache__/main.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/__pycache__/models.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/__pycache__/repository.cpython-312.pyc
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/auth.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/config.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/csrf.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/db.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/main.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/models.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/add_new_patient_backend/repository.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/app.js
[CLEAR]  Modules/Add-New-Patient-1.1.0/data/patients.json
[MARKED] Modules/Add-New-Patient-1.1.0/docs/add-new-patient-handoff.md
[MARKED] Modules/Add-New-Patient-1.1.0/docs/api-contract.md
[CLEAR]  Modules/Add-New-Patient-1.1.0/docs/patient-domain-glossary.md
[MARKED] Modules/Add-New-Patient-1.1.0/handoff.md
[CLEAR]  Modules/Add-New-Patient-1.1.0/image1.png
[CLEAR]  Modules/Add-New-Patient-1.1.0/image2.png
[CLEAR]  Modules/Add-New-Patient-1.1.0/index.html
[CLEAR]  Modules/Add-New-Patient-1.1.0/module-config.json
[CLEAR]  Modules/Add-New-Patient-1.1.0/requirements.txt
[MARKED] Modules/Add-New-Patient-1.1.0/schema/add-new-patient.schema.json
[CLEAR]  Modules/Add-New-Patient-1.1.0/server.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/styles.css
[CLEAR]  Modules/Add-New-Patient-1.1.0/test_add_new_patient_backend.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/test_auth_adapter_contract.py
[CLEAR]  Modules/Add-New-Patient-1.1.0/test_frontend.mjs
[CLEAR]  Modules/Authentication-1.1.0/.env.example
[CLEAR]  Modules/Authentication-1.1.0/DESIGN.md
[CLEAR]  Modules/Authentication-1.1.0/README.md
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/contract.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/contract.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/disclaimer_contract.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/disclaimer_contract.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/main.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/main.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/router.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/router.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/security.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/__pycache__/security.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/contract.py
[CLEAR]  Modules/Authentication-1.1.0/contracts/examples/1.0.0/contract.json
[CLEAR]  Modules/Authentication-1.1.0/contracts/openapi/1.0.0/authentication.openapi.json
[CLEAR]  Modules/Authentication-1.1.0/contracts/schemas/1.0.0/auth-contract.schema.json
[CLEAR]  Modules/Authentication-1.1.0/contracts/schemas/1.0.0/auth-session.schema.json
[CLEAR]  Modules/Authentication-1.1.0/contracts/schemas/1.0.0/security-policy.schema.json
[CLEAR]  Modules/Authentication-1.1.0/disclaimer_contract.py
[MARKED] Modules/Authentication-1.1.0/docs/Authentication v1 Contract.md
[MARKED] Modules/Authentication-1.1.0/docs/Executive Summary.md
[CLEAR]  Modules/Authentication-1.1.0/main.py
[CLEAR]  Modules/Authentication-1.1.0/module-config.json
[CLEAR]  Modules/Authentication-1.1.0/requirements.txt
[CLEAR]  Modules/Authentication-1.1.0/router.py
[CLEAR]  Modules/Authentication-1.1.0/security.py
[CLEAR]  Modules/Authentication-1.1.0/static/index.html
[CLEAR]  Modules/Authentication-1.1.0/static/logo.png
[CLEAR]  Modules/Authentication-1.1.0/static/user-management.html
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/_support.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/_support.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_auth03_security.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_auth03_security.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_auth_discovery.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_auth_discovery.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_auth_uuid_contract.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_auth_uuid_contract.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_contract.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_contract.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_migrations.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_migrations.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_routes_auth.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_routes_auth.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_security_behavior.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_security_behavior.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_unit_security.cpython-312.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/__pycache__/test_unit_security.cpython-314.pyc
[CLEAR]  Modules/Authentication-1.1.0/tests/_support.py
[CLEAR]  Modules/Authentication-1.1.0/tests/test_auth03_security.py
[CLEAR]  Modules/Authentication-1.1.0/tests/test_auth_discovery.py
[CLEAR]  Modules/Authentication-1.1.0/tests/test_auth_uuid_contract.py
[CLEAR]  Modules/Authentication-1.1.0/tests/test_contract.py
[CLEAR]  Modules/Authentication-1.1.0/tests/test_migrations.py
[CLEAR]  Modules/Authentication-1.1.0/tests/test_routes_auth.py
[CLEAR]  Modules/Authentication-1.1.0/tests/test_security_behavior.py
[CLEAR]  Modules/Authentication-1.1.0/tests/test_unit_security.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.gitignore
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/.gitignore
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/.lock
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/CACHEDIR.TAG
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/activate
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/activate.bat
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/activate.csh
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/activate.fish
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/activate.nu
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/activate.ps1
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/activate_this.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/deactivate.bat
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/fastapi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/httpx
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/idna
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/pydoc.bat
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/uvicorn
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/__pycache__/_virtualenv.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/__pycache__/typing_extensions.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/_virtualenv.pth
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/_virtualenv.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc-0.0.4.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc-0.0.4.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc-0.0.4.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc-0.0.4.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc-0.0.4.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc-0.0.4.dist-info/entry_points.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc-0.0.4.dist-info/licenses/LICENSE
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc/__pycache__/main.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc/main.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_doc/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types-0.7.0.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types-0.7.0.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types-0.7.0.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types-0.7.0.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types-0.7.0.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types-0.7.0.dist-info/licenses/LICENSE
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/annotated_types/test_cases.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/entry_points.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/licenses/LICENSE
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/scm_file_list.json
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/scm_version.json
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/top_level.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/__pycache__/from_thread.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/__pycache__/lowlevel.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/__pycache__/to_thread.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_backends/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_backends/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_backends/__pycache__/_asyncio.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_backends/_asyncio.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_backends/_trio.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_contextmanagers.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_eventloop.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_exceptions.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_fileio.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_resources.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_signals.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_sockets.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_streams.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_subprocesses.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_synchronization.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_tasks.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_tempfile.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_testing.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/__pycache__/_typedattr.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_asyncio_selector_thread.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_contextmanagers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_eventloop.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_exceptions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_fileio.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_resources.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_signals.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_sockets.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_streams.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_subprocesses.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_synchronization.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_tasks.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_tempfile.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_testing.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/_core/_typedattr.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/__pycache__/_eventloop.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/__pycache__/_resources.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/__pycache__/_sockets.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/__pycache__/_streams.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/__pycache__/_subprocesses.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/__pycache__/_tasks.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/__pycache__/_testing.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/_eventloop.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/_resources.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/_sockets.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/_streams.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/_subprocesses.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/_tasks.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/abc/_testing.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/from_thread.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/functools.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/itertools.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/lowlevel.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/pytest_plugin.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/__pycache__/memory.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/__pycache__/stapled.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/__pycache__/tls.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/buffered.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/file.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/memory.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/stapled.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/text.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/streams/tls.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/to_interpreter.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/to_process.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/anyio/to_thread.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi-2026.7.22.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi-2026.7.22.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi-2026.7.22.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi-2026.7.22.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi-2026.7.22.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi-2026.7.22.dist-info/licenses/LICENSE
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi-2026.7.22.dist-info/top_level.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi/__main__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi/cacert.pem
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi/core.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi/tests/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/certifi/tests/test_certify.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click-8.4.2.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click-8.4.2.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click-8.4.2.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click-8.4.2.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click-8.4.2.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click-8.4.2.dist-info/licenses/LICENSE.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/_compat.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/_utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/core.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/decorators.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/exceptions.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/formatting.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/globals.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/parser.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/termui.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/types.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/__pycache__/utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/_compat.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/_termui_impl.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/_textwrap.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/_utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/_winconsole.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/core.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/decorators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/exceptions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/formatting.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/globals.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/parser.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/shell_completion.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/termui.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/testing.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/types.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/click/utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi-0.139.0.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi-0.139.0.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi-0.139.0.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi-0.139.0.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi-0.139.0.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi-0.139.0.dist-info/entry_points.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi-0.139.0.dist-info/licenses/LICENSE
[MARKED] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/SKILL.md
[MARKED] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/dependencies.md
[MARKED] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/other-tools.md
[MARKED] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/path-operations.md
[MARKED] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/pydantic.md
[MARKED] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/responses.md
[MARKED] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/.agents/skills/fastapi/references/streaming.md
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__main__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/applications.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/background.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/concurrency.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/datastructures.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/encoders.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/exception_handlers.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/exceptions.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/logger.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/param_functions.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/params.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/requests.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/responses.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/routing.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/sse.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/staticfiles.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/testclient.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/types.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/__pycache__/websockets.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/_compat/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/_compat/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/_compat/__pycache__/shared.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/_compat/__pycache__/v2.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/_compat/shared.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/_compat/v2.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/applications.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/background.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/cli.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/concurrency.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/datastructures.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/dependencies/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/dependencies/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/dependencies/__pycache__/models.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/dependencies/__pycache__/utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/dependencies/models.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/encoders.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/exception_handlers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/exceptions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/logger.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/middleware/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/middleware/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/middleware/__pycache__/asyncexitstack.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/middleware/asyncexitstack.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/middleware/cors.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/middleware/gzip.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/middleware/httpsredirect.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/middleware/trustedhost.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/middleware/wsgi.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/__pycache__/constants.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/__pycache__/docs.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/__pycache__/models.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/__pycache__/utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/constants.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/docs.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/models.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/openapi/utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/param_functions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/params.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/requests.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/responses.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/routing.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/__pycache__/api_key.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/__pycache__/base.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/__pycache__/http.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/__pycache__/oauth2.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/__pycache__/open_id_connect_url.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/__pycache__/utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/api_key.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/base.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/http.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/oauth2.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/open_id_connect_url.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/security/utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/sse.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/staticfiles.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/templating.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/testclient.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/types.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/fastapi/websockets.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11-0.16.0.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11-0.16.0.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11-0.16.0.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11-0.16.0.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11-0.16.0.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11-0.16.0.dist-info/licenses/LICENSE.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11-0.16.0.dist-info/top_level.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_abnf.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_connection.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_events.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_headers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_readers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_receivebuffer.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_state.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_util.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_version.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/_writers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/h11/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore-1.0.9.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore-1.0.9.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore-1.0.9.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore-1.0.9.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore-1.0.9.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore-1.0.9.dist-info/licenses/LICENSE.md
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_api.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_async/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_async/connection.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_async/connection_pool.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_async/http11.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_async/http2.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_async/http_proxy.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_async/interfaces.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_async/socks_proxy.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_backends/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_backends/anyio.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_backends/auto.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_backends/base.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_backends/mock.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_backends/sync.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_backends/trio.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_exceptions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_models.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_ssl.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_sync/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_sync/connection.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_sync/connection_pool.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_sync/http11.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_sync/http2.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_sync/http_proxy.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_sync/interfaces.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_sync/socks_proxy.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_synchronization.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_trace.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/_utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpcore/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx-0.28.1.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx-0.28.1.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx-0.28.1.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx-0.28.1.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx-0.28.1.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx-0.28.1.dist-info/entry_points.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx-0.28.1.dist-info/licenses/LICENSE.md
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/__version__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_api.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_auth.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_client.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_config.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_content.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_decoders.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_exceptions.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_main.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_models.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_multipart.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_status_codes.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_types.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_urlparse.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_urls.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__pycache__/_utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/__version__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_api.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_auth.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_client.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_config.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_content.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_decoders.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_exceptions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_main.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_models.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_multipart.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_status_codes.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/__pycache__/asgi.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/__pycache__/base.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/__pycache__/default.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/__pycache__/mock.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/__pycache__/wsgi.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/asgi.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/base.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/default.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/mock.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_transports/wsgi.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_types.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_urlparse.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_urls.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/_utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/httpx/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna-3.18.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna-3.18.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna-3.18.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna-3.18.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna-3.18.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna-3.18.dist-info/entry_points.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna-3.18.dist-info/licenses/LICENSE.md
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/__main__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/__pycache__/core.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/__pycache__/idnadata.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/__pycache__/intranges.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/__pycache__/package_data.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/cli.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/codec.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/compat.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/core.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/idnadata.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/intranges.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/package_data.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/idna/uts46data.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml-6.1.1.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml-6.1.1.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml-6.1.1.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml-6.1.1.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml-6.1.1.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml-6.1.1.dist-info/licenses/LICENSE.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml-6.1.1.dist-info/licenses/LICENSES.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml-6.1.1.dist-info/top_level.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/ElementInclude.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/_elementpath.cpython-312-x86_64-linux-gnu.so
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/_elementpath.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/apihelpers.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/builder.cpython-312-x86_64-linux-gnu.so
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/builder.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/classlookup.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/cleanup.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/cssselect.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/debug.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/docloader.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/doctestcompare.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/dtd.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/etree.cpython-312-x86_64-linux-gnu.so
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/etree.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/etree.pyx
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/etree_api.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/extensions.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/ElementSoup.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/_diffcommand.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/_difflib.cpython-312-x86_64-linux-gnu.so
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/_difflib.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/_html5builder.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/_setmixin.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/builder.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/clean.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/defs.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/diff.cpython-312-x86_64-linux-gnu.so
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/diff.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/formfill.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/html5parser.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/soupparser.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/html/usedoctest.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/__init__.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/c14n.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/config.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/dtdvalid.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/etree_defs.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/etreepublic.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/extlibs/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/extlibs/libcharset.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/extlibs/localcharset.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/extlibs/zconf.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/extlibs/zlib.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/htmlparser.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libexslt/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libexslt/exslt.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libexslt/exsltconfig.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libexslt/exsltexports.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/HTMLparser.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/HTMLtree.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/SAX.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/SAX2.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/c14n.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/catalog.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/chvalid.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/debugXML.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/dict.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/encoding.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/entities.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/globals.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/hash.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/list.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/nanoftp.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/nanohttp.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/parser.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/parserInternals.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/relaxng.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/schemasInternals.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/schematron.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/threads.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/tree.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/uri.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/valid.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xinclude.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xlink.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlIO.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlautomata.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlerror.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlexports.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlmemory.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlmodule.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlreader.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlregexp.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlsave.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlschemas.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlschemastypes.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlstring.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlunicode.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlversion.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xmlwriter.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xpath.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xpathInternals.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxml/xpointer.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/attributes.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/documents.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/extensions.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/extra.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/functions.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/imports.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/keys.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/namespaces.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/numbersInternals.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/pattern.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/preproc.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/security.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/templates.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/transform.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/variables.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/xslt.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/xsltInternals.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/xsltconfig.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/xsltexports.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/xsltlocale.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/libxslt/xsltutils.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/lxml-version.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/relaxng.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/schematron.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/tree.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/uri.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/xinclude.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/xmlerror.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/xmlparser.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/xmlschema.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/xpath.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/includes/xslt.pxd
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/resources/rng/iso-schematron.rng
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/resources/xsl/RNG2Schtrn.xsl
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/resources/xsl/XSD2Schtrn.xsl
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/resources/xsl/iso-schematron-xslt1/iso_abstract_expand.xsl
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/resources/xsl/iso-schematron-xslt1/iso_dsdl_include.xsl
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/resources/xsl/iso-schematron-xslt1/iso_schematron_message.xsl
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/resources/xsl/iso-schematron-xslt1/iso_schematron_skeleton_for_xslt1.xsl
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/resources/xsl/iso-schematron-xslt1/iso_svrl_for_xslt1.xsl
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/isoschematron/resources/xsl/iso-schematron-xslt1/readme.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/iterparse.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/lxml.etree.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/lxml.etree_api.h
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/nsclasses.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/objectify.cpython-312-x86_64-linux-gnu.so
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/objectify.pyx
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/objectpath.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/parser.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/parsertarget.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/proxy.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/public-api.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/pyclasslookup.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/readonlytree.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/relaxng.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/sax.cpython-312-x86_64-linux-gnu.so
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/sax.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/saxparser.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/schematron.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/serializer.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/usedoctest.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/xinclude.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/xmlerror.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/xmlid.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/xmlschema.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/xpath.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/xslt.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/lxml/xsltext.pxi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic-2.13.4.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic-2.13.4.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic-2.13.4.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic-2.13.4.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic-2.13.4.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic-2.13.4.dist-info/licenses/LICENSE
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/_migration.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/aliases.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/annotated_handlers.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/color.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/config.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/errors.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/fields.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/functional_validators.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/json_schema.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/main.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/networks.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/type_adapter.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/types.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/version.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/__pycache__/warnings.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_config.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_core_metadata.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_core_utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_decorators.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_discriminated_union.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_docs_extraction.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_fields.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_forward_ref.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_generate_schema.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_generics.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_import_utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_internal_dataclass.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_known_annotated_metadata.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_mock_val_ser.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_model_construction.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_namespace_utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_repr.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_schema_gather.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_schema_generation_shared.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_signature.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_typing_extra.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_validators.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_config.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_core_metadata.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_core_utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_dataclasses.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_decorators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_decorators_v1.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_discriminated_union.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_docs_extraction.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_fields.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_forward_ref.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_generics.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_git.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_import_utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_internal_dataclass.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_known_annotated_metadata.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_mock_val_ser.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_namespace_utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_repr.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_schema_gather.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_schema_generation_shared.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_serializers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_signature.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_typing_extra.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_validate_call.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_internal/_validators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/_migration.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/alias_generators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/aliases.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/annotated_handlers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/class_validators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/color.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/config.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/dataclasses.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/datetime_parse.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/decorator.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/deprecated/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/deprecated/class_validators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/deprecated/config.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/deprecated/copy_internals.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/deprecated/decorator.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/deprecated/json.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/deprecated/parse.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/deprecated/tools.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/env_settings.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/error_wrappers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/errors.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/experimental/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/experimental/arguments_schema.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/experimental/missing_sentinel.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/experimental/pipeline.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/fields.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/functional_serializers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/functional_validators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/generics.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/json.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/json_schema.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/main.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/mypy.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/networks.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/parse.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/plugin/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/plugin/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/plugin/__pycache__/_loader.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/plugin/__pycache__/_schema_validator.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/plugin/_loader.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/plugin/_schema_validator.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/root_model.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/schema.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/tools.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/type_adapter.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/types.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/typing.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/annotated_types.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/class_validators.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/color.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/config.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/dataclasses.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/datetime_parse.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/decorator.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/env_settings.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/error_wrappers.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/errors.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/fields.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/json.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/main.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/networks.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/parse.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/schema.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/tools.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/types.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/typing.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/validators.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/__pycache__/version.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/_hypothesis_plugin.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/annotated_types.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/class_validators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/color.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/config.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/dataclasses.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/datetime_parse.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/decorator.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/env_settings.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/error_wrappers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/errors.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/fields.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/generics.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/json.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/main.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/mypy.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/networks.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/parse.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/schema.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/tools.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/types.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/typing.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/validators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/v1/version.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/validate_call_decorator.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/validators.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/version.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic/warnings.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core-2.46.4.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core-2.46.4.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core-2.46.4.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core-2.46.4.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core-2.46.4.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core-2.46.4.dist-info/licenses/LICENSE
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core-2.46.4.dist-info/sboms/pydantic-core.cyclonedx.json
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core/__pycache__/core_schema.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core/_pydantic_core.cpython-312-x86_64-linux-gnu.so
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core/_pydantic_core.pyi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core/core_schema.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/pydantic_core/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette-1.3.1.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette-1.3.1.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette-1.3.1.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette-1.3.1.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette-1.3.1.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette-1.3.1.dist-info/licenses/LICENSE.md
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/_exception_handler.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/_utils.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/applications.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/background.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/concurrency.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/convertors.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/datastructures.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/exceptions.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/formparsers.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/requests.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/responses.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/routing.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/staticfiles.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/status.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/testclient.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/types.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/__pycache__/websockets.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/_exception_handler.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/_utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/applications.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/authentication.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/background.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/concurrency.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/config.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/convertors.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/datastructures.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/endpoints.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/exceptions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/formparsers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/__pycache__/base.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/__pycache__/errors.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/__pycache__/exceptions.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/authentication.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/base.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/cors.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/errors.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/exceptions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/gzip.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/httpsredirect.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/sessions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/trustedhost.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/middleware/wsgi.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/requests.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/responses.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/routing.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/schemas.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/staticfiles.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/status.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/templating.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/testclient.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/types.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/starlette/websockets.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_extensions-4.16.0.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_extensions-4.16.0.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_extensions-4.16.0.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_extensions-4.16.0.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_extensions-4.16.0.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_extensions-4.16.0.dist-info/licenses/LICENSE
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_extensions.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection-0.4.2.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection-0.4.2.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection-0.4.2.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection-0.4.2.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection-0.4.2.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection-0.4.2.dist-info/licenses/LICENSE
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection/__pycache__/introspection.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection/__pycache__/typing_objects.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection/introspection.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection/typing_objects.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/typing_inspection/typing_objects.pyi
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn-0.50.2.dist-info/INSTALLER
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn-0.50.2.dist-info/METADATA
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn-0.50.2.dist-info/RECORD
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn-0.50.2.dist-info/REQUESTED
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn-0.50.2.dist-info/WHEEL
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn-0.50.2.dist-info/entry_points.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn-0.50.2.dist-info/licenses/LICENSE.md
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__main__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/_ansi.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/_compat.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/_subprocess.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/_types.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/config.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/importer.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/logging.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/main.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/__pycache__/server.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/_ansi.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/_compat.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/_subprocess.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/_types.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/config.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/importer.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/lifespan/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/lifespan/off.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/lifespan/on.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/logging.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/loops/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/loops/asyncio.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/loops/auto.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/loops/uvloop.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/main.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/__pycache__/asgi2.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/__pycache__/message_logger.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/__pycache__/proxy_headers.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/__pycache__/wsgi.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/asgi2.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/message_logger.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/middleware/wsgi.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/http/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/http/auto.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/http/flow_control.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/http/h11_impl.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/utils.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/websockets/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/websockets/auto.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/websockets/websockets_impl.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/websockets/websockets_sansio_impl.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/protocols/websockets/wsproto_impl.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/py.typed
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/server.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/__pycache__/basereload.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/__pycache__/multiprocess.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/__pycache__/statreload.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/__pycache__/watchfilesreload.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/basereload.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/multiprocess.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/statreload.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/supervisors/watchfilesreload.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib/python3.12/site-packages/uvicorn/workers.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/pyvenv.cfg
[MARKED] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/CONTEXT.md
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/README.md
[MARKED] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/UBIQUITOUS_LANGUAGE.md
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/__pycache__/auth_adapter.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/__pycache__/config.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/__pycache__/evaluation_store.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/__pycache__/evidence_schema.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/__pycache__/main.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/__pycache__/model_governance.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/__pycache__/model_registry.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/auth_adapter.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/config.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/evaluation_store.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/evidence_schema.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/main.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/model_governance.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/model_registry.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/model_registry/schemas/XSD.xml
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/model_registry/xml/BN-Clozapine-in-Suicide-Risk.xml
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/model_registry/xml/BN-Involuntary-Treatment-Considerations.xml
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/model_registry/xml/BN-Pharmacotherapy.xml
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/model_registry/xml/BN-Treatment-Setting.xml
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/server.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/bn_manager_backend/static/index.html
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/__init__.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/__pycache__/contract.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/__pycache__/evaluation.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/__pycache__/model.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/__pycache__/tables.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/__pycache__/validation.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/__pycache__/xmlbif_compiler.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/contract.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/evaluation.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/model.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/tables.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/validation.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/clinical_graph_models/xmlbif_compiler.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/data/bn-manager.sqlite3
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/data/bn-manager.sqlite3-shm
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/data/bn-manager.sqlite3-wal
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/docs/XML-BN-MIGRATION.md
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/main.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/pyproject.toml
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/requirements-dev.txt
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/server.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/__pycache__/test_auth_adapter.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/__pycache__/test_bn_manager_backend.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/__pycache__/test_contract.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/__pycache__/test_evaluation_store.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/__pycache__/test_model_governance.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/__pycache__/test_validation.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/__pycache__/test_xmlbif_compiler.cpython-312.pyc
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_auth_adapter.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_bn_manager_backend.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_contract.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_evaluation_store.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_model_governance.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_validation.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/tests/test_xmlbif_compiler.py
[CLEAR]  Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/uv.lock
[CLEAR]  Modules/BN-Manager-v.1.1.0/module-config.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/assemble-review.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/assembled-graph.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/batch-2.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/batches.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/fingerprint-input.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/layers.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/review.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/layers.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-arch-analyze.js
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-arch-input.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-arch-results.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-file-analyzer-input-1.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-file-analyzer-input-2.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-file-extract-results-2.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-finalize.cjs
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-import-map-input.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-import-map-output.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-scan-files.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-tour-analyze.js
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-tour-input.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tmp/ua-tour-results.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.trash-1783875387/tour.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/.understandignore
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/config.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/dashboard.err.log
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/dashboard.out.log
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/fingerprints.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/intermediate/scan-result.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/knowledge-graph.json
[CLEAR]  Modules/DDI-Checker-1.2.0/.understand-anything/meta.json
[CLEAR]  Modules/DDI-Checker-1.2.0/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/data/active-kb.json
[CLEAR]  Modules/DDI-Checker-1.2.0/data/ddi-checker.sqlite3
[CLEAR]  Modules/DDI-Checker-1.2.0/data/ddi-checker.sqlite3-shm
[CLEAR]  Modules/DDI-Checker-1.2.0/data/ddi-checker.sqlite3-wal
[CLEAR]  Modules/DDI-Checker-1.2.0/graphs/architecture.md
[CLEAR]  Modules/DDI-Checker-1.2.0/index.html
[CLEAR]  Modules/DDI-Checker-1.2.0/module-config.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/.package-lock.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/base64-js/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/base64-js/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/base64-js/base64js.min.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/base64-js/index.d.ts
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/base64-js/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/base64-js/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/binding.gyp
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Makefile
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/better_sqlite3.node.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/better_sqlite3.node.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/better_sqlite3/src/better_sqlite3.o.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/deps/locate_sqlite3.stamp.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/deps/sqlite3.a.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/sqlite3/gen/sqlite3/sqlite3.o.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/test_extension.node.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/test_extension/deps/test_extension.o.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/sqlite3.a.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/Release/test_extension.node.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/.deps/ba23eeee118cd63e16015df367567cb043fed872.intermediate.d
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/better_sqlite3.node
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj.target/better_sqlite3.node
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj.target/better_sqlite3/src/better_sqlite3.o
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj.target/deps/locate_sqlite3.stamp
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj.target/deps/sqlite3.a
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj.target/sqlite3/gen/sqlite3/sqlite3.o
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj.target/test_extension.node
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj.target/test_extension/deps/test_extension.o
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj/gen/sqlite3/sqlite3.c
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj/gen/sqlite3/sqlite3.h
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/obj/gen/sqlite3/sqlite3ext.h
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/sqlite3.a
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/Release/test_extension.node
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/better_sqlite3.target.mk
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/binding.Makefile
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/config.gypi
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/deps/locate_sqlite3.target.mk
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/deps/sqlite3.Makefile
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/deps/sqlite3.target.mk
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/test_extension.target.mk
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/common.gypi
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/copy.js
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/defines.gypi
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/download.sh
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/sqlite3.gyp
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/sqlite3/sqlite3.c
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/sqlite3/sqlite3.h
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/sqlite3/sqlite3ext.h
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/deps/test_extension.c
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/database.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/methods/aggregate.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/methods/backup.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/methods/function.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/methods/inspect.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/methods/pragma.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/methods/serialize.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/methods/table.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/methods/transaction.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/methods/wrappers.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/sqlite-error.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/lib/util.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/src/better_sqlite3.cpp
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/src/better_sqlite3.hpp
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bindings/LICENSE.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bindings/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bindings/bindings.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bindings/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/.travis.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/BufferList.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/LICENSE.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/bl.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/test/convert.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/test/indexOf.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/test/isBufferList.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/bl/test/test.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/buffer/AUTHORS.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/buffer/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/buffer/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/buffer/index.d.ts
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/buffer/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/buffer/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/chownr/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/chownr/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/chownr/chownr.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/chownr/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/decompress-response/index.d.ts
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/decompress-response/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/decompress-response/license
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/decompress-response/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/decompress-response/readme.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/deep-extend/CHANGELOG.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/deep-extend/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/deep-extend/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/deep-extend/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/deep-extend/lib/deep-extend.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/deep-extend/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/detect-libc/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/detect-libc/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/detect-libc/index.d.ts
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/detect-libc/lib/detect-libc.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/detect-libc/lib/elf.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/detect-libc/lib/filesystem.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/detect-libc/lib/process.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/detect-libc/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/end-of-stream/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/end-of-stream/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/end-of-stream/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/end-of-stream/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/expand-template/.travis.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/expand-template/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/expand-template/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/expand-template/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/expand-template/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/expand-template/test.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/.npmignore
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/.travis.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/History.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/index.d.ts
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/test/test.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/file-uri-to-path/test/tests.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/fs-constants/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/fs-constants/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/fs-constants/browser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/fs-constants/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/fs-constants/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/.travis.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/example/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/example/url.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/readme.markdown
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/test/a.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/test/b.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/test/c.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/test/d.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/test/e.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/github-from-package/test/url.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/ieee754/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/ieee754/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/ieee754/index.d.ts
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/ieee754/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/ieee754/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/inherits/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/inherits/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/inherits/inherits.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/inherits/inherits_browser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/inherits/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/ini/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/ini/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/ini/ini.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/ini/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/mimic-response/index.d.ts
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/mimic-response/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/mimic-response/license
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/mimic-response/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/mimic-response/readme.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/.eslintrc
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/.github/FUNDING.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/.nycrc
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/CHANGELOG.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/example/parse.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/all_bool.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/bool.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/dash.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/default_bool.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/dotted.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/kv_short.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/long.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/num.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/parse.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/parse_modified.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/proto.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/short.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/stop_early.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/unknown.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/minimist/test/whitespace.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/mkdirp-classic/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/mkdirp-classic/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/mkdirp-classic/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/mkdirp-classic/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/napi-build-utils/.github/workflows/run-npm-tests.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/napi-build-utils/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/napi-build-utils/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/napi-build-utils/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/napi-build-utils/index.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/napi-build-utils/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/node-abi/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/node-abi/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/node-abi/abi_registry.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/node-abi/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/node-abi/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/once/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/once/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/once/once.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/once/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/CHANGELOG.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/CONTRIBUTING.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/asset.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/bin.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/download.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/error.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/help.txt
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/log.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/proxy.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/rc.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/prebuild-install/util.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/.github/FUNDING.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/.travis.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/SECURITY.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/empty.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/test-browser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/pump/test-node.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/LICENSE.APACHE2
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/LICENSE.BSD
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/LICENSE.MIT
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/browser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/cli.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/lib/utils.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/test/ini.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/test/nested-env-vars.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/rc/test/test.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/CONTRIBUTING.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/GOVERNANCE.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/errors-browser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/errors.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/experimentalWarning.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/_stream_duplex.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/_stream_passthrough.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/_stream_readable.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/_stream_transform.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/_stream_writable.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/async_iterator.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/buffer_list.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/destroy.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/end-of-stream.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/from-browser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/from.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/pipeline.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/state.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/stream-browser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/lib/internal/streams/stream.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/readable-browser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/readable-stream/readable.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/safe-buffer/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/safe-buffer/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/safe-buffer/index.d.ts
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/safe-buffer/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/safe-buffer/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/bin/semver.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/classes/comparator.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/classes/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/classes/range.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/classes/semver.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/clean.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/cmp.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/coerce.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/compare-build.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/compare-loose.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/compare.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/diff.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/eq.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/gt.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/gte.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/inc.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/lt.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/lte.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/major.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/minor.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/neq.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/parse.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/patch.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/prerelease.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/rcompare.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/rsort.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/satisfies.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/sort.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/truncate.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/functions/valid.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/internal/constants.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/internal/debug.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/internal/identifiers.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/internal/lrucache.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/internal/parse-options.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/internal/re.js
[MARKED] Modules/DDI-Checker-1.2.0/node_modules/semver/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/preload.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/range.bnf
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/gtr.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/intersects.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/ltr.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/max-satisfying.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/min-satisfying.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/min-version.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/outside.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/simplify.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/subset.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/to-comparators.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/semver/ranges/valid.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-concat/.travis.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-concat/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-concat/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-concat/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-concat/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-concat/test/basic.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-get/.github/dependabot.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-get/.github/workflows/ci.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-get/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-get/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-get/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/simple-get/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/string_decoder/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/string_decoder/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/string_decoder/lib/string_decoder.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/string_decoder/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/strip-json-comments/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/strip-json-comments/license
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/strip-json-comments/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/strip-json-comments/readme.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/.travis.yml
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/a/hello.txt
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/b/a/test.txt
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/d/file1
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/d/file2
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/d/sub-dir/file5
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/d/sub-files/file3
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/d/sub-files/file4
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/e/directory/.ignore
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/e/file
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/fixtures/invalid.tar
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-fs/test/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-stream/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-stream/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-stream/extract.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-stream/headers.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-stream/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-stream/pack.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-stream/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tar-stream/sandbox.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tunnel-agent/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tunnel-agent/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tunnel-agent/index.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/tunnel-agent/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/util-deprecate/History.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/util-deprecate/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/util-deprecate/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/util-deprecate/browser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/util-deprecate/node.js
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/util-deprecate/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/wrappy/LICENSE
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/wrappy/README.md
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/wrappy/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/node_modules/wrappy/wrappy.js
[CLEAR]  Modules/DDI-Checker-1.2.0/package-lock.json
[CLEAR]  Modules/DDI-Checker-1.2.0/package.json
[CLEAR]  Modules/DDI-Checker-1.2.0/scripts/ingest.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/scripts/repair-bundled-kb.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/scripts/validate-kb.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/src/app.js
[CLEAR]  Modules/DDI-Checker-1.2.0/src/auth-adapter.js
[CLEAR]  Modules/DDI-Checker-1.2.0/src/ddi-engine.js
[CLEAR]  Modules/DDI-Checker-1.2.0/src/ddi-rest-adapter.cjs
[CLEAR]  Modules/DDI-Checker-1.2.0/src/kb-persistence.js
[CLEAR]  Modules/DDI-Checker-1.2.0/src/kb-sqlite.cjs
[CLEAR]  Modules/DDI-Checker-1.2.0/src/kb-validator.cjs
[CLEAR]  Modules/DDI-Checker-1.2.0/src/report-parser.js
[CLEAR]  Modules/DDI-Checker-1.2.0/src/server.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/src/storage-adapter.js
[CLEAR]  Modules/DDI-Checker-1.2.0/src/styles.css
[CLEAR]  Modules/DDI-Checker-1.2.0/test/auth-adapter.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/ci-contract.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/ddi-05-identity-evidence.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/ddi-authoritative-engine.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/ddi-engine.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/ddi-kb-sqlite.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/ddi-rest-contract.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/ddi-rest-seam.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/fixtures/kb/malformed-records.json
[CLEAR]  Modules/DDI-Checker-1.2.0/test/fixtures/kb/malformed-root.json
[CLEAR]  Modules/DDI-Checker-1.2.0/test/fixtures/kb/valid-pending.json
[CLEAR]  Modules/DDI-Checker-1.2.0/test/fixtures/reports/compact-list.txt
[CLEAR]  Modules/DDI-Checker-1.2.0/test/fixtures/reports/long-form.txt
[CLEAR]  Modules/DDI-Checker-1.2.0/test/fixtures/reports/malformed.txt
[CLEAR]  Modules/DDI-Checker-1.2.0/test/ingest.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/kb-persistence.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/storage-adapter.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/ui-source.test.mjs
[CLEAR]  Modules/DDI-Checker-1.2.0/test/validate-kb.test.mjs
[CLEAR]  Modules/Dashboard-1.2.0/.gitignore
[MARKED] Modules/Dashboard-1.2.0/HANDOFF.md
[MARKED] Modules/Dashboard-1.2.0/README.md
[CLEAR]  Modules/Dashboard-1.2.0/__pycache__/test_dashboard_backend.cpython-312.pyc
[MARKED] Modules/Dashboard-1.2.0/api-contract.md
[CLEAR]  Modules/Dashboard-1.2.0/dashboard.js
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/__init__.py
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/__pycache__/auth.cpython-312.pyc
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/__pycache__/config.cpython-312.pyc
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/__pycache__/db.cpython-312.pyc
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/__pycache__/discovery.cpython-312.pyc
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/__pycache__/main.cpython-312.pyc
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/__pycache__/repository.cpython-312.pyc
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/auth.py
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/config.py
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/db.py
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/discovery.py
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/main.py
[CLEAR]  Modules/Dashboard-1.2.0/dashboard_backend/repository.py
[MARKED] Modules/Dashboard-1.2.0/dataset-schema.md
[CLEAR]  Modules/Dashboard-1.2.0/index.html
[CLEAR]  Modules/Dashboard-1.2.0/module-config.json
[CLEAR]  Modules/Dashboard-1.2.0/package.json
[CLEAR]  Modules/Dashboard-1.2.0/requirements.txt
[CLEAR]  Modules/Dashboard-1.2.0/server.py
[CLEAR]  Modules/Dashboard-1.2.0/styles.css
[CLEAR]  Modules/Dashboard-1.2.0/test_dashboard_backend.py
[CLEAR]  Modules/Dashboard-1.2.0/test_dashboard_frontend.mjs
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783731063.47775/assembled-graph.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783731063.47775/review.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/add-tests.py
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/assemble-final.py
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/assembled-graph.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/batch-1.json
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/batch-2.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/batch-3.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/batch-4.json
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/batch-5.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/batches.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/build-fp-input.py
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/build-graph.py
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/build-graph2.py
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/fingerprint-input.json
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/full-graph.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/import-map-input.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/import-map.json
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/layers.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/review.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/scan-output-from-script.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/tmp/ua-inline-validate.cjs
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/.trash-1783755237/tour.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/.understandignore
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/fingerprints.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/intermediate/scan-result.json
[MARKED] Modules/Diagnosis-1.2.0/.understand-anything/knowledge-graph.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/meta.json
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/vite-stderr.log
[CLEAR]  Modules/Diagnosis-1.2.0/.understand-anything/vite-stdout.log
[MARKED] Modules/Diagnosis-1.2.0/HANDOFF.md
[MARKED] Modules/Diagnosis-1.2.0/README.md
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_auth.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_config.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_csrf.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_discovery.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_embed.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_patient.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_readiness.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_routes.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_support.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/__pycache__/test_unittest.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__init__.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__main__.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/__main__.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/api.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/app.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/auth.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/config.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/contract.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/criteria.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/csrf.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/dashboard.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/deps.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/diagnosis_api.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/page.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/patient.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/readiness.cpython-312.pyc
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/__pycache__/store.cpython-312.pyc
[MARKED] Modules/Diagnosis-1.2.0/diagnosis/api.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/app.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/auth.py
[MARKED] Modules/Diagnosis-1.2.0/diagnosis/config.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/contract.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/criteria.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/csrf.py
[MARKED] Modules/Diagnosis-1.2.0/diagnosis/dashboard.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/deps.py
[MARKED] Modules/Diagnosis-1.2.0/diagnosis/diagnosis_api.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/page.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/patient.py
[MARKED] Modules/Diagnosis-1.2.0/diagnosis/readiness.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/static/index.html
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis/store.py
[CLEAR]  Modules/Diagnosis-1.2.0/diagnosis_store.db
[MARKED] Modules/Diagnosis-1.2.0/docs/api-contract.md
[CLEAR]  Modules/Diagnosis-1.2.0/module-config.json
[CLEAR]  Modules/Diagnosis-1.2.0/requirements.txt
[CLEAR]  Modules/Diagnosis-1.2.0/t.py
[CLEAR]  Modules/Diagnosis-1.2.0/test_auth.py
[CLEAR]  Modules/Diagnosis-1.2.0/test_config.py
[CLEAR]  Modules/Diagnosis-1.2.0/test_csrf.py
[CLEAR]  Modules/Diagnosis-1.2.0/test_discovery.py
[MARKED] Modules/Diagnosis-1.2.0/test_embed.py
[CLEAR]  Modules/Diagnosis-1.2.0/test_output.txt
[CLEAR]  Modules/Diagnosis-1.2.0/test_patient.py
[CLEAR]  Modules/Diagnosis-1.2.0/test_readiness.py
[MARKED] Modules/Diagnosis-1.2.0/test_routes.py
[CLEAR]  Modules/Diagnosis-1.2.0/test_support.py
[MARKED] Modules/Diagnosis-1.2.0/test_unittest.py
[MARKED] Modules/Medical-History-1.0.0/MEDICAL_HISTORY_HANDOFF.md
[CLEAR]  Modules/Medical-History-1.0.0/README.md
[CLEAR]  Modules/Medical-History-1.0.0/auth-adapter.js
[CLEAR]  Modules/Medical-History-1.0.0/data/activation_sessions.json
[CLEAR]  Modules/Medical-History-1.0.0/data/medical_history_schema.json
[CLEAR]  Modules/Medical-History-1.0.0/data/medical_history_submissions.json
[CLEAR]  Modules/Medical-History-1.0.0/medical-history-submission.js
[CLEAR]  Modules/Medical-History-1.0.0/module-config.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/.package-lock.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/base64-js/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/base64-js/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/base64-js/base64js.min.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/base64-js/index.d.ts
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/base64-js/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/base64-js/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/binding.gyp
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Makefile
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/better_sqlite3.node.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/better_sqlite3.node.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/better_sqlite3/src/better_sqlite3.o.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/deps/locate_sqlite3.stamp.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/deps/sqlite3.a.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/sqlite3/gen/sqlite3/sqlite3.o.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/test_extension.node.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/obj.target/test_extension/deps/test_extension.o.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/sqlite3.a.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/Release/test_extension.node.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/.deps/ba23eeee118cd63e16015df367567cb043fed872.intermediate.d
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/better_sqlite3.node
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj.target/better_sqlite3.node
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj.target/better_sqlite3/src/better_sqlite3.o
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj.target/deps/locate_sqlite3.stamp
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj.target/deps/sqlite3.a
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj.target/sqlite3/gen/sqlite3/sqlite3.o
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj.target/test_extension.node
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj.target/test_extension/deps/test_extension.o
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj/gen/sqlite3/sqlite3.c
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj/gen/sqlite3/sqlite3.h
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/obj/gen/sqlite3/sqlite3ext.h
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/sqlite3.a
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/Release/test_extension.node
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/better_sqlite3.target.mk
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/binding.Makefile
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/config.gypi
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/deps/locate_sqlite3.target.mk
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/deps/sqlite3.Makefile
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/deps/sqlite3.target.mk
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/test_extension.target.mk
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/common.gypi
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/copy.js
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/defines.gypi
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/download.sh
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/sqlite3.gyp
[MARKED] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/sqlite3/sqlite3.c
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/sqlite3/sqlite3.h
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/sqlite3/sqlite3ext.h
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/deps/test_extension.c
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/database.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/methods/aggregate.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/methods/backup.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/methods/function.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/methods/inspect.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/methods/pragma.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/methods/serialize.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/methods/table.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/methods/transaction.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/methods/wrappers.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/sqlite-error.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/lib/util.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/src/better_sqlite3.cpp
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/better-sqlite3/src/better_sqlite3.hpp
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bindings/LICENSE.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bindings/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bindings/bindings.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bindings/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/.travis.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/BufferList.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/LICENSE.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/bl.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/test/convert.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/test/indexOf.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/test/isBufferList.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/bl/test/test.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/buffer/AUTHORS.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/buffer/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/buffer/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/buffer/index.d.ts
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/buffer/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/buffer/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/chownr/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/chownr/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/chownr/chownr.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/chownr/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/decompress-response/index.d.ts
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/decompress-response/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/decompress-response/license
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/decompress-response/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/decompress-response/readme.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/deep-extend/CHANGELOG.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/deep-extend/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/deep-extend/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/deep-extend/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/deep-extend/lib/deep-extend.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/deep-extend/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/detect-libc/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/detect-libc/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/detect-libc/index.d.ts
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/detect-libc/lib/detect-libc.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/detect-libc/lib/elf.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/detect-libc/lib/filesystem.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/detect-libc/lib/process.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/detect-libc/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/end-of-stream/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/end-of-stream/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/end-of-stream/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/end-of-stream/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/expand-template/.travis.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/expand-template/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/expand-template/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/expand-template/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/expand-template/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/expand-template/test.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/.npmignore
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/.travis.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/History.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/index.d.ts
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/test/test.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/file-uri-to-path/test/tests.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/fs-constants/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/fs-constants/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/fs-constants/browser.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/fs-constants/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/fs-constants/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/.travis.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/example/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/example/url.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/readme.markdown
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/test/a.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/test/b.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/test/c.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/test/d.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/test/e.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/github-from-package/test/url.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/ieee754/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/ieee754/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/ieee754/index.d.ts
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/ieee754/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/ieee754/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/inherits/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/inherits/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/inherits/inherits.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/inherits/inherits_browser.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/inherits/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/ini/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/ini/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/ini/ini.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/ini/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/mimic-response/index.d.ts
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/mimic-response/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/mimic-response/license
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/mimic-response/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/mimic-response/readme.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/.eslintrc
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/.github/FUNDING.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/.nycrc
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/CHANGELOG.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/example/parse.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/all_bool.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/bool.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/dash.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/default_bool.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/dotted.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/kv_short.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/long.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/num.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/parse.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/parse_modified.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/proto.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/short.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/stop_early.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/unknown.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/minimist/test/whitespace.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/mkdirp-classic/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/mkdirp-classic/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/mkdirp-classic/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/mkdirp-classic/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/napi-build-utils/.github/workflows/run-npm-tests.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/napi-build-utils/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/napi-build-utils/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/napi-build-utils/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/napi-build-utils/index.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/napi-build-utils/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/node-abi/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/node-abi/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/node-abi/abi_registry.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/node-abi/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/node-abi/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/once/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/once/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/once/once.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/once/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/CHANGELOG.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/CONTRIBUTING.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/asset.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/bin.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/download.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/error.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/help.txt
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/log.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/proxy.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/rc.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/prebuild-install/util.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/.github/FUNDING.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/.travis.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/SECURITY.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/empty.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/test-browser.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/pump/test-node.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/LICENSE.APACHE2
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/LICENSE.BSD
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/LICENSE.MIT
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/browser.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/cli.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/lib/utils.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/test/ini.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/test/nested-env-vars.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/rc/test/test.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/CONTRIBUTING.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/GOVERNANCE.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/errors-browser.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/errors.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/experimentalWarning.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/_stream_duplex.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/_stream_passthrough.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/_stream_readable.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/_stream_transform.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/_stream_writable.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/async_iterator.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/buffer_list.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/destroy.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/end-of-stream.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/from-browser.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/from.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/pipeline.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/state.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/stream-browser.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/lib/internal/streams/stream.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/readable-browser.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/readable-stream/readable.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/safe-buffer/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/safe-buffer/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/safe-buffer/index.d.ts
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/safe-buffer/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/safe-buffer/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/bin/semver.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/classes/comparator.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/classes/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/classes/range.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/classes/semver.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/clean.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/cmp.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/coerce.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/compare-build.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/compare-loose.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/compare.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/diff.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/eq.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/gt.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/gte.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/inc.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/lt.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/lte.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/major.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/minor.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/neq.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/parse.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/patch.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/prerelease.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/rcompare.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/rsort.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/satisfies.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/sort.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/truncate.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/functions/valid.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/internal/constants.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/internal/debug.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/internal/identifiers.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/internal/lrucache.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/internal/parse-options.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/internal/re.js
[MARKED] Modules/Medical-History-1.0.0/node_modules/semver/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/preload.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/range.bnf
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/gtr.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/intersects.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/ltr.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/max-satisfying.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/min-satisfying.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/min-version.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/outside.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/simplify.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/subset.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/to-comparators.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/semver/ranges/valid.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-concat/.travis.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-concat/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-concat/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-concat/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-concat/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-concat/test/basic.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-get/.github/dependabot.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-get/.github/workflows/ci.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-get/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-get/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-get/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/simple-get/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/string_decoder/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/string_decoder/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/string_decoder/lib/string_decoder.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/string_decoder/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/strip-json-comments/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/strip-json-comments/license
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/strip-json-comments/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/strip-json-comments/readme.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/.travis.yml
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/a/hello.txt
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/b/a/test.txt
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/d/file1
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/d/file2
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/d/sub-dir/file5
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/d/sub-files/file3
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/d/sub-files/file4
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/e/directory/.ignore
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/e/file
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/fixtures/invalid.tar
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-fs/test/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-stream/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-stream/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-stream/extract.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-stream/headers.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-stream/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-stream/pack.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-stream/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tar-stream/sandbox.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tunnel-agent/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tunnel-agent/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tunnel-agent/index.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/tunnel-agent/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/util-deprecate/History.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/util-deprecate/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/util-deprecate/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/util-deprecate/browser.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/util-deprecate/node.js
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/util-deprecate/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/wrappy/LICENSE
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/wrappy/README.md
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/wrappy/package.json
[CLEAR]  Modules/Medical-History-1.0.0/node_modules/wrappy/wrappy.js
[CLEAR]  Modules/Medical-History-1.0.0/package-lock.json
[CLEAR]  Modules/Medical-History-1.0.0/package.json
[CLEAR]  Modules/Medical-History-1.0.0/public/app.js
[CLEAR]  Modules/Medical-History-1.0.0/public/index.html
[CLEAR]  Modules/Medical-History-1.0.0/public/styles.css
[CLEAR]  Modules/Medical-History-1.0.0/readiness.js
[CLEAR]  Modules/Medical-History-1.0.0/repository.js
[CLEAR]  Modules/Medical-History-1.0.0/retention.js
[CLEAR]  Modules/Medical-History-1.0.0/security.js
[CLEAR]  Modules/Medical-History-1.0.0/server.js
[CLEAR]  Modules/Medical-History-1.0.0/test/auth-adapter.test.js
[CLEAR]  Modules/Medical-History-1.0.0/test/repository.test.js
[CLEAR]  Modules/Medical-History-1.0.0/test/security.test.js
[CLEAR]  Modules/Medical-History-1.0.0/test/server.test.js
[CLEAR]  Modules/Medical-History-1.0.0/test/submission.test.js
[MARKED] Modules/Severity-1.1.0/HANDOFF.md
[MARKED] Modules/Severity-1.1.0/README.md
[CLEAR]  Modules/Severity-1.1.0/assessment-repository.js
[CLEAR]  Modules/Severity-1.1.0/auth-adapter.js
[CLEAR]  Modules/Severity-1.1.0/data/assessments.json
[CLEAR]  Modules/Severity-1.1.0/module-config.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/.bin/mime
[CLEAR]  Modules/Severity-1.1.0/node_modules/.bin/mime.cmd
[CLEAR]  Modules/Severity-1.1.0/node_modules/.bin/mime.ps1
[CLEAR]  Modules/Severity-1.1.0/node_modules/.package-lock.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/accepts/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/accepts/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/accepts/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/accepts/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/accepts/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/array-flatten/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/array-flatten/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/array-flatten/array-flatten.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/array-flatten/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/lib/read.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/lib/types/json.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/lib/types/raw.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/lib/types/text.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/lib/types/urlencoded.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/body-parser/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/bytes/History.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/bytes/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/bytes/Readme.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/bytes/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/bytes/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/actualApply.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/actualApply.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/applyBind.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/applyBind.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/functionApply.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/functionApply.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/functionCall.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/functionCall.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/reflectApply.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/reflectApply.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bind-apply-helpers/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/call-bound/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-disposition/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-disposition/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-disposition/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-disposition/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-disposition/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-type/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-type/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-type/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-type/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/content-type/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/cookie-signature/History.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/cookie-signature/Readme.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/cookie-signature/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/cookie-signature/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/cookie/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/cookie/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/cookie/SECURITY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/cookie/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/cookie/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/.coveralls.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/.npmignore
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/.travis.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/Makefile
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/component.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/karma.conf.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/node.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/src/browser.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/src/debug.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/src/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/src/inspector-log.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/debug/src/node.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/depd/History.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/depd/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/depd/Readme.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/depd/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/depd/lib/browser/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/depd/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/destroy/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/destroy/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/destroy/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/destroy/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/get.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/get.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/set.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/set.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/test/get.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/test/set.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/dunder-proto/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/ee-first/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/ee-first/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/ee-first/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/ee-first/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/encodeurl/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/encodeurl/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/encodeurl/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/encodeurl/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-define-property/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/eval.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/eval.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/range.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/range.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/ref.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/ref.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/syntax.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/syntax.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/type.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/type.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/uri.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-errors/uri.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/RequireObjectCoercible.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/RequireObjectCoercible.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/ToObject.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/ToObject.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/isObject.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/isObject.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/es-object-atoms/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/escape-html/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/escape-html/Readme.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/escape-html/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/escape-html/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/etag/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/etag/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/etag/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/etag/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/etag/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/History.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/Readme.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/application.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/express.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/middleware/init.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/middleware/query.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/request.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/response.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/router/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/router/layer.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/router/route.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/utils.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/lib/view.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/express/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/finalhandler/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/finalhandler/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/finalhandler/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/finalhandler/SECURITY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/finalhandler/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/finalhandler/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/forwarded/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/forwarded/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/forwarded/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/forwarded/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/forwarded/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/fresh/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/fresh/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/fresh/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/fresh/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/fresh/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/.github/SECURITY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/implementation.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/test/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/function-bind/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-intrinsic/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-intrinsic/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-intrinsic/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-intrinsic/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-intrinsic/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-intrinsic/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-intrinsic/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-intrinsic/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-intrinsic/test/GetIntrinsic.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/Object.getPrototypeOf.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/Object.getPrototypeOf.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/Reflect.getPrototypeOf.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/Reflect.getPrototypeOf.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/get-proto/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/gOPD.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/gOPD.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/gopd/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/shams.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/shams.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/test/shams/core-js.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/test/shams/get-own-property-symbols.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/test/tests.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/has-symbols/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/eslint.config.mjs
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/hasown/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/http-errors/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/http-errors/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/http-errors/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/http-errors/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/http-errors/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/Changelog.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/dbcs-codec.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/dbcs-data.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/internal.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/sbcs-codec.js
[MARKED] Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/sbcs-data-generated.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/sbcs-data.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/tables/big5-added.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/tables/cp936.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/tables/cp949.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/tables/cp950.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/tables/eucjp.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/tables/gb18030-ranges.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/tables/gbk-added.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/tables/shiftjis.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/utf16.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/encodings/utf7.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/lib/bom-handling.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/lib/extend-node.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/lib/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/lib/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/lib/streams.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/iconv-lite/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/inherits/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/inherits/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/inherits/inherits.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/inherits/inherits_browser.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/inherits/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/ipaddr.js/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/ipaddr.js/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/ipaddr.js/ipaddr.min.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/ipaddr.js/lib/ipaddr.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/ipaddr.js/lib/ipaddr.js.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/ipaddr.js/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/abs.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/abs.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/constants/maxArrayLength.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/constants/maxArrayLength.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/constants/maxSafeInteger.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/constants/maxSafeInteger.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/constants/maxValue.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/constants/maxValue.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/floor.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/floor.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/isFinite.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/isFinite.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/isInteger.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/isInteger.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/isNaN.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/isNaN.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/isNegativeZero.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/isNegativeZero.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/max.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/max.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/min.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/min.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/mod.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/mod.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/pow.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/pow.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/round.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/round.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/sign.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/sign.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/math-intrinsics/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/media-typer/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/media-typer/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/media-typer/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/media-typer/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/media-typer/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/merge-descriptors/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/merge-descriptors/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/merge-descriptors/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/merge-descriptors/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/merge-descriptors/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/methods/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/methods/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/methods/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/methods/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/methods/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-db/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-db/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-db/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-db/db.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-db/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-db/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-types/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-types/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-types/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-types/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime-types/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/.npmignore
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/cli.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/mime.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/src/build.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/src/test.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/mime/types.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/ms/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/ms/license.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/ms/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/ms/readme.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/negotiator/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/negotiator/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/negotiator/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/negotiator/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/negotiator/lib/charset.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/negotiator/lib/encoding.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/negotiator/lib/language.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/negotiator/lib/mediaType.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/negotiator/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/example/all.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/example/circular.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/example/fn.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/example/inspect.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/package-support.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/readme.markdown
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test-core-js.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/bigint.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/browser/dom.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/circular.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/deep.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/element.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/err.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/fakes.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/fn.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/global.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/has.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/holes.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/indent-option.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/inspect.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/lowbyte.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/number.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/quoteStyle.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/toStringTag.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/undef.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/test/values.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/object-inspect/util.inspect.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/on-finished/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/on-finished/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/on-finished/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/on-finished/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/on-finished/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/parseurl/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/parseurl/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/parseurl/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/parseurl/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/parseurl/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/path-to-regexp/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/path-to-regexp/Readme.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/path-to-regexp/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/path-to-regexp/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/proxy-addr/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/proxy-addr/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/proxy-addr/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/proxy-addr/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/proxy-addr/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/.editorconfig
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/.github/SECURITY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/.github/THREAT_MODEL.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/LICENSE.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/dist/qs.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/eslint.config.mjs
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/lib/formats.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/lib/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/lib/parse.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/lib/stringify.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/lib/utils.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/test/empty-keys-cases.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/test/parse.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/test/stringify.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/qs/test/utils.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/range-parser/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/range-parser/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/range-parser/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/range-parser/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/range-parser/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/raw-body/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/raw-body/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/raw-body/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/raw-body/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/raw-body/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/safe-buffer/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/safe-buffer/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/safe-buffer/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/safe-buffer/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/safe-buffer/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/safer-buffer/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/safer-buffer/Porting-Buffer.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/safer-buffer/Readme.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/safer-buffer/dangerous.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/safer-buffer/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/safer-buffer/safer.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/safer-buffer/tests.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/SECURITY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/node_modules/ms/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/node_modules/ms/license.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/node_modules/ms/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/node_modules/ms/readme.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/send/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/serve-static/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/serve-static/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/serve-static/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/serve-static/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/serve-static/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/setprototypeof/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/setprototypeof/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/setprototypeof/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/setprototypeof/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/setprototypeof/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/setprototypeof/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/.editorconfig
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/list.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-list/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/.editorconfig
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-map/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/.editorconfig
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel-weakmap/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/.editorconfig
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/.eslintrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/.github/FUNDING.yml
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/.nycrc
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/CHANGELOG.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/index.d.ts
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/test/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/side-channel/tsconfig.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/statuses/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/statuses/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/statuses/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/statuses/codes.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/statuses/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/statuses/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/toidentifier/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/toidentifier/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/toidentifier/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/toidentifier/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/toidentifier/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/type-is/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/type-is/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/type-is/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/type-is/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/type-is/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/unpipe/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/unpipe/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/unpipe/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/unpipe/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/unpipe/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/utils-merge/.npmignore
[CLEAR]  Modules/Severity-1.1.0/node_modules/utils-merge/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/utils-merge/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/utils-merge/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/utils-merge/package.json
[CLEAR]  Modules/Severity-1.1.0/node_modules/vary/HISTORY.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/vary/LICENSE
[CLEAR]  Modules/Severity-1.1.0/node_modules/vary/README.md
[CLEAR]  Modules/Severity-1.1.0/node_modules/vary/index.js
[CLEAR]  Modules/Severity-1.1.0/node_modules/vary/package.json
[CLEAR]  Modules/Severity-1.1.0/package-lock.json
[CLEAR]  Modules/Severity-1.1.0/package.json
[CLEAR]  Modules/Severity-1.1.0/public/index.html
[CLEAR]  Modules/Severity-1.1.0/readiness.js
[CLEAR]  Modules/Severity-1.1.0/security.js
[CLEAR]  Modules/Severity-1.1.0/server.js
[CLEAR]  Modules/Severity-1.1.0/server.test.js
[CLEAR]  Modules/Severity-1.1.0/severity-assessment.js
[CLEAR]  Modules/Severity-1.1.0/test_api.js
[CLEAR]  Modules/Severity-1.1.0/test_auth_adapter.js
[CLEAR]  Modules/Treatment-Plan/.dockerignore
[CLEAR]  Modules/Treatment-Plan/.gitignore
[MARKED] Modules/Treatment-Plan/CONTEXT-MAP.md
[CLEAR]  Modules/Treatment-Plan/Dockerfile
[CLEAR]  Modules/Treatment-Plan/Dockerfile.release
[MARKED] Modules/Treatment-Plan/HANDOFF.md
[CLEAR]  Modules/Treatment-Plan/README.md
[CLEAR]  Modules/Treatment-Plan/compose.release.yaml
[CLEAR]  Modules/Treatment-Plan/compose.yaml
[CLEAR]  Modules/Treatment-Plan/contracts/IDENTIFIERS-ENCOUNTERS-AND-TRANSPORT.md
[CLEAR]  Modules/Treatment-Plan/contracts/SCHEMA-VERSIONING.md
[CLEAR]  Modules/Treatment-Plan/contracts/examples/1.0.0/audit-provenance.json
[CLEAR]  Modules/Treatment-Plan/contracts/examples/1.0.0/clinical-input-snapshot.json
[CLEAR]  Modules/Treatment-Plan/contracts/examples/1.0.0/final-plan.json
[CLEAR]  Modules/Treatment-Plan/contracts/examples/1.0.0/follow-up-delta.json
[CLEAR]  Modules/Treatment-Plan/contracts/examples/1.0.0/plan-edit.json
[CLEAR]  Modules/Treatment-Plan/contracts/examples/1.0.0/primary-plan.json
[CLEAR]  Modules/Treatment-Plan/contracts/examples/1.0.0/problem-details.json
[CLEAR]  Modules/Treatment-Plan/contracts/examples/1.0.0/recommendation-run.json
[CLEAR]  Modules/Treatment-Plan/contracts/examples/1.0.0/safety-finding.json
[CLEAR]  Modules/Treatment-Plan/contracts/identifier-transport-contract.v1.json
[CLEAR]  Modules/Treatment-Plan/contracts/manifest.v1.0.0.json
[CLEAR]  Modules/Treatment-Plan/contracts/openapi/treatment-plan.openapi.v1.0.0.json
[CLEAR]  Modules/Treatment-Plan/contracts/schema-registry.v1.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/audit-event.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/audit-provenance.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/clinical-input-snapshot.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/final-plan.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/follow-up-delta.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/plan-edit.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/primary-plan.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/problem-details.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/recommendation-run.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/safety-finding.schema.json
[CLEAR]  Modules/Treatment-Plan/contracts/schemas/1.0.0/treatment-plan.schema.json
[MARKED] Modules/Treatment-Plan/deployment/ROLLBACK.md
[CLEAR]  Modules/Treatment-Plan/deployment/compose.unified.yaml
[CLEAR]  Modules/Treatment-Plan/deployment/nginx-vps.conf
[CLEAR]  Modules/Treatment-Plan/deployment/secrets-empty/.gitkeep
[CLEAR]  Modules/Treatment-Plan/deployment/treatment-plan-container.service
[CLEAR]  Modules/Treatment-Plan/frontend/index.html
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/.package-lock.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/.vite/vitest/da39a3ee5e6b4b0d3255bfef95601890afd80709/results.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/cache.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/cache.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/cache.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/color.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/color.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/color.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/common.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/common.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/common.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/constant.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/constant.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/constant.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/convert.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/convert.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/convert.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/css-calc.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/css-calc.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/css-calc.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/css-gradient.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/css-gradient.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/css-gradient.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/css-var.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/css-var.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/css-var.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/relative-color.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/relative-color.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/relative-color.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/resolve.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/resolve.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/resolve.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/typedef.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/util.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/dist/esm/js/util.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/index.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/cache.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/color.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/common.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/constant.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/convert.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/css-calc.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/css-gradient.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/css-var.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/relative-color.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/resolve.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/typedef.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/css-color/src/js/util.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/src/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/src/js/constant.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/src/js/finder.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/src/js/matcher.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/src/js/parser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/src/js/utility.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/types/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/types/js/constant.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/types/js/finder.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/types/js/matcher.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/types/js/parser.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/dom-selector/types/js/utility.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/generational-cache/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/generational-cache/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/generational-cache/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/generational-cache/src/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/generational-cache/types/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/nwsapi/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/nwsapi/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/nwsapi/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@asamuzakjp/nwsapi/src/nwsapi.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/code-frame/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/code-frame/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/code-frame/lib/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/code-frame/lib/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/code-frame/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/helper-validator-identifier/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/helper-validator-identifier/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/helper-validator-identifier/lib/identifier.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/helper-validator-identifier/lib/identifier.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/helper-validator-identifier/lib/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/helper-validator-identifier/lib/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/helper-validator-identifier/lib/keyword.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/helper-validator-identifier/lib/keyword.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/helper-validator-identifier/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/AwaitValue.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/OverloadYield.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/applyDecoratedDescriptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/applyDecs.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/applyDecs2203.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/applyDecs2203R.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/applyDecs2301.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/applyDecs2305.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/applyDecs2311.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/arrayLikeToArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/arrayWithHoles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/arrayWithoutHoles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/assertClassBrand.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/assertThisInitialized.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/asyncGeneratorDelegate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/asyncIterator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/asyncToGenerator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/awaitAsyncGenerator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/callSuper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/checkInRHS.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/checkPrivateRedeclaration.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classApplyDescriptorDestructureSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classApplyDescriptorGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classApplyDescriptorSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classCallCheck.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classCheckPrivateStaticAccess.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classCheckPrivateStaticFieldDescriptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classExtractFieldDescriptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classNameTDZError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateFieldDestructureSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateFieldGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateFieldGet2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateFieldInitSpec.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateFieldLooseBase.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateFieldLooseKey.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateFieldSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateFieldSet2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateGetter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateMethodGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateMethodInitSpec.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateMethodSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classPrivateSetter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classStaticPrivateFieldDestructureSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classStaticPrivateFieldSpecGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classStaticPrivateFieldSpecSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classStaticPrivateMethodGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/classStaticPrivateMethodSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/construct.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/createClass.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/createForOfIteratorHelper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/createForOfIteratorHelperLoose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/createSuper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/decorate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/defaults.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/defineAccessor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/defineEnumerableProperties.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/defineProperty.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/dispose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/AwaitValue.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/OverloadYield.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/applyDecoratedDescriptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/applyDecs.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/applyDecs2203.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/applyDecs2203R.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/applyDecs2301.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/applyDecs2305.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/applyDecs2311.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/arrayLikeToArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/arrayWithHoles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/arrayWithoutHoles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/assertClassBrand.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/assertThisInitialized.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/asyncGeneratorDelegate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/asyncIterator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/awaitAsyncGenerator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/callSuper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/checkInRHS.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/checkPrivateRedeclaration.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classApplyDescriptorDestructureSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classApplyDescriptorGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classApplyDescriptorSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classCallCheck.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classCheckPrivateStaticAccess.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classCheckPrivateStaticFieldDescriptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classExtractFieldDescriptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classNameTDZError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateFieldDestructureSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateFieldGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateFieldGet2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateFieldInitSpec.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateFieldLooseBase.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateFieldLooseKey.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateFieldSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateFieldSet2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateGetter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateMethodGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateMethodInitSpec.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateMethodSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classPrivateSetter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classStaticPrivateFieldDestructureSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classStaticPrivateFieldSpecGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classStaticPrivateFieldSpecSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classStaticPrivateMethodGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/classStaticPrivateMethodSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/construct.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/createClass.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/createForOfIteratorHelper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/createForOfIteratorHelperLoose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/createSuper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/decorate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/defaults.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/defineAccessor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/defineEnumerableProperties.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/defineProperty.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/dispose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/extends.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/get.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/getPrototypeOf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/identity.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/importDeferProxy.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/inherits.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/inheritsLoose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/initializerDefineProperty.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/initializerWarningHelper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/instanceof.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/interopRequireDefault.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/interopRequireWildcard.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/isNativeFunction.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/isNativeReflectConstruct.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/iterableToArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/iterableToArrayLimit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/jsx.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/maybeArrayLike.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/newArrowCheck.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/nonIterableRest.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/nonIterableSpread.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/nullishReceiverError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/objectDestructuringEmpty.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/objectSpread.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/objectSpread2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/objectWithoutProperties.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/objectWithoutPropertiesLoose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/possibleConstructorReturn.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/readOnlyError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/regenerator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/regeneratorAsync.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/regeneratorAsyncGen.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/regeneratorAsyncIterator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/regeneratorDefine.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/regeneratorKeys.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/regeneratorRuntime.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/regeneratorValues.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/set.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/setFunctionName.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/setPrototypeOf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/skipFirstGeneratorNext.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/slicedToArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/superPropBase.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/superPropGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/superPropSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/taggedTemplateLiteral.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/taggedTemplateLiteralLoose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/tdz.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/temporalRef.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/temporalUndefined.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/toArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/toConsumableArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/toPrimitive.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/toPropertyKey.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/toSetter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/tsRewriteRelativeImportExtensions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/typeof.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/unsupportedIterableToArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/using.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/usingCtx.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/wrapAsyncGenerator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/wrapNativeSuper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/wrapRegExp.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/esm/writeOnlyError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/extends.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/get.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/getPrototypeOf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/identity.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/importDeferProxy.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/inherits.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/inheritsLoose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/initializerDefineProperty.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/initializerWarningHelper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/instanceof.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/interopRequireDefault.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/interopRequireWildcard.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/isNativeFunction.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/isNativeReflectConstruct.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/iterableToArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/iterableToArrayLimit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/jsx.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/maybeArrayLike.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/newArrowCheck.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/nonIterableRest.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/nonIterableSpread.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/nullishReceiverError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/objectDestructuringEmpty.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/objectSpread.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/objectSpread2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/objectWithoutProperties.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/objectWithoutPropertiesLoose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/possibleConstructorReturn.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/readOnlyError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/regenerator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/regeneratorAsync.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/regeneratorAsyncGen.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/regeneratorAsyncIterator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/regeneratorDefine.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/regeneratorKeys.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/regeneratorRuntime.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/regeneratorValues.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/set.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/setFunctionName.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/setPrototypeOf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/skipFirstGeneratorNext.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/slicedToArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/superPropBase.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/superPropGet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/superPropSet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/taggedTemplateLiteral.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/taggedTemplateLiteralLoose.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/tdz.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/temporalRef.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/temporalUndefined.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/toArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/toConsumableArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/toPrimitive.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/toPropertyKey.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/toSetter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/tsRewriteRelativeImportExtensions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/typeof.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/unsupportedIterableToArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/using.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/usingCtx.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/wrapAsyncGenerator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/wrapNativeSuper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/wrapRegExp.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/helpers/writeOnlyError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@babel/runtime/regenerator/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/bin/cli.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/dist/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/dist/index.cjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/dist/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/src/core/calculate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/src/core/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/src/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/src/util/compare.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/src/util/filter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/src/util/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@bramus/specificity/src/util/sort.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/color-helpers/CHANGELOG.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/color-helpers/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/color-helpers/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/color-helpers/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/color-helpers/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/color-helpers/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-calc/CHANGELOG.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-calc/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-calc/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-calc/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-calc/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-calc/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-color-parser/CHANGELOG.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-color-parser/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-color-parser/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-color-parser/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-color-parser/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-color-parser/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-parser-algorithms/CHANGELOG.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-parser-algorithms/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-parser-algorithms/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-parser-algorithms/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-parser-algorithms/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-parser-algorithms/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-syntax-patches-for-csstree/CHANGELOG.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-syntax-patches-for-csstree/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-syntax-patches-for-csstree/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-syntax-patches-for-csstree/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-syntax-patches-for-csstree/dist/index.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-syntax-patches-for-csstree/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-tokenizer/CHANGELOG.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-tokenizer/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-tokenizer/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-tokenizer/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-tokenizer/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@csstools/css-tokenizer/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/array.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/array.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/assert.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/base32.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/base32.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/base58.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/base58.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/base58check.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/base58check.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/base58check.node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/base64.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/base64.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/bech32.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/bech32.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/bigint.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/bigint.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/encoding-browser.browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/encoding-browser.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/encoding-browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/encoding-browser.native.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/encoding-lite.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/encoding-lite.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/encoding.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/encoding.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/_utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/base32.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/base58check.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/base64.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/encoding.api.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/encoding.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/encoding.labels.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/encoding.util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/hex.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/latin1.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/multi-byte.encodings.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/multi-byte.encodings.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/multi-byte.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/multi-byte.table.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/percent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/platform.browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/platform.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/platform.native.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/single-byte.encodings.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/single-byte.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/utf16.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/utf8.auto.browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/utf8.auto.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/utf8.auto.native.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/fallback/utf8.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/hex.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/hex.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/hex.node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/multi-byte.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/multi-byte.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/multi-byte.node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/single-byte.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/single-byte.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/single-byte.node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/utf16.browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/utf16.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/utf16.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/utf16.native.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/utf16.node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/utf8.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/utf8.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/utf8.node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/whatwg.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/whatwg.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/wif.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@exodus/bytes/wif.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/dist/sourcemap-codec.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/dist/sourcemap-codec.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/dist/sourcemap-codec.umd.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/dist/sourcemap-codec.umd.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/src/scopes.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/src/sourcemap-codec.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/src/strings.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/src/vlq.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/scopes.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/scopes.d.cts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/scopes.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/scopes.d.mts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/sourcemap-codec.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/sourcemap-codec.d.cts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/sourcemap-codec.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/sourcemap-codec.d.mts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/strings.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/strings.d.cts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/strings.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/strings.d.mts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/vlq.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/vlq.d.cts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/vlq.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@jridgewell/sourcemap-codec/types/vlq.d.mts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@oxc-project/types/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@oxc-project/types/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@oxc-project/types/package.json
[MARKED] Modules/Treatment-Plan/frontend/node_modules/@oxc-project/types/types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/binding-linux-x64-gnu/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/binding-linux-x64-gnu/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/binding-linux-x64-gnu/rolldown-binding.linux-x64-gnu.node
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/pluginutils/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/pluginutils/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/pluginutils/dist/filter-B_mD-HGz.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/pluginutils/dist/filter/index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/pluginutils/dist/filter/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/pluginutils/dist/index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/pluginutils/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@rolldown/pluginutils/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@standard-schema/spec/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@standard-schema/spec/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@standard-schema/spec/dist/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@standard-schema/spec/dist/index.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@standard-schema/spec/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@standard-schema/spec/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@standard-schema/spec/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/LICENSE
[MARKED] Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/@testing-library/dom.cjs.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/@testing-library/dom.esm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/@testing-library/dom.umd.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/@testing-library/dom.umd.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/@testing-library/dom.umd.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/@testing-library/dom.umd.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/DOMElementFilter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/config.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/event-map.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/events.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/get-node-text.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/get-queries-for-element.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/get-user-code-frame.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/helpers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/label-helpers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/matches.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/pretty-dom.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/all-utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/alt-text.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/display-value.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/label-text.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/placeholder-text.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/role.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/test-id.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/text.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/queries/title.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/query-helpers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/role-helpers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/screen.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/suggestions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/wait-for-element-to-be-removed.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/dist/wait-for.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/config.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/events.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/get-node-text.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/get-queries-for-element.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/matches.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/pretty-dom.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/queries.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/query-helpers.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/role-helpers.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/screen.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/suggestions.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/wait-for-element-to-be-removed.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/dom/types/wait-for.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/LICENSE
[MARKED] Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.cjs.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.esm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.pure.cjs.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.pure.esm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.pure.umd.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.pure.umd.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.pure.umd.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.pure.umd.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.umd.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.umd.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.umd.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/@testing-library/react.umd.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/act-compat.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/config.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/fire-event.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dist/pure.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/dont-cleanup-after-each.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/pure.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/pure.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/types/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/react/types/pure.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/clipboard/copy.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/clipboard/cut.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/clipboard/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/clipboard/paste.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/convenience/click.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/convenience/hover.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/convenience/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/convenience/tab.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/document/UI.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/document/copySelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/document/getValueOrTextContent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/document/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/document/interceptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/document/patchFocus.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/document/prepareDocument.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/document/trackValue.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/behavior/click.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/behavior/cut.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/behavior/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/behavior/keydown.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/behavior/keypress.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/behavior/keyup.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/behavior/paste.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/behavior/registry.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/createEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/dispatchEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/eventMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/focus.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/input.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/radio.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/getInputRange.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/getTargetTypeAndSelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/modifySelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/modifySelectionPerMouse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/moveSelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/resolveCaretPosition.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/selectAll.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/setSelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/setSelectionPerMouse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/setSelectionRange.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/selection/updateSelectionOnFocus.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/event/wrapEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/keyboard/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/keyboard/keyMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/keyboard/parseKeyDef.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/options.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/pointer/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/pointer/keyMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/pointer/parseKeyDef.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/setup/api.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/setup/directApi.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/setup/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/setup/setup.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/setup/wrapAsync.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/system/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/system/keyboard.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/system/pointer/buttons.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/system/pointer/device.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/system/pointer/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/system/pointer/mouse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/system/pointer/pointer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/system/pointer/shared.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utility/clear.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utility/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utility/selectOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utility/type.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utility/upload.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/click/isClickableInput.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/dataTransfer/Blob.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/dataTransfer/Clipboard.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/dataTransfer/DataTransfer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/dataTransfer/FileList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/edit/isContentEditable.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/edit/isEditable.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/edit/maxLength.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/edit/setFiles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/edit/timeValue.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/focus/cursor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/focus/getActiveElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/focus/getTabDestination.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/focus/isFocusable.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/focus/selection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/focus/selector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/keyDef/readNextDescriptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/cloneEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/findClosest.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/getDocumentFromNode.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/getTreeDiff.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/getWindow.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/isDescendantOrSelf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/isDisabled.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/isElementType.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/isVisible.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/level.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/misc/wait.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/cjs/utils/pointer/cssPointerEvents.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/clipboard/copy.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/clipboard/cut.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/clipboard/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/clipboard/paste.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/convenience/click.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/convenience/hover.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/convenience/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/convenience/tab.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/document/UI.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/document/copySelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/document/getValueOrTextContent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/document/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/document/interceptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/document/patchFocus.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/document/prepareDocument.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/document/trackValue.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/behavior/click.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/behavior/cut.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/behavior/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/behavior/keydown.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/behavior/keypress.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/behavior/keyup.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/behavior/paste.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/behavior/registry.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/createEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/dispatchEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/eventMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/focus.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/input.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/radio.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/getInputRange.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/getTargetTypeAndSelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/modifySelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/modifySelectionPerMouse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/moveSelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/resolveCaretPosition.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/selectAll.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/setSelection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/setSelectionPerMouse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/setSelectionRange.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/selection/updateSelectionOnFocus.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/event/wrapEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/keyboard/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/keyboard/keyMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/keyboard/parseKeyDef.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/options.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/pointer/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/pointer/keyMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/pointer/parseKeyDef.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/setup/api.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/setup/directApi.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/setup/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/setup/setup.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/setup/wrapAsync.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/system/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/system/keyboard.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/system/pointer/buttons.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/system/pointer/device.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/system/pointer/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/system/pointer/mouse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/system/pointer/pointer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/system/pointer/shared.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utility/clear.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utility/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utility/selectOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utility/type.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utility/upload.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/click/isClickableInput.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/dataTransfer/Blob.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/dataTransfer/Clipboard.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/dataTransfer/DataTransfer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/dataTransfer/FileList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/edit/isContentEditable.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/edit/isEditable.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/edit/maxLength.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/edit/setFiles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/edit/timeValue.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/focus/cursor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/focus/getActiveElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/focus/getTabDestination.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/focus/isFocusable.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/focus/selection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/focus/selector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/keyDef/readNextDescriptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/cloneEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/findClosest.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/getDocumentFromNode.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/getTreeDiff.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/getWindow.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/isDescendantOrSelf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/isDisabled.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/isElementType.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/isVisible.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/level.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/misc/wait.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/esm/utils/pointer/cssPointerEvents.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/clipboard/copy.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/clipboard/cut.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/clipboard/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/clipboard/paste.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/convenience/click.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/convenience/hover.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/convenience/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/convenience/tab.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/document/UI.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/document/copySelection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/document/getValueOrTextContent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/document/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/document/interceptor.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/document/patchFocus.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/document/prepareDocument.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/document/trackValue.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/behavior/click.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/behavior/cut.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/behavior/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/behavior/keydown.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/behavior/keypress.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/behavior/keyup.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/behavior/paste.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/behavior/registry.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/createEvent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/dispatchEvent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/eventMap.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/focus.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/input.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/radio.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/getInputRange.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/getTargetTypeAndSelection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/modifySelection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/modifySelectionPerMouse.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/moveSelection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/resolveCaretPosition.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/selectAll.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/setSelection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/setSelectionPerMouse.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/setSelectionRange.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/selection/updateSelectionOnFocus.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/event/wrapEvent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/keyboard/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/keyboard/keyMap.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/keyboard/parseKeyDef.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/options.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/pointer/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/pointer/keyMap.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/pointer/parseKeyDef.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/setup/api.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/setup/directApi.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/setup/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/setup/setup.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/setup/wrapAsync.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/system/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/system/keyboard.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/system/pointer/buttons.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/system/pointer/device.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/system/pointer/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/system/pointer/mouse.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/system/pointer/pointer.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/system/pointer/shared.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utility/clear.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utility/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utility/selectOptions.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utility/type.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utility/upload.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/click/isClickableInput.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/dataTransfer/Blob.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/dataTransfer/Clipboard.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/dataTransfer/DataTransfer.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/dataTransfer/FileList.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/edit/isContentEditable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/edit/isEditable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/edit/maxLength.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/edit/setFiles.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/edit/timeValue.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/focus/cursor.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/focus/getActiveElement.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/focus/getTabDestination.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/focus/isFocusable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/focus/selection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/focus/selector.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/keyDef/readNextDescriptor.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/cloneEvent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/findClosest.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/getDocumentFromNode.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/getTreeDiff.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/getWindow.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/isDescendantOrSelf.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/isDisabled.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/isElementType.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/isVisible.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/level.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/misc/wait.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/dist/types/utils/pointer/cssPointerEvents.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@testing-library/user-event/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/aria-query/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/aria-query/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/aria-query/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/aria-query/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/chai/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/chai/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/chai/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/chai/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/chai/register-should.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/deep-eql/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/deep-eql/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/deep-eql/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/deep-eql/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/estree/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/estree/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/estree/flow.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/estree/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/estree/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/canary.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/client.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/experimental.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/server.browser.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/server.bun.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/server.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/server.edge.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/server.node.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/static.browser.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/static.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/static.edge.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/static.node.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react-dom/test-utils/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/canary.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/compiler-runtime.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/experimental.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/global.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/jsx-dev-runtime.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/jsx-runtime.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/ts5.0/canary.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/ts5.0/experimental.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/ts5.0/global.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/ts5.0/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/ts5.0/jsx-dev-runtime.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@types/react/ts5.0/jsx-runtime.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/NOTICE.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.decorators.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.decorators.legacy.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.dom.asynciterable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.dom.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.dom.iterable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.collection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.core.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.generator.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.iterable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.promise.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.proxy.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.reflect.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.symbol.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2015.symbol.wellknown.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2016.array.include.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2016.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2016.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2016.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2017.arraybuffer.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2017.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2017.date.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2017.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2017.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2017.object.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2017.sharedmemory.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2017.string.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2017.typedarrays.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2018.asyncgenerator.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2018.asynciterable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2018.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2018.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2018.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2018.promise.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2018.regexp.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2019.array.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2019.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2019.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2019.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2019.object.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2019.string.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2019.symbol.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.bigint.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.date.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.number.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.promise.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.sharedmemory.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.string.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2020.symbol.wellknown.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2021.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2021.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2021.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2021.promise.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2021.string.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2021.weakref.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2022.array.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2022.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2022.error.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2022.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2022.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2022.object.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2022.regexp.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2022.string.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2023.array.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2023.collection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2023.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2023.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2023.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2024.arraybuffer.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2024.collection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2024.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2024.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2024.object.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2024.promise.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2024.regexp.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2024.sharedmemory.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2024.string.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2025.collection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2025.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2025.float16.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2025.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2025.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2025.iterator.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2025.promise.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es2025.regexp.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es5.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.es6.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.array.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.collection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.date.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.decorators.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.disposable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.error.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.full.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.intl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.sharedmemory.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.temporal.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.esnext.typedarrays.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.scripthost.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.webworker.asynciterable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.webworker.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.webworker.importscripts.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/lib.webworker.iterable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/tsc
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/lib/tsc.sig
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@typescript/typescript-linux-x64/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitejs/plugin-react/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitejs/plugin-react/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitejs/plugin-react/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitejs/plugin-react/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitejs/plugin-react/dist/refresh-runtime.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitejs/plugin-react/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitejs/plugin-react/types/optionalTypes.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitejs/plugin-react/types/preamble.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/expect/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/expect/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/expect/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/expect/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/expect/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/auto-register.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/auto-register.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/automock.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/automock.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/browser.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/chunk-automock.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/chunk-helpers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/chunk-hoistMocks.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/chunk-interceptor-native.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/chunk-mocker.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/chunk-pathe.M-eThtNZ.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/chunk-registry.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/chunk-utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/hoistMocks.d-w2ILr1dG.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/index.d-B41z0AuW.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/mocker.d-QEntlm6J.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/node.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/redirect.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/redirect.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/register.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/register.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/transforms.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/transforms.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/dist/types.d-BjI5eAwu.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/mocker/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/pretty-format/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/pretty-format/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/pretty-format/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/pretty-format/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/pretty-format/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/dist/chunk-artifact.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/dist/tasks.d-DEYaIMIu.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/dist/types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/dist/types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/dist/utils.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/dist/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/runner/utils.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/dist/environment.d-DOJxxZV9.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/dist/environment.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/dist/environment.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/dist/manager.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/dist/manager.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/dist/rawSnapshot.d-D_X3-62x.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/environment.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/manager.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/snapshot/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/spy/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/spy/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/spy/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/spy/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/spy/optional-types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/spy/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/diff.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/chunk-pathe.M-eThtNZ.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/constants.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/constants.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/diff.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/diff.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/display.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/display.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/error.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/error.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/helpers.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/helpers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/offset.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/offset.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/resolver.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/resolver.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/serialize.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/serialize.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/source-map.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/source-map.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/source-map/node.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/source-map/node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/timers.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/timers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/types.d-BCElaP-c.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/dist/types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/error.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/helpers.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/@vitest/utils/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-regex/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-regex/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-regex/license
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-regex/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-regex/readme.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-styles/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-styles/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-styles/license
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-styles/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/ansi-styles/readme.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/CHANGELOG.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/ariaPropsMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/domMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/elementRoleMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/commandRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/compositeRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/inputRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/landmarkRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/rangeRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/roletypeRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/sectionRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/sectionheadRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/selectRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/structureRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/widgetRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/abstract/windowRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/ariaAbstractRoles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/ariaDpubRoles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/ariaGraphicsRoles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/ariaLiteralRoles.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docAbstractRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docAcknowledgmentsRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docAfterwordRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docAppendixRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docBacklinkRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docBiblioentryRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docBibliographyRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docBibliorefRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docChapterRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docColophonRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docConclusionRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docCoverRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docCreditRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docCreditsRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docDedicationRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docEndnoteRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docEndnotesRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docEpigraphRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docEpilogueRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docErrataRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docExampleRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docFootnoteRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docForewordRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docGlossaryRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docGlossrefRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docIndexRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docIntroductionRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docNoterefRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docNoticeRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docPagebreakRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docPagelistRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docPartRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docPrefaceRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docPrologueRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docPullquoteRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docQnaRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docSubtitleRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docTipRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/dpub/docTocRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/graphics/graphicsDocumentRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/graphics/graphicsObjectRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/graphics/graphicsSymbolRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/alertRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/alertdialogRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/applicationRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/articleRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/bannerRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/blockquoteRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/buttonRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/captionRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/cellRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/checkboxRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/codeRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/columnheaderRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/comboboxRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/complementaryRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/contentinfoRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/definitionRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/deletionRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/dialogRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/directoryRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/documentRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/emphasisRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/feedRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/figureRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/formRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/genericRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/graphicsDocumentRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/graphicsObjectRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/graphicsSymbolRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/gridRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/gridcellRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/groupRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/headingRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/imgRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/insertionRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/linkRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/listRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/listboxRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/listitemRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/logRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/mainRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/markRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/marqueeRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/mathRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/menuRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/menubarRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/menuitemRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/menuitemcheckboxRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/menuitemradioRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/meterRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/navigationRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/noneRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/noteRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/optionRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/paragraphRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/presentationRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/progressbarRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/radioRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/radiogroupRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/regionRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/rowRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/rowgroupRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/rowheaderRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/scrollbarRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/searchRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/searchboxRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/separatorRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/sliderRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/spinbuttonRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/statusRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/strongRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/subscriptRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/superscriptRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/switchRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/tabRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/tableRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/tablistRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/tabpanelRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/termRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/textboxRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/timeRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/timerRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/toolbarRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/tooltipRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/treeRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/treegridRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/etc/roles/literal/treeitemRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/roleElementMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/rolesMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/util/iterationDecorator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/lib/util/iteratorProxy.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/aria-query/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/assertion-error/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/assertion-error/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/assertion-error/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/assertion-error/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/assertion-error/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/LICENSE.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/dist/bidi.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/dist/bidi.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/dist/bidi.min.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/dist/bidi.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/brackets.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/charTypes.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/data/bidiBrackets.data.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/data/bidiCharTypes.data.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/data/bidiMirroring.data.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/embeddingLevels.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/mirroring.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/reordering.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/bidi-js/src/util/parseCharacterMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/chai/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/chai/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/chai/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/chai/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/chai/register-assert.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/chai/register-expect.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/chai/register-should.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/convert-source-map/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/convert-source-map/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/convert-source-map/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/convert-source-map/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/convertor/create.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/convertor/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/data-patch.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/data.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/definition-syntax/SyntaxError.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/definition-syntax/generate.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/definition-syntax/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/definition-syntax/parse.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/definition-syntax/scanner.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/definition-syntax/walk.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/generator/create.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/generator/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/generator/sourceMap.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/generator/token-before.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/Lexer.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/error.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/generic-an-plus-b.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/generic-const.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/generic-urange.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/generic.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/match-graph.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/match.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/prepare-tokens.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/search.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/structure.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/trace.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/lexer/units.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/parser/SyntaxError.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/parser/create.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/parser/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/parser/parse-selector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/parser/sequence.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/container.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/font-face.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/import.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/layer.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/media.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/nest.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/page.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/scope.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/starting-style.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/atrule/supports.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/config/generator.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/config/lexer.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/config/mix.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/config/parser-selector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/config/parser.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/config/walker.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/create.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/function/expression.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/function/var.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/AnPlusB.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Atrule.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/AtrulePrelude.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/AttributeSelector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Block.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Brackets.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/CDC.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/CDO.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/ClassSelector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Combinator.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Comment.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Condition.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Declaration.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/DeclarationList.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Dimension.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Feature.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/FeatureFunction.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/FeatureRange.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Function.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/GeneralEnclosed.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Hash.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/IdSelector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Identifier.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Layer.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/LayerList.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/MediaQuery.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/MediaQueryList.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/NestingSelector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Nth.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Number.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Operator.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Parentheses.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Percentage.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/PseudoClassSelector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/PseudoElementSelector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Ratio.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Raw.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Rule.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Scope.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Selector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/SelectorList.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/String.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/StyleSheet.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/SupportsDeclaration.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/TypeSelector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/UnicodeRange.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Url.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/Value.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/WhiteSpace.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/index-generate.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/index-parse-selector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/index-parse.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/node/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/pseudo/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/pseudo/lang.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/scope/atrulePrelude.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/scope/default.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/scope/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/scope/selector.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/syntax/scope/value.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/tokenizer/OffsetToLocation.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/tokenizer/TokenStream.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/tokenizer/adopt-buffer.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/tokenizer/char-code-definitions.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/tokenizer/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/tokenizer/names.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/tokenizer/types.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/tokenizer/utils.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/utils/List.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/utils/clone.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/utils/create-custom-error.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/utils/ident.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/utils/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/utils/names.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/utils/string.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/utils/url.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/version.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/walker/create.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/cjs/walker/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/data/patch.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/dist/csstree.esm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/dist/csstree.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/dist/data.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/dist/data.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/dist/version.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/dist/version.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/convertor/create.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/convertor/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/data-patch.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/data.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/definition-syntax/SyntaxError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/definition-syntax/generate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/definition-syntax/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/definition-syntax/parse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/definition-syntax/scanner.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/definition-syntax/walk.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/generator/create.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/generator/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/generator/sourceMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/generator/token-before.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/Lexer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/error.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/generic-an-plus-b.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/generic-const.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/generic-urange.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/generic.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/match-graph.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/match.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/prepare-tokens.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/search.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/structure.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/trace.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/lexer/units.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/parser/SyntaxError.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/parser/create.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/parser/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/parser/parse-selector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/parser/sequence.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/container.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/font-face.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/import.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/layer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/media.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/nest.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/page.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/scope.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/starting-style.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/atrule/supports.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/config/generator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/config/lexer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/config/mix.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/config/parser-selector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/config/parser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/config/walker.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/create.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/function/expression.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/function/var.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/AnPlusB.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Atrule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/AtrulePrelude.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/AttributeSelector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Block.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Brackets.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/CDC.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/CDO.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/ClassSelector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Combinator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Comment.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Condition.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Declaration.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/DeclarationList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Dimension.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Feature.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/FeatureFunction.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/FeatureRange.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Function.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/GeneralEnclosed.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Hash.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/IdSelector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Identifier.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Layer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/LayerList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/MediaQuery.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/MediaQueryList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/NestingSelector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Nth.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Number.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Operator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Parentheses.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Percentage.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/PseudoClassSelector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/PseudoElementSelector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Ratio.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Raw.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Rule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Scope.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Selector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/SelectorList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/String.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/StyleSheet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/SupportsDeclaration.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/TypeSelector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/UnicodeRange.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Url.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/Value.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/WhiteSpace.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/index-generate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/index-parse-selector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/index-parse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/node/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/pseudo/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/pseudo/lang.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/scope/atrulePrelude.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/scope/default.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/scope/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/scope/selector.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/syntax/scope/value.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/tokenizer/OffsetToLocation.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/tokenizer/TokenStream.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/tokenizer/adopt-buffer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/tokenizer/char-code-definitions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/tokenizer/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/tokenizer/names.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/tokenizer/types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/tokenizer/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/utils/List.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/utils/clone.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/utils/create-custom-error.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/utils/ident.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/utils/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/utils/names.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/utils/string.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/utils/url.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/version.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/walker/create.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/lib/walker/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/css-tree/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/csstype/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/csstype/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/csstype/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/csstype/index.js.flow
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/csstype/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/data-urls/LICENSE.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/data-urls/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/data-urls/lib/parser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/data-urls/lib/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/data-urls/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/decimal.js/LICENCE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/decimal.js/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/decimal.js/decimal.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/decimal.js/decimal.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/decimal.js/decimal.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/decimal.js/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/dist/index.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/license
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/lite/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/lite/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/lite/index.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/lite/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dequal/readme.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/detect-libc/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/detect-libc/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/detect-libc/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/detect-libc/lib/detect-libc.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/detect-libc/lib/elf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/detect-libc/lib/filesystem.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/detect-libc/lib/process.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/detect-libc/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/.browserslistrc
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-description.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-description.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-description.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-description.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-description.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-description.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name-and-description.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name-and-description.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name-and-description.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name-and-description.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name-and-description.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name-and-description.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/accessible-name.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/getRole.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/getRole.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/getRole.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/getRole.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/getRole.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/getRole.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/index.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/index.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/is-inaccessible.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/is-inaccessible.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/is-inaccessible.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/is-inaccessible.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/is-inaccessible.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/is-inaccessible.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/SetLike.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/SetLike.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/SetLike.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/SetLike.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/SetLike.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/SetLike.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/array.from.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/array.from.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/array.from.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/array.from.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/array.from.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/array.from.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/iterator.d.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/iterator.d.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/iterator.d.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/polyfills/iterator.d.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/util.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/util.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/util.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/util.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/dist/util.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/dom-accessibility-api/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/decode-codepoint.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/decode-codepoint.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/decode-codepoint.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/decode-codepoint.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/decode.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/decode.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/decode.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/decode.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/encode.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/encode.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/encode.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/encode.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/escape.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/escape.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/escape.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/escape.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/decode-data-html.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/decode-data-html.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/decode-data-html.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/decode-data-html.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/decode-data-xml.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/decode-data-xml.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/decode-data-xml.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/decode-data-xml.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/encode-html.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/encode-html.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/encode-html.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/generated/encode-html.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/index.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/bin-trie-flags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/bin-trie-flags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/bin-trie-flags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/bin-trie-flags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/decode-shared.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/decode-shared.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/decode-shared.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/decode-shared.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/encode-shared.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/encode-shared.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/encode-shared.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/dist/internal/encode-shared.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/readme.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/decode-codepoint.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/decode.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/encode.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/escape.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/generated/decode-data-html.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/generated/decode-data-xml.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/generated/encode-html.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/index.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/internal/bin-trie-flags.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/internal/decode-shared.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/entities/src/internal/encode-shared.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/dist/lexer.asm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/dist/lexer.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/dist/lexer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/dist/lexer.minimal.asm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/dist/lexer.minimal.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/dist/lexer.minimal.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/lexer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/types/lexer.d.ts
[MARKED] Modules/Treatment-Plan/frontend/node_modules/es-module-lexer/types/lexer.minimal.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/src/async.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/src/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/src/sync.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/src/walker.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/types/async.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/types/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/types/sync.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/estree-walker/types/walker.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/SECURITY.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/branding.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/branding.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/messages.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/messages.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/overloads.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/overloads.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/utils.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/dist/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/expect-type/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/fdir/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/fdir/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/fdir/dist/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/fdir/dist/index.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/fdir/dist/index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/fdir/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/fdir/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/html-encoding-sniffer/LICENSE.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/html-encoding-sniffer/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/html-encoding-sniffer/lib/html-encoding-sniffer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/html-encoding-sniffer/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/is-potential-custom-element-name/LICENSE-MIT.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/is-potential-custom-element-name/README.md
[MARKED] Modules/Treatment-Plan/frontend/node_modules/is-potential-custom-element-name/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/is-potential-custom-element-name/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/js-tokens/CHANGELOG.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/js-tokens/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/js-tokens/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/js-tokens/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/js-tokens/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/LICENSE.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/api.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/css-property-definitions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/css-property-descriptors.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/css-property-metadata.js
[MARKED] Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/event-sets.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/AbortController.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/AbortSignal.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/AbstractRange.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/AddEventListenerOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/AssignedNodesOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Attr.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/BarProp.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/BeforeUnloadEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/BinaryType.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Blob.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/BlobCallback.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/BlobEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/BlobEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/BlobPropertyBag.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CDATASection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSConditionRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSContainerRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSCounterStyleRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSFontFaceRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSGroupingRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSImportRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSKeyframeRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSKeyframesRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSLayerBlockRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSLayerStatementRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSMediaRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSNamespaceRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSNestedDeclarations.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSPageRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSRuleList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSScopeRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSStyleDeclaration.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSStyleProperties.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSStyleRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSStyleSheet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSStyleSheetInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CSSSupportsRule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CanPlayTypeResult.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CharacterData.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CloseEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CloseEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Comment.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CompositionEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CompositionEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Crypto.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CustomElementConstructor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CustomElementRegistry.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CustomEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/CustomEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DOMException.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DOMImplementation.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DOMParser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DOMRect.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DOMRectInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DOMRectReadOnly.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DOMStringMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DOMTokenList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DeviceMotionEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DeviceMotionEventAcceleration.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DeviceMotionEventAccelerationInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DeviceMotionEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DeviceMotionEventRotationRate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DeviceMotionEventRotationRateInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DeviceOrientationEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DeviceOrientationEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Document.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DocumentFragment.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DocumentReadyState.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/DocumentType.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Element.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ElementCreationOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ElementDefinitionOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ElementInternals.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/EndingType.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ErrorEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ErrorEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Event.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/EventHandlerNonNull.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/EventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/EventListener.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/EventListenerOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/EventModifierInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/EventTarget.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/External.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/File.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/FileList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/FilePropertyBag.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/FileReader.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/FocusEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/FocusEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/FormData.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Function.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/GetRootNodeOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLAnchorElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLAreaElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLAudioElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLBRElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLBaseElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLBodyElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLButtonElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLCanvasElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLCollection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLDListElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLDataElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLDataListElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLDetailsElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLDialogElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLDirectoryElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLDivElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLEmbedElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLFieldSetElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLFontElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLFormControlsCollection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLFormElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLFrameElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLFrameSetElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLHRElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLHeadElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLHeadingElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLHtmlElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLIFrameElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLImageElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLInputElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLLIElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLLabelElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLLegendElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLLinkElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLMapElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLMarqueeElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLMediaElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLMenuElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLMetaElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLMeterElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLModElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLOListElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLObjectElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLOptGroupElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLOptionElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLOptionsCollection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLOutputElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLParagraphElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLParamElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLPictureElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLPreElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLProgressElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLQuoteElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLScriptElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLSelectElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLSlotElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLSourceElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLSpanElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLStyleElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTableCaptionElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTableCellElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTableColElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTableElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTableRowElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTableSectionElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTemplateElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTextAreaElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTimeElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTitleElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLTrackElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLUListElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLUnknownElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HTMLVideoElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HashChangeEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/HashChangeEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Headers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/History.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/InputEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/InputEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/KeyboardEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/KeyboardEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Location.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MediaList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MessageEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MessageEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MimeType.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MimeTypeArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MouseEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MouseEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MutationCallback.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MutationObserver.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MutationObserverInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/MutationRecord.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/NamedNodeMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Navigator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/NodeFilter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/NodeIterator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/NodeList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/OnBeforeUnloadEventHandlerNonNull.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/OnErrorEventHandlerNonNull.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/PageTransitionEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/PageTransitionEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Performance.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Plugin.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/PluginArray.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/PointerEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/PointerEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/PopStateEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/PopStateEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ProcessingInstruction.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ProgressEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ProgressEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/PromiseRejectionEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/PromiseRejectionEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/RadioNodeList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Range.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGAnimatedPreserveAspectRatio.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGAnimatedRect.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGAnimatedString.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGBoundingBoxOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGDefsElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGDescElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGGElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGGraphicsElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGMetadataElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGNumber.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGPreserveAspectRatio.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGRect.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGSVGElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGStringList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGSwitchElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGSymbolElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SVGTitleElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Screen.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ScrollBehavior.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ScrollIntoViewOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ScrollLogicalPosition.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ScrollOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ScrollRestoration.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Selection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SelectionMode.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ShadowRoot.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ShadowRootInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ShadowRootMode.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/StaticRange.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/StaticRangeInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Storage.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/StorageEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/StorageEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/StyleSheet.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/StyleSheetList.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SubmitEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SubmitEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/SupportedType.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/Text.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TextDecodeOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TextDecoder.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TextDecoderOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TextEncoder.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TextEncoderEncodeIntoResult.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TextTrackKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TouchEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TouchEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TransitionEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TransitionEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/TreeWalker.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/UIEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/UIEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/ValidityState.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/VisibilityState.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/VoidFunction.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/WebSocket.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/WheelEvent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/WheelEventInit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/XMLDocument.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/XMLHttpRequest.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/XMLHttpRequestEventTarget.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/XMLHttpRequestResponseType.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/XMLHttpRequestUpload.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/XMLSerializer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/idl/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/generated/js-globals.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/Window.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/default-stylesheet.css
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/not-implemented.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/parser/html.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/parser/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/parser/xml.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/resources/async-resource-queue.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/resources/decompress-interceptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/resources/jsdom-dispatcher.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/resources/per-document-resource-loader.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/resources/request-interceptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/resources/request-manager.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/resources/resource-queue.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/browser/resources/stream-handler.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/level3/xpath.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/aborting/AbortController-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/aborting/AbortSignal-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/attributes.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/attributes/Attr-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/attributes/NamedNodeMap-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/constraint-validation/DefaultConstraintValidation-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/constraint-validation/ValidityState-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/crypto/Crypto-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSConditionRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSContainerRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSCounterStyleRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSFontFaceRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSGroupingRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSImportRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSKeyframeRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSKeyframesRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSLayerBlockRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSLayerStatementRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSMediaRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSNamespaceRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSNestedDeclarations-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSPageRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSRuleList-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSScopeRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSStyleDeclaration-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSStyleProperties-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSStyleRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSStyleSheet-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/CSSSupportsRule-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/ElementCSSInlineStyle-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/MediaList-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/StyleSheet-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/StyleSheetList-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/helpers/computed-style.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/helpers/css-parser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/helpers/css-values.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/helpers/generic-property-descriptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/helpers/patched-csstree.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/helpers/shorthand-properties.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/helpers/stylesheets.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/helpers/system-colors.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/background.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/backgroundAttachment.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/backgroundClip.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/backgroundColor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/backgroundImage.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/backgroundOrigin.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/backgroundPosition.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/backgroundRepeat.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/backgroundSize.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/border.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderBottom.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderBottomColor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderBottomStyle.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderBottomWidth.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderColor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderLeft.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderLeftColor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderLeftStyle.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderLeftWidth.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderRight.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderRightColor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderRightStyle.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderRightWidth.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderSpacing.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderStyle.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderTop.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderTopColor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderTopStyle.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderTopWidth.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/borderWidth.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/bottom.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/clip.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/display.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/flex.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/flexBasis.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/flexGrow.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/flexShrink.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/font.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/fontFamily.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/fontSize.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/fontStyle.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/fontVariant.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/fontWeight.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/height.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/left.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/lineHeight.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/margin.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/marginBottom.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/marginLeft.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/marginRight.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/marginTop.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/opacity.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/padding.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/paddingBottom.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/paddingLeft.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/paddingRight.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/paddingTop.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/right.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/top.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/css/properties/width.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/custom-elements/CustomElementRegistry-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/custom-elements/ElementInternals-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/deviceorientation/DeviceMotionEventAcceleration-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/deviceorientation/DeviceMotionEventRotationRate-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/documents.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/domparsing/DOMParser-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/domparsing/InnerHTML-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/domparsing/XMLSerializer-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/domparsing/parse5-adapter-serialization.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/domparsing/serialization.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/encoding/TextDecoder-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/encoding/TextEncoder-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/BeforeUnloadEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/BlobEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/CloseEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/CompositionEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/CustomEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/DeviceMotionEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/DeviceOrientationEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/ErrorEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/Event-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/EventModifierMixin-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/EventTarget-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/FocusEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/HashChangeEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/InputEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/KeyboardEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/MessageEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/MouseEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/PageTransitionEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/PointerEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/PopStateEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/ProgressEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/PromiseRejectionEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/StorageEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/SubmitEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/TouchEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/TransitionEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/UIEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/events/WheelEvent-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/fetch/Headers-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/fetch/header-list.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/fetch/header-types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/fetch/header-utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/file-api/Blob-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/file-api/File-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/file-api/FileList-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/file-api/FileReader-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/geometry/DOMRect-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/geometry/DOMRectReadOnly-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/binary-data.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/by-id-cache.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/create-element.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/create-event-accessor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/custom-elements.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/dates-and-times.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/details.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/encoding.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/events.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/focusing.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/form-controls.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/html-constructor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/internal-constants.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/is-window.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/iterable-weak-set.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/json.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/mutation-observers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/namespaces.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/number-and-date-inputs.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/ordered-set.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/page-transition-event.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/runtime-script-errors.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/shadow-dom.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/strings.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/svg/basic-types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/svg/render.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/text.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/traversal.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/helpers/validate-names.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/hr-time/Performance-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/interfaces.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/mutation-observer/MutationObserver-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/mutation-observer/MutationRecord-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/MimeType-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/MimeTypeArray-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/Navigator-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/NavigatorConcurrentHardware-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/NavigatorCookies-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/NavigatorID-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/NavigatorLanguage-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/NavigatorOnLine-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/NavigatorPlugins-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/Plugin-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/navigator/PluginArray-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/node-document-position.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/node-type.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/CDATASection-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/CharacterData-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/ChildNode-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/Comment-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/DOMImplementation-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/DOMStringMap-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/DOMTokenList-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/Document-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/DocumentFragment-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/DocumentOrShadowRoot-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/DocumentType-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/Element-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/ElementContentEditable-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/GlobalEventHandlers-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLAnchorElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLAreaElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLAudioElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLBRElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLBaseElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLBodyElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLButtonElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLCanvasElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLCollection-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLDListElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLDataElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLDataListElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLDetailsElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLDialogElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLDirectoryElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLDivElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLEmbedElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLFieldSetElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLFontElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLFormControlsCollection-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLFormElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLFrameElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLFrameSetElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLHRElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLHeadElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLHeadingElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLHtmlElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLHyperlinkElementUtils-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLIFrameElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLImageElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLInputElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLLIElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLLabelElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLLegendElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLLinkElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLMapElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLMarqueeElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLMediaElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLMenuElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLMetaElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLMeterElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLModElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLOListElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLObjectElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLOptGroupElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLOptionElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLOptionsCollection-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLOrSVGElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLOutputElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLParagraphElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLParamElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLPictureElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLPreElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLProgressElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLQuoteElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLScriptElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLSelectElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLSlotElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLSourceElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLSpanElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLStyleElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTableCaptionElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTableCellElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTableColElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTableElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTableRowElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTableSectionElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTemplateElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTextAreaElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTimeElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTitleElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLTrackElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLUListElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLUnknownElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/HTMLVideoElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/LinkStyle-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/Node-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/NodeList-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/NonDocumentTypeChildNode-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/NonElementParentNode-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/ParentNode-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/ProcessingInstruction-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/RadioNodeList-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGDefsElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGDescElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGGElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGGraphicsElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGMetadataElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGSVGElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGSwitchElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGSymbolElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGTests-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/SVGTitleElement-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/ShadowRoot-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/Slotable-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/Text-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/WindowEventHandlers-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/nodes/XMLDocument-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/range/AbstractRange-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/range/Range-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/range/StaticRange-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/range/boundary-point.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/selection/Selection-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/svg/SVGAnimatedPreserveAspectRatio-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/svg/SVGAnimatedRect-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/svg/SVGAnimatedString-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/svg/SVGListBase.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/svg/SVGNumber-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/svg/SVGPreserveAspectRatio-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/svg/SVGRect-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/svg/SVGStringList-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/traversal/NodeIterator-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/traversal/TreeWalker-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/traversal/helpers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/webidl/DOMException-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/websockets/WebSocket-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/webstorage/Storage-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/window-properties.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/window/BarProp-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/window/External-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/window/History-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/window/Location-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/window/Screen-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/window/SessionHistory.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/window/navigation.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/xhr/FormData-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/xhr/XMLHttpRequest-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/xhr/XMLHttpRequestEventTarget-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/xhr/XMLHttpRequestUpload-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/xhr/multipart-form-data.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/xhr/xhr-sync-worker.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/living/xhr/xhr-utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/lib/jsdom/virtual-console.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/jsdom/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss-linux-x64-gnu/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss-linux-x64-gnu/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss-linux-x64-gnu/lightningcss.linux-x64-gnu.node
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss-linux-x64-gnu/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/ast.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/ast.js.flow
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/browserslistToTargets.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/composeVisitors.js
[MARKED] Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/flags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/index.js.flow
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/index.mjs
[MARKED] Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/targets.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/node/targets.js.flow
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lightningcss/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/diagnostics-channel-browser.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/diagnostics-channel-browser.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/diagnostics-channel.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/diagnostics-channel.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/index.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/index.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/index.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/perf.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/perf.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/perf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/browser/perf.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/diagnostics-channel-cjs.cjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/diagnostics-channel-cjs.d.cts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/diagnostics-channel.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/diagnostics-channel.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/index.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/index.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/index.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/diagnostics-channel-node.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/diagnostics-channel-node.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/diagnostics-channel.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/diagnostics-channel.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/index.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/index.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/index.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/perf.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/perf.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/perf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/node/perf.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/perf.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/perf.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/perf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/commonjs/perf.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/diagnostics-channel-browser.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/diagnostics-channel-browser.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/diagnostics-channel.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/diagnostics-channel.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/index.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/index.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/index.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/perf.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/perf.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/perf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/browser/perf.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/diagnostics-channel-esm.d.mts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/diagnostics-channel-esm.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/diagnostics-channel.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/diagnostics-channel.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/index.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/index.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/index.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/diagnostics-channel-node.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/diagnostics-channel-node.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/diagnostics-channel.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/diagnostics-channel.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/index.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/index.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/index.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/perf.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/perf.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/perf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/node/perf.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/perf.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/perf.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/perf.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/dist/esm/perf.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lru-cache/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/bin/bin.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/bower.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/libs/base64-string.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/libs/lz-string.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/libs/lz-string.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/reference/lz-string-1.0.2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/tests/SpecRunner.html
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/tests/lib/jasmine-1.3.1/MIT.LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/tests/lib/jasmine-1.3.1/jasmine-html.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/tests/lib/jasmine-1.3.1/jasmine.css
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/tests/lib/jasmine-1.3.1/jasmine.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/tests/lz-string-spec.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/lz-string/typings/lz-string.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/dist/magic-string.cjs.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/dist/magic-string.cjs.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/dist/magic-string.cjs.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/dist/magic-string.es.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/dist/magic-string.es.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/dist/magic-string.es.mjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/dist/magic-string.umd.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/dist/magic-string.umd.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/magic-string/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/api/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/api/inheritance.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/api/inheritance.schema.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/at-rules.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/at-rules.schema.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/definitions.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/functions.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/functions.schema.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/properties.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/properties.schema.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/selectors.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/selectors.schema.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/syntaxes.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/syntaxes.schema.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/types.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/types.schema.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/units.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/css/units.schema.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/l10n/css.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/l10n/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/mdn-data/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/async/index.browser.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/async/index.browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/async/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/async/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/async/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/async/index.native.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/async/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/bin/nanoid.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/index.browser.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/index.browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/index.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/nanoid.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/non-secure/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/non-secure/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/non-secure/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/non-secure/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/url-alphabet/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/url-alphabet/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/nanoid/url-alphabet/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/dist/browser.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/dist/browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/dist/browser.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/dist/core.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/dist/core.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/dist/node.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/dist/node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/obug/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/doctype.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/doctype.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/error-codes.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/error-codes.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/foreign-content.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/foreign-content.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/html.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/html.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/token.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/token.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/unicode.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/common/unicode.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/parser/formatting-element-list.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/parser/formatting-element-list.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/parser/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/parser/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/parser/open-element-stack.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/parser/open-element-stack.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/serializer/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/serializer/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/tokenizer/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/tokenizer/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/tokenizer/preprocessor.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/tokenizer/preprocessor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/tree-adapters/default.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/tree-adapters/default.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/tree-adapters/interface.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/dist/tree-adapters/interface.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/parse5/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/index.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/shared/pathe.BSlhyZSM.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/shared/pathe.M-eThtNZ.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/utils.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/utils.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/utils.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/utils.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/dist/utils.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pathe/utils.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picocolors/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picocolors/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picocolors/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picocolors/picocolors.browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picocolors/picocolors.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picocolors/picocolors.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picocolors/types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picomatch/LICENSE
[MARKED] Modules/Treatment-Plan/frontend/node_modules/picomatch/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picomatch/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picomatch/lib/constants.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picomatch/lib/parse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picomatch/lib/picomatch.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picomatch/lib/scan.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picomatch/lib/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picomatch/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/picomatch/posix.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/at-rule.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/at-rule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/comment.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/comment.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/container.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/container.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/css-syntax-error.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/css-syntax-error.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/declaration.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/declaration.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/document.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/document.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/fromJSON.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/fromJSON.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/input.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/input.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/lazy-result.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/lazy-result.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/list.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/list.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/map-generator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/no-work-result.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/no-work-result.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/node.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/parse.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/parse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/parser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/postcss.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/postcss.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/postcss.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/postcss.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/previous-map.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/previous-map.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/processor.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/processor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/result.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/result.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/root.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/root.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/rule.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/rule.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/stringifier.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/stringifier.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/stringify.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/stringify.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/symbols.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/terminal-highlight.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/tokenize.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/warn-once.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/warning.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/lib/warning.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/postcss/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/collections.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/collections.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/AsymmetricMatcher.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/AsymmetricMatcher.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/ConvertAnsi.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/ConvertAnsi.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/DOMCollection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/DOMCollection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/DOMElement.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/DOMElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/Immutable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/Immutable.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/ReactElement.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/ReactElement.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/ReactTestComponent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/ReactTestComponent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/lib/escapeHTML.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/lib/escapeHTML.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/lib/markup.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/plugins/lib/markup.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/build/types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/pretty-format/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/punycode/LICENSE-MIT.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/punycode/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/punycode/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/punycode/punycode.es6.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/punycode/punycode.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-client.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-client.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-profiling.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-profiling.profiling.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server-legacy.browser.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server-legacy.browser.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server-legacy.node.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server-legacy.node.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server.browser.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server.browser.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server.bun.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server.bun.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server.edge.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server.edge.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server.node.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-server.node.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-test-utils.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom-test-utils.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom.react-server.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/cjs/react-dom.react-server.production.js
[MARKED] Modules/Treatment-Plan/frontend/node_modules/react-dom/client.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/client.react-server.js
[MARKED] Modules/Treatment-Plan/frontend/node_modules/react-dom/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/package.json
[MARKED] Modules/Treatment-Plan/frontend/node_modules/react-dom/profiling.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/profiling.react-server.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/react-dom.react-server.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/server.browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/server.bun.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/server.edge.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/server.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/server.node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/server.react-server.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/static.browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/static.edge.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/static.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/static.node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/static.react-server.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-dom/test-utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-is/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-is/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-is/build-info.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-is/cjs/react-is.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-is/cjs/react-is.production.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-is/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-is/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-is/umd/react-is.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react-is/umd/react-is.production.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-compiler-runtime.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-compiler-runtime.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-compiler-runtime.profiling.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-dev-runtime.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-dev-runtime.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-dev-runtime.profiling.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-dev-runtime.react-server.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-dev-runtime.react-server.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-runtime.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-runtime.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-runtime.profiling.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-runtime.react-server.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react-jsx-runtime.react-server.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react.react-server.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/cjs/react.react-server.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/compiler-runtime.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/jsx-dev-runtime.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/jsx-dev-runtime.react-server.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/jsx-runtime.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/jsx-runtime.react-server.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/react/react.react-server.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/require-from-string/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/require-from-string/license
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/require-from-string/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/require-from-string/readme.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/bin/cli.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/cli.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/cli.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/config.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/config.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/experimental-index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/experimental-index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/experimental-runtime-types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/filter-index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/filter-index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/get-log-filter.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/get-log-filter.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/parallel-plugin-worker.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/parallel-plugin-worker.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/parallel-plugin.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/parallel-plugin.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/parse-ast-index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/parse-ast-index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/plugins-index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/plugins-index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/binding-D26QphWG.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/binding-TuFFIE_J.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/bindingify-input-options-XPJLJOD0.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/constructors-BbWPse2X.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/constructors-D_3i7dpX.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/define-config-BhJ90aEv.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/define-config-Demdg3_4.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/dist-DKbukT1H.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/error-BHRSI0R7.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/get-log-filter-BpNVNJ5-.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/load-config-BL_FI6dc.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/logging-BSNejiLS.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/logs-ZGEh6uhb.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/misc-CoQm4NHO.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/normalize-string-or-regex-dnh67V_w.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/parse-D4dtlfWy.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/prompt--dNycKSZ.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/resolve-tsconfig-DxqIJB3x.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/rolldown-ChpIlMRm.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/rolldown-build-CtPvmZgJ.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/transform-BPrUvqEZ.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/shared/watch-B1b0gmVh.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/utils-index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/dist/utils-index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/rolldown/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/saxes/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/saxes/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/saxes/saxes.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/saxes/saxes.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/saxes/saxes.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/cjs/scheduler-unstable_mock.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/cjs/scheduler-unstable_mock.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/cjs/scheduler-unstable_post_task.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/cjs/scheduler-unstable_post_task.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/cjs/scheduler.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/cjs/scheduler.native.development.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/cjs/scheduler.native.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/cjs/scheduler.production.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/index.native.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/unstable_mock.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/scheduler/unstable_post_task.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/siginfo/.travis.yml
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/siginfo/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/siginfo/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/siginfo/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/siginfo/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/siginfo/test.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/LICENSE
[MARKED] Modules/Treatment-Plan/frontend/node_modules/source-map-js/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/array-set.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/base64-vlq.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/base64.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/binary-search.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/mapping-list.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/quick-sort.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/source-map-consumer.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/source-map-consumer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/source-map-generator.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/source-map-generator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/source-node.d.ts
[MARKED] Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/source-node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/lib/util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/source-map.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/source-map-js/source-map.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/stackback/.npmignore
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/stackback/.travis.yml
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/stackback/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/stackback/formatstack.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/stackback/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/stackback/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/stackback/test.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/std-env/LICENCE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/std-env/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/std-env/dist/index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/std-env/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/std-env/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/symbol-tree/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/symbol-tree/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/symbol-tree/lib/SymbolTree.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/symbol-tree/lib/SymbolTreeNode.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/symbol-tree/lib/TreeIterator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/symbol-tree/lib/TreePosition.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/symbol-tree/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinybench/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinybench/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinybench/dist/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinybench/dist/index.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinybench/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinybench/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinybench/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyexec/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyexec/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyexec/dist/main.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyexec/dist/main.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyexec/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyglobby/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyglobby/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyglobby/dist/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyglobby/dist/index.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyglobby/dist/index.d.mts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyglobby/dist/index.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyglobby/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyrainbow/LICENCE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyrainbow/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyrainbow/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyrainbow/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tinyrainbow/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/domain-without-suffix.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/domain-without-suffix.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/domain.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/domain.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/extract-hostname.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/extract-hostname.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/factory.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/factory.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/is-ip.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/is-ip.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/is-special-use.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/is-special-use.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/is-valid.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/is-valid.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/lookup/fast-path.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/lookup/fast-path.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/lookup/interface.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/lookup/interface.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/options.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/options.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/subdomain.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/src/subdomain.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/cjs/tsconfig.tsbuildinfo
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/domain-without-suffix.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/domain-without-suffix.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/domain.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/domain.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/extract-hostname.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/extract-hostname.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/factory.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/factory.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/is-ip.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/is-ip.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/is-special-use.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/is-special-use.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/is-valid.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/is-valid.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/lookup/fast-path.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/lookup/fast-path.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/lookup/interface.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/lookup/interface.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/options.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/options.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/subdomain.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/src/subdomain.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/es6/tsconfig.bundle.tsbuildinfo
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/domain-without-suffix.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/domain.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/extract-hostname.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/factory.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/is-ip.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/is-special-use.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/is-valid.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/lookup/fast-path.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/lookup/interface.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/options.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/dist/types/src/subdomain.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/index.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/domain-without-suffix.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/domain.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/extract-hostname.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/factory.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/is-ip.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/is-special-use.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/is-valid.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/lookup/fast-path.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/lookup/interface.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/options.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts-core/src/subdomain.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/bin/cli.js
[MARKED] Modules/Treatment-Plan/frontend/node_modules/tldts/dist/cjs/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/cjs/index.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/tldts/dist/cjs/src/data/trie.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/cjs/src/data/trie.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/cjs/src/suffix-trie.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/cjs/src/suffix-trie.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/cjs/tsconfig.tsbuildinfo
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/es6/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/es6/index.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/tldts/dist/es6/src/data/trie.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/es6/src/data/trie.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/es6/src/suffix-trie.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/es6/src/suffix-trie.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/es6/tsconfig.bundle.tsbuildinfo
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/index.cjs.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/index.cjs.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/index.esm.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/index.esm.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/index.umd.min.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/index.umd.min.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/types/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/types/src/data/trie.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/dist/types/src/suffix-trie.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/index.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/package.json
[MARKED] Modules/Treatment-Plan/frontend/node_modules/tldts/src/data/trie.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tldts/src/suffix-trie.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tough-cookie/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tough-cookie/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tough-cookie/dist/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tough-cookie/dist/index.cjs.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tough-cookie/dist/index.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tough-cookie/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tough-cookie/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tough-cookie/dist/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tough-cookie/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tr46/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tr46/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tr46/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tr46/lib/mappingTable.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tr46/lib/regexes.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tr46/lib/statusMapping.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/tr46/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/NOTICE.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/bin/tsc
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/api.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/api.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/api.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/api.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/client.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/client.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/client.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/client.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/types.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/async/types.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/compilerOptions.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/compilerOptions.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/compilerOptions.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/compilerOptions.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/fs.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/fs.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/fs.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/fs.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/encoder.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/encoder.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/encoder.generated.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/encoder.generated.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/encoder.generated.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/encoder.generated.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/encoder.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/encoder.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/msgpack.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/msgpack.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/msgpack.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/msgpack.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.generated.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.generated.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.generated.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.generated.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.infrastructure.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.infrastructure.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.infrastructure.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.infrastructure.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/node.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/protocol.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/protocol.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/protocol.generated.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/protocol.generated.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/protocol.generated.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/protocol.generated.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/protocol.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/protocol.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/wtf8.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/wtf8.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/wtf8.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/node/wtf8.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/options.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/options.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/options.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/options.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/path.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/path.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/path.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/path.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/proto.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/proto.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/proto.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/proto.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sourceFileCache.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sourceFileCache.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sourceFileCache.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sourceFileCache.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/api.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/api.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/api.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/api.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/client.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/client.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/client.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/client.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/types.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/types.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/sync/types.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/syncChannel.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/syncChannel.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/syncChannel.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/syncChannel.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/timing.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/timing.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/timing.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/api/timing.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/ast.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/ast.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/ast.generated.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/ast.generated.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/ast.generated.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/ast.generated.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/ast.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/ast.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/astnav.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/astnav.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/astnav.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/astnav.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/clone.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/clone.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/clone.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/clone.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/factory.generated.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/factory.generated.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/factory.generated.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/factory.generated.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/index.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/index.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/is.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/is.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/is.generated.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/is.generated.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/is.generated.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/is.generated.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/is.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/is.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/jsdoc.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/jsdoc.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/jsdoc.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/jsdoc.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/scanner.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/scanner.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/scanner.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/scanner.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/utils.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/utils.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/utils.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/visitor.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/visitor.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/visitor.generated.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/visitor.generated.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/visitor.generated.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/visitor.generated.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/visitor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/ast/visitor.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/characterCodes.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/characterCodes.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/characterCodes.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/characterCodes.enum.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/characterCodes.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/characterCodes.enum.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/characterCodes.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/characterCodes.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/commentDirectiveType.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/commentDirectiveType.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/commentDirectiveType.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/commentDirectiveType.enum.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/commentDirectiveType.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/commentDirectiveType.enum.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/commentDirectiveType.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/commentDirectiveType.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/completionItemKind.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/diagnosticCategory.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/elementFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/internalSymbolName.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/jsxEmit.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/languageVariant.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/languageVariant.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/languageVariant.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/languageVariant.enum.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/languageVariant.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/languageVariant.enum.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/languageVariant.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/languageVariant.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/modifierFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleDetectionKind.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleKind.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/moduleResolutionKind.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/newLineKind.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeBuilderFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/nodeFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/objectFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/outerExpressionKinds.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/regularExpressionFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/regularExpressionFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/regularExpressionFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/regularExpressionFlags.enum.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/regularExpressionFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/regularExpressionFlags.enum.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/regularExpressionFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/regularExpressionFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptKind.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptKind.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptKind.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptKind.enum.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptKind.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptKind.enum.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptKind.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptTarget.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptTarget.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptTarget.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptTarget.enum.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptTarget.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptTarget.enum.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptTarget.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/scriptTarget.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/signatureKind.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/symbolFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/syntaxKind.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/tokenFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typeFlags.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.enum.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.enum.d.ts.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.enum.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.enum.js.map
[MARKED] Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/enums/typePredicateKind.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/internal/utils.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/internal/utils.d.ts.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/internal/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/dist/internal/utils.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/lib/getExePath.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/lib/getExePath.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/lib/tsc.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/lib/version.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/lib/version.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/License.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/browser/main.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/browser/main.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/browser/ril.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/browser/ril.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/api.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/api.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/cancellation.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/cancellation.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/connection.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/connection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/disposable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/disposable.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/encoding.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/encoding.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/events.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/events.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/is.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/is.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/linkedMap.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/linkedMap.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageBuffer.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageBuffer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageReader.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageReader.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageWriter.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageWriter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messages.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messages.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/ral.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/ral.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/semaphore.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/semaphore.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/sharedArrayCancellation.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/sharedArrayCancellation.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/node/main.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/node/main.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/node/ril.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/lib/node/ril.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/typescript/vendor/vscode-jsonrpc/typings/thenable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Agent.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/BalancedPool.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/CacheStorage.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/CacheStore.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Client.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/ClientStats.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Connector.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/ContentType.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Cookies.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Debug.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/DiagnosticsChannel.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Dispatcher.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/EnvHttpProxyAgent.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Errors.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/EventSource.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Fetch.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/GlobalInstallation.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/H2CClient.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/MockAgent.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/MockCallHistory.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/MockCallHistoryLog.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/MockClient.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/MockErrors.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/MockPool.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Pool.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/PoolStats.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/ProxyAgent.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/RedirectHandler.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/RetryAgent.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/RetryHandler.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/RoundRobinPool.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/SnapshotAgent.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Socks5ProxyAgent.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/Util.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/WebSocket.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/api/api-lifecycle.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/best-practices/client-certificate.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/best-practices/crawling.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/best-practices/mocking-request.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/best-practices/proxy.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/best-practices/undici-vs-builtin-fetch.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/docs/docs/best-practices/writing-tests.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/index-fetch.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/api/abort-signal.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/api/api-connect.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/api/api-pipeline.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/api/api-request.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/api/api-stream.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/api/api-upgrade.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/api/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/api/readable.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/cache/memory-cache-store.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/cache/sqlite-cache-store.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/connect.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/constants.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/diagnostics.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/errors.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/request.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/socks5-client.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/socks5-utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/symbols.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/tree.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/core/util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/agent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/balanced-pool.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/client-h1.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/client-h2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/client.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/dispatcher-base.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/dispatcher.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/env-http-proxy-agent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/fixed-queue.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/h2c-client.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/pool-base.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/pool.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/proxy-agent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/retry-agent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/round-robin-pool.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/dispatcher/socks5-proxy-agent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/encoding/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/global.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/handler/cache-handler.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/handler/cache-revalidation-handler.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/handler/decorator-handler.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/handler/deduplication-handler.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/handler/redirect-handler.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/handler/retry-handler.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/handler/unwrap-handler.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/handler/wrap-handler.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/interceptor/cache.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/interceptor/decompress.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/interceptor/deduplicate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/interceptor/dns.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/interceptor/dump.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/interceptor/redirect.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/interceptor/response-error.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/interceptor/retry.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/llhttp/.gitkeep
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/llhttp/constants.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/llhttp/constants.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/llhttp/llhttp-wasm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/llhttp/llhttp_simd-wasm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/llhttp/utils.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/llhttp/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/mock-agent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/mock-call-history.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/mock-client.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/mock-errors.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/mock-interceptor.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/mock-pool.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/mock-symbols.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/mock-utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/pending-interceptors-formatter.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/snapshot-agent.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/snapshot-recorder.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/mock/snapshot-utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/util/cache.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/util/date.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/util/promise.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/util/runtime-features.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/util/stats.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/util/timers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/cache/cache.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/cache/cachestorage.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/cache/util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/cookies/constants.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/cookies/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/cookies/parse.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/cookies/util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/eventsource/eventsource-stream.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/eventsource/eventsource.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/eventsource/util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/body.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/constants.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/data-url.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/formdata-parser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/formdata.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/global.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/headers.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/request.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/response.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/fetch/util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/infra/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/subresource-integrity/Readme.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/subresource-integrity/subresource-integrity.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/webidl/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/connection.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/constants.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/events.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/frame.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/permessage-deflate.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/receiver.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/sender.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/stream/websocketerror.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/stream/websocketstream.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/util.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/lib/web/websocket/websocket.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/scripts/strip-comments.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/agent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/api.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/balanced-pool.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/cache-interceptor.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/cache.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/client-stats.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/client.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/connector.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/content-type.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/cookies.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/diagnostics-channel.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/dispatcher.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/env-http-proxy-agent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/errors.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/eventsource.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/fetch.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/formdata.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/global-dispatcher.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/global-origin.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/h2c-client.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/handlers.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/header.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/interceptors.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/mock-agent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/mock-call-history.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/mock-client.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/mock-errors.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/mock-interceptor.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/mock-pool.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/patch.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/pool-stats.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/pool.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/proxy-agent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/readable.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/retry-agent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/retry-handler.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/round-robin-pool.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/snapshot-agent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/socks5-proxy-agent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/util.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/utility.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/webidl.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/undici/types/websocket.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/bin/openChrome.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/bin/vite.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/client.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/client/client.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/client/env.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/chunks/build.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/chunks/dist.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/chunks/lib.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/chunks/moduleRunnerTransport.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/chunks/node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/chunks/postcss-import.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/cli.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/internal.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/internal.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/module-runner.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/dist/node/module-runner.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/misc/false.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/misc/true.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/customEvent.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/hmrPayload.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/hot.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/import-meta.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/importGlob.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/importMeta.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/internal/cssPreprocessorOptions.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/internal/esbuildOptions.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/internal/lightningcssOptions.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/internal/rollupTypeCompat.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/internal/terserOptions.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vite/types/metadata.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/browser/context.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/browser/context.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/config.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/coverage.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/browser.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/browser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/_commonjsHelpers.D26ty3Ew.js
[MARKED] Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/acorn.B2iPLyUM.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/base.B6Opl8PE.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/benchmark.CX_oY03V.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/benchmark.d.DAaHLpsq.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/browser.d.BcoexmFG.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/cac.DdICfEr1.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/cli-api.BK8pd4xc.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/config.d.A1h_Y6Jt.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/console.3WNpx0tS.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/constants.CPYnjOGj.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/coverage.CTzCuANN.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/coverage.DM_a_rWm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/coverage.d.BZtK59WP.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/creator.DgVhQm5q.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/defaults.9aQKnqFk.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/env.D4Lgay0q.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/environment.d.CrsxCzP1.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/evaluatedModules.Dg1zASAC.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/evaluatedModules.d.BxJ5omdx.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/global.d.DVsSRdQ5.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/globals.Dj1TGiMC.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/index.BCY_7LL2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/index.CMESou6r.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/index.Chj8NDwU.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/index.DC7d2Pf8.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/index.DXx9Dtk7.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/index.DdgEv5B1.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/index.UpGiHP7g.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/index.og1WyBLx.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/init-forks.H5ZuobOQ.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/init-threads.6kl1khcL.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/init.k9zZ9sLh.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/inspector.CvyFGlXm.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/modules.BJuCwlRJ.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/native.DPzPHdi5.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/nativeModuleMocker.BkNfQMkH.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/nativeModuleRunner.BIakptoF.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/node.COQbm6gK.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/plugin.d.DwFIiJ7i.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/reporters.d.DtoKVV2s.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/rpc.MzXet3jl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/rpc.d.B_8sPU0w.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/setup-common.DYx3LtFI.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/startVitestModuleRunner.DB-7oCpn.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/suite.d.udJtyAgw.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/test.DNmyFkvJ.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/traces.DT5aQ62U.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/traces.d.D2T_R8rx.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/utils.BS4fH3nR.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/utils.BX5Fg8C4.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/vm.CXMd5FHa.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/chunks/worker.d.ZpHpO4yb.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/cli.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/config.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/config.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/config.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/coverage.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/coverage.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/environments.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/environments.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/index.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/module-evaluator.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/module-evaluator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/node.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/node.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/nodejs-worker-loader.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/path.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/reporters.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/reporters.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/runners.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/runners.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/runtime.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/runtime.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/snapshot.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/snapshot.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/spy.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/suite.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/suite.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/worker.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/worker.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/workers/forks.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/workers/runVmTests.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/workers/threads.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/workers/vmForks.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/dist/workers/vmThreads.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/environments.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/globals.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/import-meta.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/importMeta.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/index.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/index.d.cts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/jsdom.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/mocker.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/node.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/optional-runtime-types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/optional-types.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/reporters.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/runners.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/snapshot.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/suite.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/suppress-warnings.cjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/vitest.mjs
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/vitest/worker.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/w3c-xmlserializer/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/w3c-xmlserializer/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/w3c-xmlserializer/lib/attributes.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/w3c-xmlserializer/lib/constants.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/w3c-xmlserializer/lib/serialize.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/w3c-xmlserializer/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/webidl-conversions/LICENSE.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/webidl-conversions/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/webidl-conversions/lib/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/webidl-conversions/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/LICENSE.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/lib/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/lib/mime-type-parameters.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/lib/mime-type.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/lib/parser.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/lib/serializer.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/lib/sniff.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/lib/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-mimetype/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/LICENSE.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/Function.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/URL-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/URL.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/URLSearchParams-impl.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/URLSearchParams.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/VoidFunction.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/encoding.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/infra.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/percent-encoding.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/url-state-machine.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/urlencoded.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/lib/utils.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/whatwg-url/webidl2js-wrapper.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/why-is-node-running/.github/FUNDING.yml
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/why-is-node-running/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/why-is-node-running/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/why-is-node-running/cli.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/why-is-node-running/example.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/why-is-node-running/include.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/why-is-node-running/index.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/why-is-node-running/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xml-name-validator/LICENSE.txt
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xml-name-validator/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xml-name-validator/lib/xml-name-validator.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xml-name-validator/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/LICENSE
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/README.md
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xml/1.0/ed4.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xml/1.0/ed4.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xml/1.0/ed4.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xml/1.0/ed5.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xml/1.0/ed5.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xml/1.0/ed5.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xml/1.1/ed2.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xml/1.1/ed2.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xml/1.1/ed2.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xmlchars.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xmlchars.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xmlchars.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xmlns/1.0/ed3.d.ts
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xmlns/1.0/ed3.js
[CLEAR]  Modules/Treatment-Plan/frontend/node_modules/xmlchars/xmlns/1.0/ed3.js.map
[CLEAR]  Modules/Treatment-Plan/frontend/package-lock.json
[CLEAR]  Modules/Treatment-Plan/frontend/package.json
[CLEAR]  Modules/Treatment-Plan/frontend/public/insight-logo.png
[CLEAR]  Modules/Treatment-Plan/frontend/src/main.tsx
[CLEAR]  Modules/Treatment-Plan/frontend/src/review-screen.test.tsx
[CLEAR]  Modules/Treatment-Plan/frontend/src/review-workspace.test.ts
[CLEAR]  Modules/Treatment-Plan/frontend/src/review-workspace.ts
[CLEAR]  Modules/Treatment-Plan/frontend/src/styles.css
[CLEAR]  Modules/Treatment-Plan/frontend/tsconfig.json
[MARKED] Modules/Treatment-Plan/governance/ADR-TP-04-DISPOSABLE-LIFECYCLE-PROTOTYPE.md
[MARKED] Modules/Treatment-Plan/governance/TP-01-SCOPE-AND-RELEASE-GATES.md
[MARKED] Modules/Treatment-Plan/governance/TP-10-BN-MAPPING-COVERAGE.md
[MARKED] Modules/Treatment-Plan/governance/clinical-validation/approvals.v1.json
[CLEAR]  Modules/Treatment-Plan/governance/clinical-validation/cases.v1.json
[CLEAR]  Modules/Treatment-Plan/governance/clinical-validation/hazard-log.v1.json
[CLEAR]  Modules/Treatment-Plan/governance/clinical-validation/observations.v1.json
[CLEAR]  Modules/Treatment-Plan/governance/context-ownership.v1.json
[CLEAR]  Modules/Treatment-Plan/governance/scope-matrix.schema.json
[MARKED] Modules/Treatment-Plan/governance/scope-matrix.v1.json
[CLEAR]  Modules/Treatment-Plan/module-config.json
[CLEAR]  Modules/Treatment-Plan/prototype/__pycache__/treatment_plan_lifecycle.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/prototype/run_lifecycle.py
[CLEAR]  Modules/Treatment-Plan/prototype/treatment_plan_lifecycle.py
[CLEAR]  Modules/Treatment-Plan/pyproject.toml
[CLEAR]  Modules/Treatment-Plan/requirements-dev.txt
[CLEAR]  Modules/Treatment-Plan/requirements.lock
[CLEAR]  Modules/Treatment-Plan/requirements.txt
[CLEAR]  Modules/Treatment-Plan/run.ps1
[CLEAR]  Modules/Treatment-Plan/scripts/__pycache__/check_context_ownership.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/scripts/__pycache__/check_identifier_contract.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/scripts/__pycache__/check_tp01_release_gate.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/scripts/__pycache__/check_tp05_contracts.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/scripts/__pycache__/check_tp21_clinical_safety_case.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/scripts/__pycache__/package_release.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/scripts/__pycache__/verify_deployment.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/scripts/check_context_ownership.py
[CLEAR]  Modules/Treatment-Plan/scripts/check_identifier_contract.py
[MARKED] Modules/Treatment-Plan/scripts/check_tp01_release_gate.py
[CLEAR]  Modules/Treatment-Plan/scripts/check_tp05_contracts.py
[MARKED] Modules/Treatment-Plan/scripts/check_tp21_clinical_safety_case.py
[CLEAR]  Modules/Treatment-Plan/scripts/package_release.py
[CLEAR]  Modules/Treatment-Plan/scripts/verify_deployment.py
[CLEAR]  Modules/Treatment-Plan/test.ps1
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_context_ownership.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp01_release_gate.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp03_identifier_contract.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp04_lifecycle_prototype.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp05_contracts.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp06_scaffold.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp07_security.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp08_clinical_context.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp09_eligibility.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp10_bn_evaluation.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp11_safety_policy.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp12_primary_plan.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp13_ddi_check.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp13_ddi_failure.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp13_ddi_hash_binding.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp13_ddi_http.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp13_ddi_pair_coverage.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp13_ddi_response_binding.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp13_ddi_unresolved.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp15_edit_ledger.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp16_finalization.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp17_finalization_versioning.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp18_supersession.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp19_persistence.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp20_observability.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp21_clinical_validation.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp22_deployment.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp23_suicide_risk_resolution.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/__pycache__/test_tp_bn_caller_policy.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/tests/fixtures/bn05_registry_evidence_mapping.json
[CLEAR]  Modules/Treatment-Plan/tests/fixtures/tp10_bn_golden.json
[CLEAR]  Modules/Treatment-Plan/tests/test_context_ownership.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp01_release_gate.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp03_identifier_contract.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp04_lifecycle_prototype.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp05_contracts.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp06_scaffold.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp07_security.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp08_clinical_context.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp09_eligibility.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp10_bn_evaluation.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp11_safety_policy.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp12_primary_plan.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp13_ddi_check.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp13_ddi_failure.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp13_ddi_hash_binding.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp13_ddi_http.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp13_ddi_pair_coverage.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp13_ddi_response_binding.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp13_ddi_unresolved.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp15_edit_ledger.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp16_finalization.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp17_finalization_versioning.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp18_supersession.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp19_persistence.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp20_observability.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp21_clinical_validation.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp22_deployment.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp23_suicide_risk_resolution.py
[CLEAR]  Modules/Treatment-Plan/tests/test_tp_bn_caller_policy.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__init__.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__main__.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/app.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/bn_caller_policy.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/bn_evaluation.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/bn_store.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/clinical_context.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/clinical_validation.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/config.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/ddi_check.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/ddi_http.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/deployment.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/edit_ledger.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/eligibility.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/finalization.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/logging.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/migration.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/observability.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/postgres_repository.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/primary_plan.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/repository.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/retention.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/safety_policy.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/security.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/sqlite_edit_store.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/sqlite_repository.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/suicide_risk_observations.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/__pycache__/supersession.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/app.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/bn_caller_policy.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/bn_evaluation.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/bn_store.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/clinical_context.py
[MARKED] Modules/Treatment-Plan/treatment_plan/clinical_validation.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/config.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/ddi_check.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/ddi_http.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/deployment.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/edit_ledger.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/eligibility.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/finalization.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/logging.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migration.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0001_runtime_records.down.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0001_runtime_records.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0002_plan_edit_ledger.down.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0002_plan_edit_ledger.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0003_finalized_plans.down.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0003_finalized_plans.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0004_immutable_finalized_plans.down.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0004_immutable_finalized_plans.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0005_plan_supersessions.down.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0005_plan_supersessions.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0006_tp19_persistence.down.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/0006_tp19_persistence.sql
[CLEAR]  Modules/Treatment-Plan/treatment_plan/migrations/__init__.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/observability.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/policies/__init__.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/policies/__pycache__/__init__.cpython-312.pyc
[CLEAR]  Modules/Treatment-Plan/treatment_plan/policies/primary-plan-synthesis.schizophrenia-research.v1.json
[CLEAR]  Modules/Treatment-Plan/treatment_plan/policies/safety-policy.schizophrenia-research.v1.json
[CLEAR]  Modules/Treatment-Plan/treatment_plan/postgres_repository.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/primary_plan.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/repository.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/retention.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/safety_policy.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/security.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/sqlite_edit_store.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/sqlite_repository.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/suicide_risk_observations.py
[CLEAR]  Modules/Treatment-Plan/treatment_plan/supersession.py
[MARKED] contracts/README.md
[CLEAR]  contracts/adapters/node/index.mjs
[CLEAR]  contracts/adapters/python/__init__.py
[CLEAR]  contracts/adapters/python/__pycache__/__init__.cpython-312.pyc
[CLEAR]  contracts/adapters/python/__pycache__/fastapi.cpython-312.pyc
[CLEAR]  contracts/adapters/python/__pycache__/filesystem.cpython-312.pyc
[CLEAR]  contracts/adapters/python/__pycache__/memory.cpython-312.pyc
[CLEAR]  contracts/adapters/python/fastapi.py
[CLEAR]  contracts/adapters/python/fastapi_v1.py
[CLEAR]  contracts/adapters/python/filesystem.py
[CLEAR]  contracts/adapters/python/memory.py
[MARKED] contracts/clients/node/common-contracts-client.mjs
[MARKED] contracts/clients/python/common_contracts_client.py
[CLEAR]  contracts/examples/1.0.0/audit-event.json
[CLEAR]  contracts/examples/1.0.0/auth-denial.json
[CLEAR]  contracts/examples/1.0.0/auth-session.json
[CLEAR]  contracts/examples/1.0.0/idempotency-conflict.json
[CLEAR]  contracts/examples/1.0.0/identifiers.json
[CLEAR]  contracts/examples/1.0.0/module-contract.json
[CLEAR]  contracts/examples/1.0.0/pagination.json
[CLEAR]  contracts/examples/1.0.0/provenance.json
[CLEAR]  contracts/examples/1.0.0/request-metadata.json
[CLEAR]  contracts/examples/1.0.0/resource-version.json
[CLEAR]  contracts/examples/1.0.0/stale-etag.json
[CLEAR]  contracts/examples/1.0.0/success.json
[CLEAR]  contracts/examples/1.0.0/unavailable-dependency.json
[CLEAR]  contracts/examples/1.0.0/validation-error.json
[CLEAR]  contracts/examples/manifest.json
[CLEAR]  contracts/openapi/1.0.0/common.openapi.json
[MARKED] contracts/package-policy.json
[CLEAR]  contracts/schemas/1.0.0/audit-event.schema.json
[CLEAR]  contracts/schemas/1.0.0/auth-session.schema.json
[CLEAR]  contracts/schemas/1.0.0/identifiers.schema.json
[CLEAR]  contracts/schemas/1.0.0/module-contract.schema.json
[CLEAR]  contracts/schemas/1.0.0/pagination.schema.json
[CLEAR]  contracts/schemas/1.0.0/problem-details.schema.json
[CLEAR]  contracts/schemas/1.0.0/provenance.schema.json
[CLEAR]  contracts/schemas/1.0.0/request-metadata.schema.json
[CLEAR]  contracts/schemas/1.0.0/resource-version.schema.json
[CLEAR]  contracts/schemas/1.0.0/response-envelope.schema.json
[CLEAR]  deployment/Dockerfile
[CLEAR]  deployment/HOST_RECOVERY.md
[MARKED] deployment/WINDOWS_DOCKER_DESKTOP.md
[CLEAR]  deployment/__pycache__/gateway_readiness.cpython-312.pyc
[CLEAR]  deployment/__pycache__/supervisor.cpython-312.pyc
[CLEAR]  deployment/compose.unified.yaml
[CLEAR]  deployment/gateway_readiness.py
[CLEAR]  deployment/insight-unified-container.service
[CLEAR]  deployment/manifest.json
[CLEAR]  deployment/manifest.schema.json
[CLEAR]  deployment/nginx-vps.conf
[CLEAR]  deployment/nginx.conf
[CLEAR]  deployment/secrets-empty/.gitkeep
[CLEAR]  deployment/supervisor.py
[CLEAR]  deployment/test.ps1
[CLEAR]  deployment/verify.ps1
[CLEAR]  scripts/__pycache__/check_architecture.cpython-312.pyc
[CLEAR]  scripts/__pycache__/check_common_contracts.cpython-312.pyc
[CLEAR]  scripts/__pycache__/check_deployment.cpython-312.pyc
[CLEAR]  scripts/__pycache__/verify_unified_deployment.cpython-312.pyc
[MARKED] scripts/check_architecture.py
[MARKED] scripts/check_common_contracts.py
[MARKED] scripts/check_deployment.py
[CLEAR]  scripts/verify_unified_deployment.py
[CLEAR]  tests/__pycache__/test_architecture.cpython-312.pyc
[CLEAR]  tests/__pycache__/test_common_contracts.cpython-312.pyc
[CLEAR]  tests/__pycache__/test_deployment_contract.cpython-312.pyc
[CLEAR]  tests/__pycache__/test_gateway_readiness.cpython-312.pyc
[CLEAR]  tests/__pycache__/test_tp22_rollback_drill.cpython-312.pyc
[CLEAR]  tests/__pycache__/test_tp22_unified_verification.cpython-312.pyc
[CLEAR]  tests/__pycache__/test_unified_image.cpython-312.pyc
[MARKED] tests/test_architecture.py
[MARKED] tests/test_common_contracts.py
[CLEAR]  tests/test_common_contracts_node.mjs
[MARKED] tests/test_deployment_contract.py
[CLEAR]  tests/test_gateway_readiness.py
[CLEAR]  tests/test_redaction_node.mjs
[CLEAR]  tests/test_tp22_rollback_drill.py
[CLEAR]  tests/test_tp22_unified_verification.py
[CLEAR]  tests/test_unified_image.py
```

## Symbolic Links Checked

```text
[CLEAR symlink] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/python -> /usr/bin/python3
[CLEAR symlink] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/python3 -> python
[CLEAR symlink] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/bin/python3.12 -> python
[CLEAR symlink] Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0/.venv/lib64 -> lib
[CLEAR symlink] Modules/DDI-Checker-1.2.0/node_modules/.bin/prebuild-install -> ../prebuild-install/bin.js
[CLEAR symlink] Modules/DDI-Checker-1.2.0/node_modules/.bin/rc -> ../rc/cli.js
[CLEAR symlink] Modules/DDI-Checker-1.2.0/node_modules/.bin/semver -> ../semver/bin/semver.js
[CLEAR symlink] Modules/DDI-Checker-1.2.0/node_modules/better-sqlite3/build/node_gyp_bins/python3 -> /usr/bin/python3
[CLEAR symlink] Modules/Medical-History-1.0.0/node_modules/.bin/prebuild-install -> ../prebuild-install/bin.js
[CLEAR symlink] Modules/Medical-History-1.0.0/node_modules/.bin/rc -> ../rc/cli.js
[CLEAR symlink] Modules/Medical-History-1.0.0/node_modules/.bin/semver -> ../semver/bin/semver.js
[CLEAR symlink] Modules/Medical-History-1.0.0/node_modules/better-sqlite3/build/node_gyp_bins/python3 -> /usr/bin/python3
[CLEAR symlink] Modules/Treatment-Plan/frontend/node_modules/.bin/lz-string -> ../lz-string/bin/bin.js
[CLEAR symlink] Modules/Treatment-Plan/frontend/node_modules/.bin/nanoid -> ../nanoid/bin/nanoid.cjs
[CLEAR symlink] Modules/Treatment-Plan/frontend/node_modules/.bin/rolldown -> ../rolldown/bin/cli.mjs
[CLEAR symlink] Modules/Treatment-Plan/frontend/node_modules/.bin/specificity -> ../@bramus/specificity/bin/cli.js
[CLEAR symlink] Modules/Treatment-Plan/frontend/node_modules/.bin/tldts -> ../tldts/bin/cli.js
[CLEAR symlink] Modules/Treatment-Plan/frontend/node_modules/.bin/tsc -> ../typescript/bin/tsc
[CLEAR symlink] Modules/Treatment-Plan/frontend/node_modules/.bin/vite -> ../vite/bin/vite.js
[CLEAR symlink] Modules/Treatment-Plan/frontend/node_modules/.bin/vitest -> ../vitest/vitest.mjs
[CLEAR symlink] Modules/Treatment-Plan/frontend/node_modules/.bin/why-is-node-running -> ../why-is-node-running/cli.js
```

## Coverage Notes

- Text files: line scan plus contextual review of handoffs, contracts, architecture checks, and clinical-release gates.
- Binary files: byte-string scan; binary excerpts have no reliable line number.
- Checked-in `node_modules/` and `.venv/` are included. Their warnings govern vendored artifacts, not project source generally.
- `graphify-out/` is excluded everywhere, including nested module copies.
