import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { createDdiServer } = require("../src/ddi-rest-adapter.cjs");
const engine = require("../src/ddi-engine.js");

// DDI-02 — Request/response contract for the standalone REST seam.
//
// Request: medication concepts with originalText, normalized identity when
// known (medicationCode/codeSystem), dose, route, frequency, optional
// patientId/encounterId only when persistence is requested, and idempotencyKey.
//
// Response: normalized + unresolved medications, every pair checked, alerts,
// severity, mechanism, evidence, recommendation, knowledgeBaseVersion,
// medicationSetHash, and a coverage status object.
//
// Zero alerts with unresolved identity or incomplete pair coverage MUST return
// indeterminate — never "no interactions".

const fixtureKb = {
  schemaVersion: "1.0.0",
  version: "ikb-test",
  status: "draft_parsed_pending_admin_review",
  drugs: [
    { id: "rxnorm:4493", name: "fluoxetine", aliases: ["Prozac"] },
    { id: "rxnorm:8332", name: "pimozide", aliases: [] },
    { id: "rxnorm:51272", name: "quetiapine", aliases: ["Seroquel"] },
    { id: "local:first", name: "first drug", aliases: ["shared"] },
    { id: "local:second", name: "second drug", aliases: ["shared"] },
  ],
  interactions: [
    {
      id: "ddi-1",
      drugAId: "rxnorm:4493",
      drugAName: "fluoxetine",
      drugBId: "rxnorm:8332",
      drugBName: "pimozide",
      severity: "contraindicated",
      mechanism: "QTc prolongation",
      clinicalEffect: "fluoxetine + pimozide both increase QTc.",
      recommendation: "Do not coadminister.",
      monitoring: "ECG/QTc",
      evidenceSource: "fixture",
      evidenceExcerpt: "fluoxetine + pimozide both increase QTc. Contraindicated.",
      sourceReportPath: "fixture",
      reviewStatus: "approved",
      knowledgeBaseVersion: "ikb-test",
    },
  ],
};

test("medication suggestions rank canonical and alias matches and preserve identity metadata", async () => {
  const kb = structuredClone(fixtureKb);
  kb.drugs = [
    { id: "exact", name: "Test Drug", aliases: [], rxcui: "100", identityStatus: "approved" },
    { id: "canonical-prefix", name: "Test Drug Extended", aliases: [], rxcui: "101", identityStatus: "approved" },
    { id: "alias-prefix", name: "Canonical Alias Match", aliases: ["test drug alias"], rxcui: null, identityStatus: "pending_rxnorm_review" },
    { id: "substring", name: "A Test Drug Substring", aliases: [], rxcui: "102", identityStatus: "approved" },
    { id: "alias-substring", name: "Canonical Alias Substring", aliases: ["a test drug alias"], rxcui: null, identityStatus: "unknown" },
    { id: "exact", name: "Duplicate Identity", aliases: ["test drug"], rxcui: "999", identityStatus: "unknown" },
  ];
  const server = createDdiServer({
    knowledgeStore: { async load() { return kb; } },
    activeVersion: "ikb-test",
  });

  const response = await call(server, "GET", "/api/ddi-checker/v1/medications/suggestions?q=%20TEST%20%20DRUG%20&limit=10");
  assert.equal(response.status, 200);
  const body = await asJson(response);
  assert.equal(body.query, "TEST DRUG");
  assert.equal(body.knowledgeBaseVersion, "ikb-test");
  assert.deepEqual(body.items.map((item) => item.id), [
    "exact",
    "canonical-prefix",
    "alias-prefix",
    "substring",
    "alias-substring",
  ]);
  assert.deepEqual(body.items[0], {
    id: "exact",
    name: "Test Drug",
    aliases: [],
    rxcui: "100",
    identityStatus: "approved",
  });
  assert.equal(body.items[2].identityStatus, "pending_rxnorm_review");
});

