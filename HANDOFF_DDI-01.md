# Handoff — DDI-01 Standalone Node REST Seam (Phase 5)

>Status: **in progress, mid-implementation. NOT committed.** Resume and finish the loop before committing.

## Session intent

Implement Phase 5 / packet **DDI-01** of the INSIGHT roadmap: wrap the existing
deterministic DDI engine in a standalone Node REST server. Per the issue the
*deep module* owns resolution, pair generation, severity, evidence, and results;
HTTP and CLI are adapters. The static UI stays but must call REST.

Skills requested (`\caveman`, `\handoff`, `\codebase-design`, `\ponytail` under
`root/skills/...`) were **not installed** on this machine — only `graphify` is
present at `~/.claude/skills/`. Proceeded without them; flag if they appear later.

## Work-packet loop contract (must follow exactly)

Each packet is a separate commit and follows:
1. `git status --short` in the affected repo, record pre-existing changes.
2. Read only the named module interface, its adapter, and relevant tests.
3. Add/change tests first.
4. Implement only the packet; no opportunistic refactors.
5. Run focused tests, module full suite, common-contract checks.
6. `git diff --check` and `git diff --stat`.
8. Stop on missing clinical decisions / schema conflicts / migration ambiguity
   / external credentials. Never fabricate approvals, identifiers, thresholds,
   or evidence.
9. Commit only after automated acceptance checks pass.
10. Do not begin a dependent packet before its prerequisite passes.

## Step 1 result — pre-existing state

Affected repo is `/root/projects/insight` (single git repo, no nested submodules).
Pre-existing `git status --short` after the graphify rebuild shows ONLY:

- `graphify-out/**` cache churn (AST v0.9.23 → v0.9.24 rebuilds, manifest/labels).
- `Modules/*/graphify-out/**` same.
- `__pycache__/**` and `*.pyc` under `Modules/Diagnosis-1.2.0/`.
- `Modules/Medical-History-1.0.0/node_modules/`.
- `contracts/adapters/python/__pycache__/`, `scripts/__pycache__/`,
  `tests/__pycache__/`.

**No pre-existing source-code changes** (confirmed: filtering the above noise
returns no rows). These are gitignored noise and must NOT be committed.

## Step 2 — modules read (interface, adapter, tests)

Deep module (existing, untouched):
- `Modules/DDI-Checker-1.2.0/src/ddi-engine.js` — UMD, exports
  `buildIndex, resolveDrug, suggestDrugs, checkInteractions, createAuditEntry,
  extractDoseSuggestions, parseReportText, normalizeName, pairKey, hashString,
  isInteractionEligible, SEVERITY_ORDER, DISPLAY_SEVERITY`.
  *This is the deep module. The REST seam is an adapter around it.*

Adapters / support already in the module:
- `src/storage-adapter.js` (browser + memory storage adapters)
- `src/kb-persistence.js` (revision rebase / createRevision)
- `src/auth-adapter.js` (`parseCanonicalSession`, `createMemoryAuthAdapter`,
  `createHttpAuthAdapter` reading `AUTH_SESSION_URL`). This session shape is the
  authoritative auth contract and MUST be reused (do not invent a new one).
- `src/report-parser.js`, `src/styles.css`, `index.html`, `src/app.js`
  (static UI controller).
- `data/active-kb.json` / `data/active-kb.js` (bundled KB).
- `scripts/ingest.mjs`, `scripts/validate-kb.mjs`.
- `package.json` (`"type": "commonjs"`, scripts `test:unit` / `test:kb` /
  `test:ci`). **Note: `.mjs` files are always ESM here; use `.cjs` for Node
  CommonJS server code that `require`s the UMD engine.**

Common contract package (allowed cross-module import per
`scripts/check_architecture.py` `_ALLOWED_COMMON_IMPORTS`):
- `contracts/adapters/node/index.mjs` exports `HttpContractAdapter`,
  `InMemoryContractAdapter`, `createCommonContractHandlers`.
- `contracts/schemas/1.0.0/*.schema.json`, `contracts/openapi/1.0.0/common.openapi.json`.
- Example envelope: `contracts/examples/1.0.0/success.json`.
- Schema required keys: `moduleId, moduleVersion, interfaceVersion, schemaVersion,
  basePath, capabilities, dependencies, auth, compatibilityRoutes,
  supportedClinicalScope` (`contracts/schemas/1.0.0/module-contract.schema.json`).

