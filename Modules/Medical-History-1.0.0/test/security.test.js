const test = require("node:test");
const assert = require("node:assert/strict");
const { createServer } = require("../server.js");
const { createMemoryMedicalHistoryRepository } = require("../repository.js");
const { createMemoryAuthAdapter, parseCanonicalSession } = require("../auth-adapter.js");
const { applyRetentionPolicy, RetentionApprovalRequired } = require("../retention.js");
const { corsOrigins } = require("../server.js");

function listen(server) {
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      resolve(`http://127.0.0.1:${port}`);
    });
  });
}

function close(server) {
  return new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}

const sessions = new Map([
  ["psy", parseCanonicalSession({
    schemaVersion: "1.0.0",
    authenticated: true,
    user: { id: "u-psy", roles: ["psychiatrist"] },
    session: { id: "s-psy", expiresAt: "2099-01-01T00:00:00Z" },
    gates: { disclaimerAccepted: true, passwordChangeRequired: false },
  })],
  ["nurse", parseCanonicalSession({
    schemaVersion: "1.0.0",
    authenticated: true,
    user: { id: "u-nurse", roles: ["nurse"] },
    session: { id: "s-nurse", expiresAt: "2099-01-01T00:00:00Z" },
    gates: { disclaimerAccepted: true, passwordChangeRequired: false },
  })],
]);

test("configured canonical auth enforces roles and signed double-submit CSRF", async () => {
  const repository = createMemoryMedicalHistoryRepository();
  const server = createServer({
    repository,
    authAdapter: createMemoryAuthAdapter(sessions),
    csrfSecret: "test-csrf-secret",
  });
  const baseUrl = await listen(server);
  try {
    const unauthenticated = await fetch(`${baseUrl}/api/internal/medical-history/submissions/missing`);
    assert.equal(unauthenticated.status, 401);

    const wrongRole = await fetch(`${baseUrl}/api/internal/medical-history/submissions/missing`, {
      headers: { cookie: "insight_session=nurse" },
    });
    assert.equal(wrongRole.status, 403);

    const ready = await fetch(`${baseUrl}/ready`);
    assert.equal(ready.status, 200);
    assert.deepEqual((await ready.json()).checks, {
      database: "ok",
      authentication: "ok",
      csrf: "ok",
    });

    const tokenResponse = await fetch(`${baseUrl}/api/internal/medical-history/csrf`, {
      headers: { cookie: "insight_session=psy" },
    });
    assert.equal(tokenResponse.status, 200);
    const token = (await tokenResponse.json()).token;
    const csrfCookie = tokenResponse.headers.get("set-cookie").split(";", 1)[0];

    const created = await fetch(`${baseUrl}/api/internal/medical-history/submissions`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        cookie: `insight_session=psy; ${csrfCookie}`,
        "x-csrf-token": token,
      },
      body: JSON.stringify({
        patientId: "11111111-1111-4111-8111-111111111111",
        encounterId: "22222222-2222-4222-8222-222222222222",
        author: "clinician-1",
        pastMedicalHistory: [],
        drugs: [],
        priorAntipsychoticTherapy: false,
        clozapineContraindication: false,
        clozapineContraindications: [],
        recurrentNonAdherenceDeterioration: false,
      }),
    });
    assert.equal(created.status, 201);
    const body = await created.json();
    assert.equal(repository.listAudits({ submissionId: body.submissionId }).length, 1);

    const missingCsrf = await fetch(`${baseUrl}/api/internal/medical-history/submissions`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        cookie: "insight_session=psy",
      },
      body: JSON.stringify({
        patientId: "11111111-1111-4111-8111-111111111111",
        encounterId: "22222222-2222-4222-8222-222222222222",
        author: "clinician-1",
        pastMedicalHistory: [],
        drugs: [],
        priorAntipsychoticTherapy: false,
        clozapineContraindication: false,
        clozapineContraindications: [],
        recurrentNonAdherenceDeterioration: false,
      }),
    });
    assert.equal(missingCsrf.status, 403);
  } finally {
    await close(server);
  }
});

test("retention redacts expired PHI while preserving audit records", async () => {
  const repository = createMemoryMedicalHistoryRepository();
  await repository.appendSubmission({
    id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    submissionId: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    patientId: "11111111-1111-4111-8111-111111111111",
    encounterId: "22222222-2222-4222-8222-222222222222",
    author: "clinician-1",
    createdAt: "2020-01-01T00:00:00.000Z",
    updatedAt: "2020-01-01T00:00:00.000Z",
    submittedAt: "2020-01-01T00:00:00.000Z",
    status: "submitted",
    version: 1,
    etag: '"old"',
    data: { pastMedicalHistory: ["Hypertension"] },
    pastMedicalHistory: ["Hypertension"],
  });
  repository.appendAudit({
    action: "submission.create",
    actor: "clinician-1",
    patientId: "11111111-1111-4111-8111-111111111111",
    submissionId: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    detail: { mode: "canonical" },
    createdAt: "2020-01-01T00:00:00.000Z",
  });

  assert.throws(
    () => applyRetentionPolicy(repository, {
      policy: { policyId: "p1", approverRoles: ["privacy_officer"], approvedAt: "2026-07-01T00:00:00.000Z" },
      retentionDays: 30,
      now: new Date("2026-07-23T00:00:00.000Z"),
    }),
    RetentionApprovalRequired,
  );

  const result = applyRetentionPolicy(repository, {
    policy: {
      policyId: "mh-retention-1",
      approverRoles: ["privacy_officer", "clinical_safety_officer"],
      approvedAt: "2026-07-01T00:00:00.000Z",
    },
    retentionDays: 30,
    now: new Date("2026-07-23T00:00:00.000Z"),
  });
  assert.equal(result.submissionsRedacted, 1);
  assert.equal(result.auditsPreserved, 1);
  const redacted = repository.findSubmissionById("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
  assert.equal(redacted.data, null);
  assert.equal(redacted.author, "[redacted]");
  assert.ok(redacted.phiRedactedAt);
  assert.equal(repository.listAudits().length, 2);
});

test("production CORS rejects wildcard default", () => {
  const previousNodeEnv = process.env.NODE_ENV;
  const previousOrigins = process.env.MEDICAL_HISTORY_CORS_ORIGINS;
  try {
    process.env.NODE_ENV = "production";
    delete process.env.MEDICAL_HISTORY_CORS_ORIGINS;
    assert.deepEqual(corsOrigins(), []);
    process.env.MEDICAL_HISTORY_CORS_ORIGINS = "https://insight.local";
    assert.deepEqual(corsOrigins(), ["https://insight.local"]);
  } finally {
    if (previousNodeEnv === undefined) delete process.env.NODE_ENV;
    else process.env.NODE_ENV = previousNodeEnv;
    if (previousOrigins === undefined) delete process.env.MEDICAL_HISTORY_CORS_ORIGINS;
    else process.env.MEDICAL_HISTORY_CORS_ORIGINS = previousOrigins;
  }
});