test("medication suggestions enforce query and safe result limits", async () => {
  const server = startServer();
  const shortQuery = await call(server, "GET", "/api/ddi-checker/v1/medications/suggestions?q=p");
  assert.equal(shortQuery.status, 400);
  assert.equal((await asJson(shortQuery)).code, "INVALID_QUERY");

  const limited = await call(server, "GET", "/api/ddi-checker/v1/medications/suggestions?q=pi&limit=999");
  assert.equal(limited.status, 400);
  assert.equal((await asJson(limited)).code, "INVALID_QUERY");

  const response = await call(server, "GET", "/api/ddi-checker/v1/medications/suggestions?q=pi&limit=1");
  assert.equal(response.status, 200);
  assert.equal((await asJson(response)).items.length, 1);
});

function memoryStorage() {
  const store = new Map([["ikb-test", structuredClone(fixtureKb)]]);
  return {
    async load(version) {
      return store.has(version) ? structuredClone(store.get(version)) : null;
    },
    async list() {
      return [...store.keys()].map((version) => ({ version, status: store.get(version).status }));
    },
  };
}

function startServer(options = {}) {
  return createDdiServer({
    knowledgeStore: memoryStorage(),
    activeVersion: "ikb-test",
    allowAdminWithoutAuth: options.allowAdminWithoutAuth ?? false,
  });
}

async function call(server, method, path, { body, headers } = {}) {
  const init = {
    method,
    headers: headers || { "content-type": "application/json", accept: "application/json" },
  };
  if (body !== undefined) init.body = typeof body === "string" ? body : JSON.stringify(body);
  return server.fetch(`http://localhost${path}`, init);
}

function asJson(response) {
  return response.status === 204 ? null : response.json();
}

function medicationSet(meds) {
  return meds.map((med, index) => ({
    inputIndex: index,
    originalText: med.originalText,
    medicationCode: med.medicationCode,
    codeSystem: med.codeSystem,
    dose: med.dose,
    route: med.route,
    frequency: med.frequency,
  }));
}

