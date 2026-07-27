const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const { createServer } = require("../server.js");
const { createMemoryMedicalHistoryRepository } = require("../repository.js");

let base;
let server;

async function request(url, options) {
  const response = await fetch(base + url, { headers: { "Content-Type": "application/json" }, ...options });
  return { status: response.status, etag: response.headers.get("etag"), body: await response.json() };
}

test.before(async () => {
  server = createServer({ repository: createMemoryMedicalHistoryRepository() });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  base = `http://127.0.0.1:${server.address().port}`;
});

test.after(async () => {
  await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
});

test("options expose diseases, antipsychotics, and exact clozapine contraindications", async () => {
  const result = await request("/api/internal/medical-history/options");
  assert.equal(result.status, 200);
  assert.ok(result.body.pastMedicalHistory.includes("Hypertension"));
  assert.ok(result.body.antipsychotics.includes("Clozapine"));
  assert.deepEqual(result.body.clozapineContraindications, ["Severe neutropenia", "Clozapine-induced myocarditis", "Unmanaged seizure disorder"]);
});

test("activation launches through the gateway Medical History route", async () => {
  const patientId = "11111111-1111-4111-8111-111111111111";
  const encounterId = "22222222-2222-4222-8222-222222222222";
  const activation = await request("/api/internal/medical-history/activate", {
    method: "POST",
    body: JSON.stringify({ code: "e98pq5", patientId, encounterId, requestedByModule: "suicide-risk" }),
  });
  assert.equal(activation.status, 201);
  assert.equal(activation.body.code, "E98PQ5");
    assert.equal(activation.body.launchUrl, "/modules/medical-history?code=E98PQ5");
  assert.deepEqual(activation.body.context, { patientId, encounterId, requestedByModule: "suicide-risk", returnUrl: null });
});

test("Medical History browser client keeps module base path and sends CSRF tokens", async () => {
  const [html, client] = await Promise.all([
    fs.readFile(path.resolve(__dirname, "../public/index.html"), "utf8"),
    fs.readFile(path.resolve(__dirname, "../public/app.js"), "utf8"),
  ]);
  assert.match(html, /href="\/modules\/medical-history\/styles\.css"/);
  assert.match(html, /src="\/modules\/medical-history\/app\.js"/);
  assert.match(client, /"\/api\/internal\/medical-history\/csrf"/);
  assert.match(client, /"X-CSRF-Token"/);
  assert.match(client, /`\/modules\/medical-history\?code=\$\{encodeURIComponent\(activation\.code\)\}`/);
  assert.match(client, /window\.location\.assign\("\/modules\/medical-history"\)/);
  assert.doesNotMatch(client, /`\/\?code=\$\{encodeURIComponent\(activation\.code\)\}`/);
  assert.doesNotMatch(client, /window\.location\.assign\("\/"\)/);
});

test("publishes deep submission identity while documenting code as compatibility metadata", async () => {
  const result = await request("/api/internal/medical-history/schema");
  assert.equal(result.status, 200);
  assert.equal(result.body.storage.immutableHistory, true);
  assert.deepEqual(result.body.storage.correlationKey, ["patientId", "encounterId"]);
  assert.equal(result.body.submission.schemaVersion.const, "1.0.0");
  assert.equal(result.body.submission.patientId.type, "uuid");
  assert.equal(result.body.submission.encounterId.type, "uuid");
  assert.equal(result.body.submission.code.compatibilityAdapter, true);
});

test("saves complete conditional history correlated with normalized code", async () => {
  await request("/api/internal/medical-history/activate", { method: "POST", body: JSON.stringify({ code: "ab12cd" }) });
  const payload = { code: "ab12cd", pastMedicalHistory: ["Hypertension", "Asthma"], drugs: [{ name: "Lithium", dose: "300 mg", route: "Oral", frequency: "Daily" }], substantialSuicideRisk: true, priorAntipsychoticTherapy: true, priorAntipsychoticTherapySuccessful: false, antipsychotic: "Risperidone", clozapineContraindication: true, clozapineContraindications: ["Severe neutropenia"], recurrentNonAdherenceDeterioration: true };
  const saved = await request("/api/internal/medical-history/submissions", { method: "POST", body: JSON.stringify(payload) });
  assert.equal(saved.status, 201);
  assert.equal(saved.body.code, "AB12CD");
  assert.deepEqual(saved.body.pastMedicalHistory, [
    { originalText: "Hypertension", coding: { system: null, code: null, display: "Hypertension", resolutionStatus: "unresolved" } },
    { originalText: "Asthma", coding: { system: null, code: null, display: "Asthma", resolutionStatus: "unresolved" } },
  ]);
  assert.deepEqual(saved.body.drugs, [{
    originalText: "Lithium",
    rxNorm: { system: null, code: null, display: "Lithium", resolutionStatus: "unresolved" },
    doseAmount: null,
    doseUnit: null,
    dose: "300 mg",
    route: "Oral",
    frequency: "Daily",
  }]);
  assert.equal(saved.body.antipsychotic, "Risperidone");
  const lookup = await request("/api/internal/medical-history/submissions?code=ab12cd");
  assert.equal(lookup.body.length, 1);
  assert.equal(lookup.body[0].submissionId, saved.body.submissionId);
});

