# Medical History Module

Standalone Node.js module that collects a patient's medical history as immutable, versioned submissions keyed by patient and encounter UUIDs. Six-character activation codes remain compatibility adapters for existing callers.

## Run and test

```powershell
npm start
npm test
```

Open `http://localhost:4173`, activate with a six-character alphanumeric code, complete the form, and submit. Node.js 18 or newer is required.

## Collected information

- Patient drug list: zero to 20 entries; each drug keeps original text, RxNorm resolution (explicitly unresolved until coded), dose amount/unit, route, and frequency.
- Past medical history: multi-select list of relevant diseases, each stored with original text and coding (approved when provided, otherwise unresolved).
- Substantial suicide risk: Yes/No, default No.
- Prior antipsychotic therapy: Yes/No, default No. When Yes, therapy success and an antipsychotic selection are required.
- Contraindication to clozapine: Yes/No, default No. When Yes, one or more of Severe neutropenia, Clozapine-induced myocarditis, or Unmanaged seizure disorder is required.
- Recurrent non-adherence-related deterioration: Yes/No, default No.

Conditional questions are hidden until applicable. The server independently validates all rules, including the 20-drug maximum and controlled option lists.

## Correlation and persistence

A deep submission requires `patientId`, `encounterId`, and `author`; each resource includes UUID identity, schema version, timestamps, status, and a quoted ETag. Submissions are append-only in SQLite (`data/medical_history.sqlite` by default). Six-character activation routes normalize the code and adapt legacy callers to the same store:

```http
GET /api/internal/medical-history/submissions?code=A1B2C3
```

Deep resources support latest and immutable history lookup:

```http
GET /api/internal/medical-history/submissions/latest?patientId={uuid}&encounterId={uuid}
GET /api/internal/medical-history/submissions/history?patientId={uuid}&encounterId={uuid}
```

Legacy JSON files (`activation_sessions.json`, `medical_history_submissions.json`) migrate into SQLite on startup. Set `MEDICAL_HISTORY_DATA_DIR` for an isolated data directory. Optional auth is enabled with `AUTH_SESSION_URL`; readiness is `GET /ready`. Production must set `MEDICAL_HISTORY_CORS_ORIGINS` (wildcard CORS is disabled when `NODE_ENV=production`).

## Internal REST API

- `GET /api/internal/medical-history/health`
- `POST /api/internal/medical-history/activate`
- `GET /api/internal/medical-history/activation/{code}`
- `GET /api/internal/medical-history/options`
- `POST /api/internal/medical-history/submissions`
- `GET /api/internal/medical-history/submissions[?code=...]`
- `GET /api/internal/medical-history/submissions/latest?patientId={uuid}&encounterId={uuid}`
- `GET /api/internal/medical-history/submissions/history?patientId={uuid}&encounterId={uuid}`
- `GET /api/internal/medical-history/submissions/{id}`
- `GET /api/internal/medical-history/schema`

Example submission:

```json
{
  "code": "A1B2C3",
  "pastMedicalHistory": ["Hypertension"],
  "drugs": [{ "name": "Lithium", "dose": "300 mg", "route": "Oral", "frequency": "Daily" }],
  "substantialSuicideRisk": false,
  "priorAntipsychoticTherapy": true,
  "priorAntipsychoticTherapySuccessful": false,
  "antipsychotic": "Risperidone",
  "clozapineContraindication": true,
  "clozapineContraindications": ["Severe neutropenia"],
  "recurrentNonAdherenceDeterioration": false
}
```

The canonical dataset contract is `data/medical_history_schema.json`.

## Production note

SQLite persistence, optional canonical auth/CSRF, audit events, readiness, concurrency-safe transactional writes, and approval-gated retention are in place. Production still needs encrypted volumes, operator-approved retention windows (`MEDICAL_HISTORY_PHI_RETENTION_DAYS` plus dual privacy/clinical-safety approval), and restricted CORS origins.