test("DDI-02 request accepts medication concepts with originalText, identity, dose, route, frequency, idempotencyKey", async () => {
  const server = startServer();
  const request = {
    schemaVersion: "1.0.0",
    idempotencyKey: "idem-contract",
    medicationSetHash: "set-contract",
    medications: medicationSet([
      { originalText: "Prozac", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
      { originalText: "pimozide", medicationCode: "rxnorm:8332", codeSystem: "RxNorm", dose: "1 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const response = await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request });
  assert.equal(response.status, 200);
  const body = await asJson(response);

  // normalized identity when known is echoed back with conceptId + display
  assert.equal(body.normalizedMedications.length, 2);
  for (const [index, expected] of [[0, "rxnorm:4493"], [1, "rxnorm:8332"]]) {
    const identity = body.normalizedMedications[index];
    assert.equal(identity.inputIndex, index);
    assert.equal(typeof identity.conceptId, "string");
    assert.ok(identity.conceptId.length > 0);
    assert.equal(identity.codeSystem, "RxNorm");
  }
});

test("DDI-02 response carries severity, mechanism, evidence, and recommendation on each alert", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-fields",
    medicationSetHash: "set-fields",
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
      { originalText: "pimozide", medicationCode: "rxnorm:8332", codeSystem: "RxNorm", dose: "1 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));

  assert.equal(body.alerts.length, 1);
  const alert = body.alerts[0];
  assert.deepEqual(alert.medicationInputIndexes, [0, 1]);
  assert.equal(alert.severity, "contraindicated");
  assert.equal(typeof alert.mechanism, "string");
  assert.ok(alert.mechanism.length > 0);
  assert.ok(Array.isArray(alert.evidence));
  assert.ok(alert.evidence.length > 0);
  assert.equal(typeof alert.recommendation, "string");
  assert.ok(alert.recommendation.length > 0);
});

test("DDI-02 response carries knowledgeBaseVersion, medicationSetHash, and a coverage status object", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-coverage",
    medicationSetHash: "set-coverage",
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
      { originalText: "pimozide", medicationCode: "rxnorm:8332", codeSystem: "RxNorm", dose: "1 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));

  assert.equal(body.knowledgeBaseVersion, "ikb-test");
  assert.equal(body.medicationSetHash, "set-coverage");
  assert.ok(body.coverage && typeof body.coverage === "object");
  assert.equal(body.coverage.medicationCount, 2);
  assert.equal(body.coverage.resolved, 2);
  assert.equal(body.coverage.unresolved, 0);
  assert.equal(body.coverage.pairsExpected, 1);
  assert.equal(body.coverage.pairsChecked, 1);
  assert.equal(body.coverage.complete, true);
});

test("DDI-02 clean check returns outcome no-interactions and coverage complete", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-clean2",
    medicationSetHash: "set-clean2",
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));
  assert.equal(body.alerts.length, 0);
  assert.equal(body.normalizedMedications.length, 1);
  assert.equal(body.unresolvedMedications.length, 0);
  assert.equal(body.outcome, "no-interactions");
  assert.equal(body.coverage.complete, true);
});

test("DDI-02 ambiguous identity is reported unresolved with candidates and outcome indeterminate", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-amb",
    medicationSetHash: "set-amb",
    medications: medicationSet([
      { originalText: "pimozide", medicationCode: "rxnorm:8332", codeSystem: "RxNorm", dose: "1 mg", route: "oral", frequency: "daily" },
      { originalText: "shared", codeSystem: "local", dose: "1 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));

  // The ambiguous "shared" must not be reported as normalized (no conceptId)
  assert.equal(body.normalizedMedications.length, 1);
  assert.equal(body.normalizedMedications[0].inputIndex, 0);
  assert.equal(body.unresolvedMedications.length, 1);
  const unresolved = body.unresolvedMedications[0];
  assert.equal(unresolved.inputIndex, 1);
  assert.equal(unresolved.reason, "ambiguous");
  assert.ok(Array.isArray(unresolved.candidates));
  assert.equal(unresolved.candidates.length, 2);
  assert.deepEqual(unresolved.candidates.map((c) => c.conceptId).sort(), ["local:first", "local:second"]);

  // Zero alerts but indeterminate — NOT "no interactions"
  assert.equal(body.alerts.length, 0);
  assert.equal(body.outcome, "indeterminate");
  assert.equal(body.coverage.complete, false);
  assert.equal(body.coverage.unresolved, 1);
});

test("DDI-02 unknown identity is reported unresolved with reason unknown and outcome indeterminate", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-unknown",
    medicationSetHash: "set-unknown",
    medications: medicationSet([
      { originalText: "pimozide", medicationCode: "rxnorm:8332", codeSystem: "RxNorm", dose: "1 mg", route: "oral", frequency: "daily" },
      { originalText: "totally unknown drug", codeSystem: "rxnorm", dose: "5 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));

  assert.equal(body.normalizedMedications.length, 1);
  assert.equal(body.unresolvedMedications.length, 1);
  assert.equal(body.unresolvedMedications[0].inputIndex, 1);
  assert.equal(body.unresolvedMedications[0].reason, "unknown");
  assert.ok(Array.isArray(body.unresolvedMedications[0].candidates));
  assert.equal(body.unresolvedMedications[0].candidates.length, 0);

  assert.equal(body.alerts.length, 0);
  assert.equal(body.outcome, "indeterminate");
  assert.equal(body.coverage.complete, false);
  assert.equal(body.coverage.unresolved, 1);
});

test("DDI-02 every normalized medication pair is checked and coverage reports completeness", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-every-pair",
    medicationSetHash: "set-every-pair",
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
      { originalText: "pimozide", medicationCode: "rxnorm:8332", codeSystem: "RxNorm", dose: "1 mg", route: "oral", frequency: "daily" },
      { originalText: "quetiapine", medicationCode: "rxnorm:51272", codeSystem: "RxNorm", dose: "50 mg", route: "oral", frequency: "nightly" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));

  // 3 normalized medications → C(3,2) = 3 unique pairs required
  assert.equal(body.normalizedMedications.length, 3);
  assert.equal(body.unresolvedMedications.length, 0);
  assert.equal(body.coverage.medicationCount, 3);
  assert.equal(body.coverage.resolved, 3);
  assert.equal(body.coverage.pairsExpected, 3);
  assert.equal(body.coverage.pairsChecked, 3);
  // When all normalized identities are resolved, every expected pair MUST be checked
  assert.equal(body.coverage.complete, true);
});

test("DDI-02 a single resolved medication with no pairs is no-interactions, not indeterminate", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-single",
    medicationSetHash: "set-single",
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));
  assert.equal(body.outcome, "no-interactions");
  assert.equal(body.coverage.complete, true);
  assert.equal(body.coverage.pairsExpected, 0);
  assert.equal(body.coverage.pairsChecked, 0);
});

test("DDI-02 idempotencyKey is required and echoed back as checkId when present", async () => {
  const server = startServer();
  const missing = await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", {
    body: {
      medicationSetHash: "set-no-idem",
      medications: medicationSet([{ originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm" }]),
    },
  });
  assert.equal(missing.status, 400);
  assert.equal((await asJson(missing)).code, "INVALID_REQUEST");

  const present = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", {
    body: {
      idempotencyKey: "idem-echo",
      medicationSetHash: "set-echo",
      medications: medicationSet([{ originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm" }]),
    },
  }));
  assert.equal(typeof present.checkId, "string");
  assert.ok(present.checkId.length > 0);
});

test("DDI-02 optional patientId/encounterId are accepted when persist=true is requested", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-persist",
    medicationSetHash: "set-persist",
    persist: true,
    patientId: "patient-512",
    encounterId: "encounter-789",
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const response = await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request });
  assert.equal(response.status, 200);
  const body = await asJson(response);
  assert.equal(body.outcome, "no-interactions");
  // DDI-02 leaves persistence wiring to a later packet; the seam must accept
  // the persist marker without erroring. It must not pretend to have persisted:
  assert.equal(body.persisted, false);
});