Existing cross-module consumer contract (MUST NOT break):
- `Modules/Treatment-Plan/treatment_plan/ddi_http.py` POSTs to
  **`{base_url}/api/ddi-checker/v1/interaction-checks`** with headers
  `X-Schema-Version: 1.0.0` and `Idempotency-Key`, body containing
  `idempotencyKey, planSemanticHash, medicationSetHash, medications[]`.
- `Modules/Treatment-Plan/treatment_plan/ddi_check.py` validates the response:
  - `schemaVersion`, `checkId`, `medicationSetHash` echoed,
  - `knowledgeBaseId` nonempty string, `knowledgeBaseVersion` nonempty string,
  - `normalizedMedications[]` each with `inputIndex:int`, and (when not
    unresolved) nonempty `conceptId:string`,
  - `unresolvedMedications[]`,
  - **`pairsChecked[]` covering EVERY normalized medication pair when
    `unresolvedMedications` is empty** (each item has either
    `medicationInputIndexes:[left,right]` or `leftInputIndex/rightInputIndex`).
    Duplicate pairs or missing coverage → `_InvalidDdiResponse("invalid-response")`.
  - `alerts[]` each with `medicationInputIndexes:int[]` (len ≥ 2, in range),
    `severity`, `recommendedAction` (or `recommendation`), `evidence:list` nonempty.
- Tests: `Modules/Treatment-Plan/tests/test_tp13_ddi_http.py`,
  `test_tp13_ddi_hash_binding.py` (`no_interaction_response`),
  `test_tp13_ddi_pair_coverage.py`,
  `test_tp13_ddi_failure.py`, `test_tp13_ddi_unresolved.py`,
  `test_tp13_ddi_response_binding.py`, `test_tp13_ddi_check.py`.

Architecture rules (`scripts/check_architecture.py`):
- Cross-module imports are rejected (`CROSS_MODULE_IMPORT`) EXCEPT
  `contracts.clients` / `contracts.adapters`. New server file may import
  `contracts/adapters/node/index.mjs` and the local engine; nothing else.
- Path-literal regex flags `runtime|state|active-kb*.json`. The bundled
  `data/active-kb.json` is the canonical KB; do not introduce new runtime JSON
  path literals.
- "browser storage cannot own clinical integration state" — production state
  must move server-side. This packet begins that migration; the UI still
  persists to localStorage *for now* (do not change Behavior in this packet
  beyond wiring REST calls — that is the next packet).

Other DDI engine tests read (still green, must stay green):
- `test/ddi-engine.test.mjs`, `test/auth-adapter.test.mjs`,
  `test/storage-adapter.test.mjs`, `test/kb-persistence.test.mjs`,
  `test/ingest.test.mjs`, `test/report-parser-parity.test.mjs`,
  `test/validate-kb.test.mjs`, `test/ui-source.test.mjs`,
  `test/ci-contract.test.mjs`.

## Step 3 — tests written (first)

New file **`Modules/DDI-Checker-1.2.0/test/ddi-rest-seam.test.mjs`** (untracked,
complete, in place). Covers:

- Canonical routes `/health /ready /contract /openapi.json /schemas/{v}/{name}`
  mounted and shaped per `module-contract.schema.json`
  (`moduleId=ddi-checker`, `basePath=/api/ddi-checker/v1`, capabilities include
  `ddi.interaction-check, ddi.medication-resolve, ddi.knowledge-base.read`,
  `auth.required=true`, `auth.schemes.includes("session")`).
- `POST /api/ddi-checker/v1/medications/resolve` → engine.resolveDrug, 200;
  unknown KB version → 404 problem-details.
- `POST /api/ddi-checker/v1/interaction-checks` — full TP-13 contract:
  echoes `medicationSetHash, schemaVersion=1.0.0`, returns
  `knowledgeBaseId, knowledgeBaseVersion=ikb-test`, `normalizedMedications`,
  `pairsChecked`, `alerts` (severity, `medicationInputIndexes=[0,1`]).
  Missing idempotencyKey → 400 `INVALID_REQUEST`.
  Clean (no-interaction) check still returns nonempty `knowledgeBaseId`.
