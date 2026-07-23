# Medical History Handoff

## Architecture

This is a dependency-free standalone Node.js module. `medical-history-submission.js` owns versioned submission identity, append-only JSON persistence, ETags, and latest/history lookup. `server.js` owns activation compatibility, validation, HTTP adaptation, and static serving. `public/index.html`, `public/app.js`, and `public/styles.css` implement the browser flow. `data/medical_history_schema.json` is the integration contract. `test/server.test.js` runs the real HTTP server against a temporary data directory.

The canonical submission boundary is `/api/internal/medical-history/submissions` with patient and encounter UUIDs. Use `/submissions/latest` and `/submissions/history` for identity-based lookup. The six-character `/activate`, `/activation/{code}`, and `?code=` routes are compatibility adapters only; codes are normalized to uppercase and stored as optional legacy metadata.

## Submission model (v2)

- `pastMedicalHistory: string[]` — values must come from the options endpoint.
- `drugs: Drug[]` — at most 20; each included row requires `name`; dose, route, and frequency are optional.
- `substantialSuicideRisk: boolean` — UI default false.
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

Default runtime data is stored in `data/activation_sessions.json` and `data/medical_history_submissions.json`. Submission records are immutable history entries; `MEDICAL_HISTORY_DATA_DIR` overrides the runtime directory so tests can run without touching real module data.

Verification:

```powershell
node --check server.js
node --check public/app.js
npm test
```

The integration tests cover option lists, a fully populated conditional submission, all-default No answers, code normalization/retrieval, the 20-drug maximum, and invalid conditional combinations.

## Change guidance

When changing a collected field, keep these synchronized:

1. `medical-history-submission.js` resource and persistence interface.
2. `public/index.html` markup and defaults.
3. `public/app.js` conditional behavior and payload mapping.
4. `server.js` controlled options, validation, and adapter mapping.
5. `data/medical_history_schema.json`.
6. `test/server.test.js`.
7. `README.md` and this handoff.
8. `graphify-out` via `graphify --update`.

Do not rename the internal REST routes without coordinating every parent-module integration. Runtime JSON storage is suitable only for a prototype; production PHI requires hardened identity, access control, persistence, encryption, audit, and retention controls.