test("DDI-02 patientId/encounterId omitted when persist flag is absent is normal flow", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-nopersist",
    medicationSetHash: "set-nopersist",
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));
  assert.equal(body.outcome, "no-interactions");
  assert.equal(body.persisted, undefined);
});

test("DDI-02 idempotencyKey with persist=true but missing patientId/encounterId is rejected", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-persist-missing-ids",
    medicationSetHash: "set-persist-missing-ids",
    persist: true,
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const response = await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request });
  assert.equal(response.status, 400);
  assert.equal((await asJson(response)).code, "INVALID_REQUEST");
});

test("DDI-02 idempotencyKey with patientId set but persist=false/absent stays a normal check", async () => {
  const server = startServer();
  // patientId arriving without persist=true is tolerated (deferred to caller);
  // persistence is only invoked when persist=true. This is the safe contract.
  const request = {
    idempotencyKey: "idem-id-without-persist",
    medicationSetHash: "set-id-without-persist",
    patientId: "patient-extra",
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));
  assert.equal(body.outcome, "no-interactions");
  assert.equal(body.persisted, undefined);
});

test("DDI-02 TP-13 recommendedAction alias is still present alongside recommendation", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-alias",
    medicationSetHash: "set-alias",
    medications: medicationSet([
      { originalText: "fluoxetine", medicationCode: "rxnorm:4493", codeSystem: "RxNorm", dose: "20 mg", route: "oral", frequency: "daily" },
      { originalText: "pimozide", medicationCode: "rxnorm:8332", codeSystem: "RxNorm", dose: "1 mg", route: "oral", frequency: "daily" },
    ]),
  };
  const body = await asJson(await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request }));
  assert.equal(body.alerts.length, 1);
  assert.equal(typeof body.alerts[0].recommendedAction, "string");
  assert.ok(body.alerts[0].recommendedAction.length > 0);
  assert.equal(body.alerts[0].recommendation, body.alerts[0].recommendedAction);
});