- `GET /api/ddi-checker/v1/knowledge-bases/{version}` returns KB summary
  (schemaVersion, version, status, drugs, interactions with `reviewStatus`);
  unknown version → 404.
- Deprecated alias `/api/ddi/v1/medications/resolve` still works;
  `/contract.compatibilityRoutes` lists `{path:/api/ddi/v1, deprecated:true,
  replacement:/api/ddi-checker/v1}`.
- Protected admin routes
  (`GET /api/ddi-checker/v1/knowledge-bases`,
  `POST .../{version}/review|activate|retire|rollback`) reject unauthenticated
  callers with 401 `UNAUTHENTICATED`; a `psychiatrist` (non-admin) principal
  gets 403 `FORBIDDEN` on `.../{version}/activate`. Admin token allows listing.
- Static UI assets served when `serveStatic` true (test asserts index.html
  contains `data-view="checker"`).

Test helper `memoryStorage()` supplies minimal `knowledgeStore` with
`load(version), list()`; assume `admin(action, version, body)` will be added
by implementation (test does not exercise admin mutators beyond auth gating).
`adminAuth()` only does cookie/`insight_session` parsing; canonical session
shape lives in `src/auth-adapter.js` — the real server should delegate to that
adapter, not re-implement parseCanonicalSession.

## Step 4 — implementation in progress (NOT finished — do not commit yet)

New file **`Modules/DDI-Checker-1.2.0/src/ddi-rest-adapter.cjs`** (untracked,
partially working). **Status: tests run, currently failing with
`ReferenceError: knowledgeBaseShape is not defined` at module export line.**

Root cause in progress of fixing:
- `knowledgeBaseShape(kb)` was defined INSIDE `createDdiServer()` block scope
  but referenced in the module-level `module.exports`. Last edit changed it to
  a local `knowledgeBaseShapeLocal` wrapper calling a `knowledgeBaseShape`
  that no longer exists at outer scope → still broken.
- **Fix to apply next:** define a single `knowledgeBaseShape(kb)` at MODULE
  scope (outside `createDdiServer`), delete the `knowledgeBaseShapeLocal`
  wrapper, and make `handleKnowledgeBase` call the module-scope function
  directly. Also tidy the `recommendation || recommendation` self-reference
  that the hoist edit removed (good).

### Open implementation TODOs (in this file)

1. Hoist `knowledgeBaseShape` to module scope (see above). Then re-run
   `node --test test/ddi-rest-seam.test.mjs` from
   `/root/projects/insight/Modules/DDI-Checker-1.2.0`.
2. Author a thin entrypoint `src/server.mjs` (ESM) that imports the `.cjs`
   adapter via `createRequire`, builds a real `knowledgeStore` backed by
   `data/active-kb.json` (read-only is fine for DDI-01; mutators may return
   501 `ADMIN_NOT_IMPLEMENTED` which the adapter already supports) and wires
   `src/auth-adapter.js#createHttpAuthAdapter` (env `AUTH_SESSION_URL`) /
   `createMemoryAuthAdapter`. Add `package.json` scripts:
   `start: "node src/server.mjs"`. Optional: respect `PORT` env (default 8087).
   Match the `HttpContractAdapter` import from `contracts/adapters/node/index.mjs`
   for schema/openapi disk reads.
3. Verify `/contract` and `/openapi.json` actually serve the COMMON openapi
   fragment merged in (`x-insight-common-openapi`) AND expose DDI-specific
   paths. The current `buildOpenapiDocument()` only contains DDI paths; the
   common fragment is just attached as a vendor extension. The test only
   checks DDI paths exist — that passes — but consider whether the contract
   adapter should actually be the source of `/openapi.json` (mirroring the
   Python `install_common_routes`). Decision pending: for DDI-01 the test's
   expectation is met; revisiting how common OpenAPI is merged is a candidate
   for a later packet, not this one. RESOLVE before commit: keep current
   approach (DDI-owned openapi merges common fragment under a vendor key) and
   note in handoff.
4. Confirm `readContractsArtifact("openapi")` finds the file at the resolved
   `contracts/openapi/1.0.0/common.openapi.json`. The path resolution uses
   `path.resolve(__dirname, "..", "..", "..", "contracts")` — verify that
   resolves to `/root/projects/insight/contracts` from
   `Modules/DDI-Checker-1.2.0/src/`. (`__dirname` in `.cjs` is the `src/`
   dir; three `..` → `/root/projects/insight`. Correct.) Add a defensive
   check; not currently exercised by tests beyond the contract route.