test("preserves approved medication and condition coding when provided", async () => {
  const patientId = crypto.randomUUID();
  const encounterId = crypto.randomUUID();
  const payload = {
    patientId,
    encounterId,
    author: "clinician-1",
    pastMedicalHistory: [{
      originalText: "Asthma",
      coding: {
        system: "http://snomed.info/sct",
        code: "195967001",
        display: "Asthma",
        resolutionStatus: "approved",
      },
    }],
    drugs: [{
      originalText: "Sertraline",
      rxNorm: {
        system: "http://www.nlm.nih.gov/research/umls/rxnorm",
        code: "36437",
        display: "sertraline",
        resolutionStatus: "approved",
      },
      doseAmount: 50,
      doseUnit: "mg",
      route: "Oral",
      frequency: "Daily",
    }],
    substantialSuicideRisk: false,
    priorAntipsychoticTherapy: false,
    clozapineContraindication: false,
    clozapineContraindications: [],
    recurrentNonAdherenceDeterioration: false,
  };
  const saved = await request("/api/internal/medical-history/submissions", { method: "POST", body: JSON.stringify(payload) });
  assert.equal(saved.status, 201);
  assert.deepEqual(saved.body.pastMedicalHistory[0].coding, payload.pastMedicalHistory[0].coding);
  assert.equal(saved.body.pastMedicalHistory[0].originalText, "Asthma");
  assert.deepEqual(saved.body.drugs[0].rxNorm, payload.drugs[0].rxNorm);
  assert.equal(saved.body.drugs[0].doseAmount, 50);
  assert.equal(saved.body.drugs[0].doseUnit, "mg");
  assert.equal(saved.body.drugs[0].originalText, "Sertraline");
});

test("defaults-compatible no answers persist null conditional therapy data", async () => {
  await request("/api/internal/medical-history/activate", { method: "POST", body: JSON.stringify({ code: "NO1234" }) });
  const payload = { code: "NO1234", pastMedicalHistory: [], drugs: [], substantialSuicideRisk: false, priorAntipsychoticTherapy: false, priorAntipsychoticTherapySuccessful: null, antipsychotic: null, clozapineContraindication: false, clozapineContraindications: [], recurrentNonAdherenceDeterioration: false };
  const saved = await request("/api/internal/medical-history/submissions", { method: "POST", body: JSON.stringify(payload) });
  assert.equal(saved.status, 201);
  assert.equal(saved.body.priorAntipsychoticTherapySuccessful, null);
  assert.equal(saved.body.antipsychotic, null);
});

test("rejects over 20 drugs and invalid conditional answers", async () => {
  await request("/api/internal/medical-history/activate", { method: "POST", body: JSON.stringify({ code: "BAD123" }) });
  const basePayload = { code: "BAD123", pastMedicalHistory: [], drugs: Array.from({ length: 21 }, (_, i) => ({ name: `Drug ${i}` })), substantialSuicideRisk: false, priorAntipsychoticTherapy: true, clozapineContraindication: true, clozapineContraindications: [], recurrentNonAdherenceDeterioration: false };
  const result = await request("/api/internal/medical-history/submissions", { method: "POST", body: JSON.stringify(basePayload) });
  assert.equal(result.status, 422);
  assert.ok(result.body.error.details.some((error) => error.includes("more than 20")));
  assert.ok(result.body.error.details.some((error) => error.includes("antipsychotic")));
  assert.ok(result.body.error.details.some((error) => error.includes("at least one clozapine")));
});

test("supports deep UUID submission identity, latest lookup, and immutable history", async () => {
  const patientId = crypto.randomUUID();
  const encounterId = crypto.randomUUID();
  const first = await request("/api/internal/medical-history/submissions", {
    method: "POST",
    body: JSON.stringify({ patientId, encounterId, author: "clinician-1", pastMedicalHistory: [], drugs: [], substantialSuicideRisk: false, priorAntipsychoticTherapy: false, clozapineContraindication: false, clozapineContraindications: [], recurrentNonAdherenceDeterioration: false }),
  });
  assert.equal(first.status, 201);
  assert.equal(first.body.patientId, patientId);
  assert.equal(first.body.encounterId, encounterId);
  assert.equal(first.body.schemaVersion, "1.0.0");
  assert.equal(first.body.author, "clinician-1");
  assert.match(first.body.etag, /^"[^"]+"$/);
  assert.equal(first.etag, first.body.etag);

  const second = await request("/api/internal/medical-history/submissions", {
    method: "POST",
    body: JSON.stringify({ patientId, encounterId, author: "clinician-1", pastMedicalHistory: ["Asthma"], drugs: [], substantialSuicideRisk: false, priorAntipsychoticTherapy: false, clozapineContraindication: false, clozapineContraindications: [], recurrentNonAdherenceDeterioration: false }),
  });
  assert.equal(second.status, 201);
  assert.notEqual(second.body.id, first.body.id);

  const latest = await request(`/api/internal/medical-history/submissions/latest?patientId=${patientId}&encounterId=${encounterId}`);
  assert.equal(latest.status, 200);
  assert.equal(latest.body.id, second.body.id);
  assert.equal(latest.body.pastMedicalHistory[0].originalText, "Asthma");
  assert.equal(latest.body.pastMedicalHistory[0].coding.resolutionStatus, "unresolved");
  assert.equal(latest.etag, latest.body.etag);

  const history = await request(`/api/internal/medical-history/submissions/history?patientId=${patientId}&encounterId=${encounterId}`);
  assert.equal(history.status, 200);
  assert.deepEqual(history.body.map((item) => item.id), [first.body.id, second.body.id]);
  assert.equal(history.body[0].pastMedicalHistory.length, 0);
});
