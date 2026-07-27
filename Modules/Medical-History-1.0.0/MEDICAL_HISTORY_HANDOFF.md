# Medical History Handoff

## Architecture

This is a dependency-free standalone Node.js module. `medical-history-submission.js` owns versioned submission identity, append-only JSON persistence, ETags, and latest/history lookup. `server.js` owns activation compatibility, validation, HTTP adaptation, and static serving. `public/index.html`, `public/app.js`, and `public/styles.css` implement the browser flow. `data/medical_history_schema.json` is the integration contract. `test/server.test.js` runs the real HTTP server against a temporary data directory.

The canonical submission boundary is `/api/internal/medical-history/submissions` with patient and encounter UUIDs. Use `/submissions/latest` and `/submissions/history` for identity-based lookup. The six-character `/activate`, `/activation/{code}`, and `?code=` routes are compatibility adapters only; codes are normalized to uppercase and stored as optional legacy metadata.

## Submission model (v2)

- `pastMedicalHistory: Condition[]` — each entry has `originalText` plus `coding` (`system`, `code`, `display`, `resolutionStatus`). Legacy string values are accepted and normalized. Unresolved coding stays explicit (`system`/`code` null, `resolutionStatus: "unresolved"`). Approved coding is preserved only when system, code, and display are all present.
- `drugs: Drug[]` — at most 20; each entry has `originalText` (legacy `name` accepted), `rxNorm` coding, `doseAmount`/`doseUnit` (null when unknown), optional free-text `dose`, plus `route` and `frequency`.
- `priorAntipsychoticTherapy: boolean` — UI default false.
- `priorAntipsychoticTherapySuccessful: boolean | null` — required and boolean only when prior therapy is true.
- `antipsychotic: string | null` — controlled selection required only when prior therapy is true.
- `clozapineContraindication: boolean` — UI default false.
- `clozapineContraindications: string[]` — empty when false; at least one controlled option when true.
- `recurrentNonAdherenceDeterioration: boolean` — UI default false.

Exact clozapine contraindications:

1. Severe neutropenia
2. Clozapine-induced myocarditis
3. Unmanaged seizure disorder

`GET /api/internal/medical-history/options` returns disease, antipsychotic, and contraindication lists. Server validation is authoritative; do not rely only on conditional UI visibility.

## Conditional UI behavior

All four primary Yes/No questions default to No. Prior therapy = Yes reveals therapy success and antipsychotic selection. Clozapine contraindication = Yes reveals the checkbox list. Switching contraindication back to No clears checked contraindications. The Add drug control disables at 20 and re-enables after removal.

## Persistence and testing

Default runtime uses SQLite (`medical_history.sqlite`) via `better-sqlite3`, with an in-memory adapter for tests. Legacy `activation_sessions.json` and `medical_history_submissions.json` are migrated transactionally on boot. Submission records stay append-only. `MEDICAL_HISTORY_DATA_DIR` overrides the runtime directory so tests can run without touching real module data. `MEDICAL_HISTORY_STORE=memory` forces the memory adapter.

When `AUTH_SESSION_URL` is set, write routes require canonical session roles plus signed double-submit CSRF (`GET /api/internal/medical-history/csrf`). Readiness is at `/ready`. Production defaults drop wildcard CORS; set `MEDICAL_HISTORY_CORS_ORIGINS`. PHI retention is approval-gated (`privacy_officer` + `clinical_safety_officer`) via `applyRetentionPolicy` and `MEDICAL_HISTORY_PHI_RETENTION_DAYS`.

Verification:

```powershell
npm install
node --check server.js
node --check public/app.js
npm test
```

The integration tests cover option lists, repository adapters, migration, concurrency-safe legacy submits, auth/CSRF/readiness, retention redaction with audit preservation, production CORS, conditional submissions, code normalization, the 20-drug maximum, and invalid combinations.

## Change guidance

When changing a collected field, keep these synchronized:

1. `medical-history-submission.js` resource and coding helpers.
2. `repository.js` persistence adapters and JSON migration.
3. `security.js` / `readiness.js` / `retention.js` PHI controls.
4. `public/index.html` markup and defaults.
5. `public/app.js` conditional behavior and payload mapping.
6. `server.js` controlled options, validation, and adapter mapping.
7. `data/medical_history_schema.json`.
8. `test/*.test.js`.
9. `README.md` and this handoff.
10. `graphify-out` via `graphify --update`.

Do not rename the internal REST routes without coordinating every parent-module integration.