5. Re-run the FULL module test suite:
   `cd Modules/DDI-Checker-1.2.0 && npm test` (runs `node --test test/*.test.mjs`).
   Watch `ui-source.test.mjs` — it scans `index.html`/`app.js` source text for
   invariants (overrideDialog, evidence markup, `sessionStorage.getItem`, etc).
   **Do not rewire index.html/app.js in a way that drops those markers.** The
   UI-rest wiring in this packet must be additive (optional fetch-based path
   alongside existing local engine path) or be deferred to a later packet.
   Current plan: keep app.js calling `window.DDIEngine` for this packet; ship
   a minimal `server.mjs` + adapter now; reserve UI↔REST migration for the
   next packet. The issue text says "Keep the static UI, but make it call
   REST." — if doing that fully here, ensure `ui-source.test.mjs` still passes
   or update that test in the same commit (it is in the same packet by right).
   **Decision needed before commit**: ask which scope is intended — full UI
   rewire (large, touches ui-source tests) or REST seam first + UI rewire next
   packet. Default to REST seam first; the issue lists UI wiring last, so a
   two-packet split is reasonable. NOT a missing clinical decision; this is a
   scope decision — surface it before committing.
6. Run `python3 tests/test_common_contracts.py` and
   `python3 tests/test_architecture.py` from repo root. The new `.cjs`/`.mjs`
   files must not trigger `CROSS_MODULE_IMPORT`. Confirm the only cross-package
   import line is `contracts/adapters/node/index.mjs` (allowed) — verify by
   grepping the new files for `require(`/`import`. Note: the adapter currently
   does NOT import the contracts node adapter yet (it reimplements response
   helpers). **Consider** switching to `createCommonContractHandlers` from
   `contracts/adapters/node/index.mjs` for `/health /ready /contract
   /openapi.json /schemas/*` so canonical envelopes (X-Request-ID,
   X-Correlation-ID, problem+json) match the shared adapter exactly. If done,
   update the test expectations accordingly (the test asserts header presence
   indirectly via body shape; reuse is safe). If keeping the local handlers,
   ensure header behavior matches the shared adapter enough for the test.
7. Run `git diff --check` and `git diff --stat` from repo root before commit.
   The stat should show only:
   - `Modules/DDI-Checker-1.2.0/src/ddi-rest-adapter.cjs` (new)
   - `Modules/DDI-Checker-1.2.0/src/server.mjs` (new, after TODO 2)
   - `Modules/DDI-Checker-1.2.0/test/ddi-rest-seam.test.mjs` (new)
   - `Modules/DDI-Checker-1.2.0/package.json` (new start script, after TODO 2)
   - (optional) a contract example file if added.
   DO NOT stage any `graphify-out/**`, `__pycache__/**`, `*.pyc`, or
   `node_modules/**` files.

## Clinical / schema decisions made (do not fabricate beyond these)

- `moduleId = "ddi-checker"` (taken from `Modules/DDI-Checker-1.2.0/module-config.json`).
- `basePath = "/api/ddi-checker/v1"` — chosen to MATCH the existing TP-13
  consumer contract exactly (`/api/ddi-checker/v1/interaction-checks`).
  The issue text wrote `/api/ddi/v1/...`; treated `ddi/v1` as a deprecated
  alias (`compatibilityRoutes`). Both exposed; canonical is `ddi-checker`.
- `interfaceVersion = schemaVersion = "1.0.0"`.
- Auth scheme: `session` (cookie `insight_session=...`), reusing
  `src/auth-adapter.js` canonical-session shape. Admin role gate uses a
  `ddi_admin` role string — NOT yet validated against the Authentication
  module's real role vocabulary. **Flag this**: confirm `ddi_admin` is an
  accepted role, or stop and request the canonical admin role identifier
  before exposing the admin endpoints in production. For tests, the role
  string is asserted against the test-only `adminAuth()` stub. This is the
  only clinical/identity-approval-adjacent decision; rest is mechanical.
- `knowledgeBaseId` format: `"ddi-checker:{kb.version}"`. Acceptable per
  TP-13 (any nonempty string). Not a fabricated clinical identifier.

