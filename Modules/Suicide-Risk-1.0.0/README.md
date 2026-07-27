# Suicide Score

Standalone C-SSRS Screen Version - Recent module for Insight.

## Insight deployment

Unified Insight deploys this module at `/modules/suicide-risk` with API prefix
`/api/suicide-risk/v1` on internal port `8111`. Source revision is pinned in
[`UPSTREAM.md`](UPSTREAM.md). Workflow activation is required before a screen
can load; six-character codes remain compatibility context while supplied
patient and encounter UUIDs are retained on the assessment.

`POST /api/suicide-risk/v1/activate` is idempotent for identical context.
`PUT /api/suicide-risk/v1/assessments/{code}` saves one immutable assessment
per activation and returns it on retry. New workflow writes require a completed
screen; this integration does not expose an unassessed bypass. Health and
readiness are available at `/api/suicide-risk/v1/health` and
`/api/suicide-risk/v1/ready`. Production session and CSRF checks use the
canonical Authentication session endpoint.

After durable save, browser activation of Medical History preserves activation
code plus available patient and encounter UUIDs, then redirects to its gateway
route. If activation fails, retrying Save retries only this idempotent
continuation; it does not create another assessment.

## Run

Open `index.html` directly in a browser for upstream demo behavior. Unified
Insight uses its server adapter and isolated `/var/lib/insight/suicide-risk`
volume instead of browser storage.

## Embed

```html
<link rel="stylesheet" href="/suicide-score/styles.css" />
<div id="suicide-score"></div>
<script src="/suicide-score/app.js"></script>
<script>
  SuicideScore.mount(document.getElementById("suicide-score"), {
    apiBase: "https://internal.example",
    patientCode: "PAT-001",
    dashboardUrl: "/dashboard"
  });
</script>
```

## REST interface

`GET /api/suicide-score/patients/{patientCode}`

Expected response:

```json
{
  "patientCode": "PAT-001",
  "displayName": "Optional display name"
}
```

`PUT /api/suicide-score/patients/{patientCode}/screen`

Completed payload:

```json
{
  "status": "completed",
  "score": 4,
  "result": "High risk",
  "riskLevel": "high",
  "answers": {
    "q1": true,
    "q2": true,
    "q3": true,
    "q4": true,
    "q5": false,
    "q6": false,
    "q6Recent": null
  },
  "completedAt": "2026-07-05T00:00:00.000Z"
}
```

Passed payload:

```json
{
  "status": "not_completed",
  "score": null,
  "result": "Not completed",
  "riskLevel": "incomplete",
  "answers": {
    "q1": null,
    "q2": null,
    "q3": null,
    "q4": null,
    "q5": null,
    "q6": null,
    "q6Recent": null
  },
  "completedAt": null
}
```

## Scoring

The score is the highest endorsed C-SSRS screener severity item. Recent suicidal behavior/preparation is represented as score `6`.

- `No current risk endorsed`: no endorsed required items
- `Low risk`: Q1 or Q2 endorsed without method, intent, plan, or behavior
- `Moderate risk`: Q3 endorsed, or lifetime behavior/preparation outside the past three months
- `High risk`: Q4, Q5, or behavior/preparation within the past three months endorsed
