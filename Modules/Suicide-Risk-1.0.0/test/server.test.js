const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { createServer, createMemoryRepository } = require("../server.js");

let base;
let server;

async function request(path, options = {}) {
  const response = await fetch(base + path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  return {
    status: response.status,
    headers: response.headers,
    body: await response.json(),
  };
}

test.before(async () => {
  server = createServer({ repository: createMemoryRepository() });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  base = `http://127.0.0.1:${server.address().port}`;
});

test.after(async () => {
  await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
});

test("health and readiness report independently deployed service", async () => {
  const [health, ready] = await Promise.all([
    request("/api/suicide-risk/v1/health"),
    request("/api/suicide-risk/v1/ready"),
  ]);
  assert.deepEqual(health.body, { ok: true, module: "suicide-risk" });
  assert.equal(ready.status, 200);
  assert.equal(ready.body.ok, true);
});

test("browser uses workflow activation API and does not offer an unassessed bypass", () => {
  const html = fs.readFileSync(path.resolve(__dirname, "../index.html"), "utf8");
  const app = fs.readFileSync(path.resolve(__dirname, "../app.js"), "utf8");
  assert.match(html, /\/api\/suicide-risk\/v1\/activation/);
  assert.match(html, /\/api\/internal\/medical-history\/activate/);
  assert.match(html, /The suicide-risk assessment was saved, but Medical History could not be opened/);
  assert.match(html, /window\.location\.assign\(`\/modules\/medical-history\?code=/);
  assert.match(html, /credentials: "same-origin"/);
  assert.doesNotMatch(app, /data-pass/);
});

test("activation requires valid legacy context and is idempotent", async () => {
  const invalid = await request("/api/suicide-risk/v1/activate", {
    method: "POST",
    body: JSON.stringify({ code: "bad" }),
  });
  assert.equal(invalid.status, 422);

  const payload = {
    code: "SR1234",
    patientId: "11111111-1111-4111-8111-111111111111",
    encounterId: "22222222-2222-4222-8222-222222222222",
    requestedByModule: "severity",
  };
  const first = await request("/api/suicide-risk/v1/activate", { method: "POST", body: JSON.stringify(payload) });
  const second = await request("/api/suicide-risk/v1/activate", { method: "POST", body: JSON.stringify(payload) });
  assert.equal(first.status, 201);
  assert.equal(second.status, 200);
  assert.equal(second.body.activationId, first.body.activationId);
  assert.deepEqual(second.body.context, {
    patientId: payload.patientId,
    encounterId: payload.encounterId,
    requestedByModule: "severity",
    returnUrl: null,
  });

  const conflict = await request("/api/suicide-risk/v1/activate", {
    method: "POST",
    body: JSON.stringify({ ...payload, patientId: "33333333-3333-4333-8333-333333333333" }),
  });
  assert.equal(conflict.status, 409);
});

test("save retains activation identity and retries return original assessment", async () => {
  await request("/api/suicide-risk/v1/activate", {
    method: "POST",
    body: JSON.stringify({ code: "SAVE01", requestedByModule: "severity" }),
  });
  const payload = {
    status: "completed",
    score: 1,
    result: "Low risk",
    riskLevel: "low",
    answers: { q1: true, q2: false, q3: null, q4: null, q5: null, q6: false, q6Recent: null },
    completedAt: "2026-07-27T00:00:00.000Z",
  };
  const first = await request("/api/suicide-risk/v1/assessments/SAVE01", { method: "PUT", body: JSON.stringify(payload) });
  const retry = await request("/api/suicide-risk/v1/assessments/SAVE01", { method: "PUT", body: JSON.stringify(payload) });
  const fetched = await request("/api/suicide-risk/v1/assessments/SAVE01");
  assert.equal(first.status, 201);
  assert.equal(retry.status, 200);
  assert.equal(retry.body.assessmentId, first.body.assessmentId);
  assert.equal(fetched.body.assessmentId, first.body.assessmentId);
  assert.equal(fetched.body.patientId, null);
  assert.equal(fetched.body.encounterId, null);
});

test("new workflow writes reject an unassessed bypass result", async () => {
  await request("/api/suicide-risk/v1/activate", {
    method: "POST",
    body: JSON.stringify({ code: "NOPASS" }),
  });
  const result = await request("/api/suicide-risk/v1/assessments/NOPASS", {
    method: "PUT",
    body: JSON.stringify({ status: "not_completed" }),
  });
  assert.equal(result.status, 422);
});

test("authenticated state changes require a matching CSRF token", async () => {
  const secured = createServer({
    repository: createMemoryRepository(),
    authAdapter: { verify: async () => ({ userId: "clinician", roles: ["psychiatrist"] }) },
    csrfSecret: "test-secret",
  });
  await new Promise((resolve) => secured.listen(0, "127.0.0.1", resolve));
  const securedBase = `http://127.0.0.1:${secured.address().port}`;
  try {
    const csrfResponse = await fetch(securedBase + "/api/suicide-risk/v1/csrf");
    const csrf = await csrfResponse.json();
    const cookie = csrfResponse.headers.get("set-cookie");
    const rejected = await fetch(securedBase + "/api/suicide-risk/v1/activate", {
      method: "POST",
      headers: { "Content-Type": "application/json", cookie },
      body: JSON.stringify({ code: "CSRF01" }),
    });
    assert.equal(rejected.status, 403);
    const accepted = await fetch(securedBase + "/api/suicide-risk/v1/activate", {
      method: "POST",
      headers: { "Content-Type": "application/json", cookie, "X-CSRF-Token": csrf.token },
      body: JSON.stringify({ code: "CSRF01" }),
    });
    assert.equal(accepted.status, 201);
  } finally {
    await new Promise((resolve, reject) => secured.close((error) => error ? reject(error) : resolve()));
  }
});