## Stop conditions that DID NOT trigger

- No migration ambiguity (no DB migrations in this packet — `knowledgeStore`
  is an injected seam; real persistence is a later packet).
- No external credentials (auth adapter reads `AUTH_SESSION_URL` only if set;
  tests use the memory adapter).
- No fabricated clinical thresholds / evidence / approval identifiers.

## Resume checklist (do these in order)

1. Hoist `knowledgeBaseShape` to module scope in
   `Modules/DDI-Checker-1.2.0/src/ddi-rest-adapter.cjs`; delete the
   `knowledgeBaseShapeLocal` wrapper; ensure `handleKnowledgeBase` calls the
   hoisted function. Re-run
   `cd Modules/DDI-Checker-1.2.0 && node --test test/ddi-rest-seam.test.mjs`
   until green.
2. Decide (ask if unclear): full UI↔REST rewire now, or REST seam + entrypoint
   now and UI rewire as the next packet. Default = REST seam + `server.mjs`
   now; UI rewire next packet.
3. Add `src/server.mjs` (ESM) + `package.json` `start` script wiring the
   real `knowledgeStore` (`data/active-kb.json`) and `auth-adapter.js`.
4. (Optional but recommended) switch the common routes
   (`/health /ready /contract /openapi.json /schemas/*`) to
   `createCommonContractHandlers` from `contracts/adapters/node/index.mjs` so
   the response envelope (X-Request-ID / X-Correlation-ID / problem+json)
   matches the shared adapter exactly. Update test if shape changes.
5. Confirm `ddi_admin` role string with the Authentication module, or scope
   the gate to whatever the canonical admin role identifier is. If unknown,
   keep the gate but add a TODO and do not document the endpoint as production
   ready — the packet's admin routes remain "protected" (gated) regardless.
6. Run `cd Modules/DDI-Checker-1.2.0 && npm test` (full module suite).
7. From repo root: `python3 tests/test_common_contracts.py` and
   `python3 tests/test_architecture.py`.
8. `git diff --check` and `git diff --stat` — confirm ONLY the four intended
   files (`src/ddi-rest-adapter.cjs`, `src/server.mjs`,
   `test/ddi-rest-seam.test.mjs`, `package.json`).
9. Commit as a single packet, message in repo style, e.g.:
   `DDI-01: wrap deterministic engine in standalone Node REST seam`
   (match `git log --oneline` prefix convention — recent commits use
   `MH-0N:`, `SEV-0N:`, `DX-0N:`, `DASH-0N:`; use `DDI-01:`).
10. Do NOT stage graphify-out / __pycache__ / *.pyc / node_modules noise.

## Files touched this session (untracked, uncommitted)

- `Modules/DDI-Checker-1.2.0/src/ddi-rest-adapter.cjs` (new, partially working)
- `Modules/DDI-Checker-1.2.0/test/ddi-rest-seam.test.mjs` (new, complete)

## Files to add before commit (still TODO)

- `Modules/DDI-Checker-1.2.0/src/server.mjs` (new, ESM entrypoint)
- `Modules/DDI-Checker-1.2.0/package.json` (edit: add `start` script)

## Commands to resume

```bash
cd /root/projects/insight/Modules/DDI-Checker-1.2.0
node --test test/ddi-rest-seam.test.mjs      # focused (currently failing)
npm test                                     # full module suite
cd /root/projects/insight
python3 tests/test_common_contracts.py
python3 tests/test_architecture.py
git status --short | grep -vE 'graphify-out|__pycache__|node_modules|\.pyc$'
git diff --check
git diff --stat
```

## Graphify context (already analyzed, no need to rebuild)

`graphify-out/graph.json` already exists for `/root/projects/insight`
(4621 nodes / 9229 edges / 265 communities). Relevant communities already
located via `graphify query "DDI checker module architecture server routes"`:
`DdiMedicationChecker`, `treatment_plan/app.py`, `finalization.py`,
`test_routes.py`, `DDI-Checker 1.1.0 — Architecture & Data Flow`. Architecture
doc `Modules/DDI-Checker-1.2.0/graphs/architecture.md` documents the three
existing entry points (CLI ingest, CLI validate, browser app) and explicitly
flags browser localStorage owning state as a "production-side migration target" —
this packet is the start of that migration.
