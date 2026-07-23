import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { createDdiServer, ddiContractPayload } = require("../src/ddi-rest-adapter.cjs");
const engine = require("../src/ddi-engine.js");

const fixtureKb = {
  schemaVersion: "1.0.0",
  version: "ikb-test",
  status: "draft_parsed_pending_admin_review",
  drugs: [
    { id: "rxnorm:4493", name: "fluoxetine", aliases: ["Prozac"] },
    { id: "rxnorm:8332", name: "pimozide", aliases: [] }
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
      knowledgeBaseVersion: "ikb-test"
    }
  ]
};

function memoryStorage() {
  const store = new Map([["ikb-test", structuredClone(fixtureKb)]]);
  return {
    async load(version) { return store.has(version) ? structuredClone(store.get(version)) : null; },
    async list() { return [...store.keys()].map((version) => ({ version, status: store.get(version).status })); }
  };
}

function adminAuth() {
  return {
    async verify(cookieHeader) {
      const token = String(cookieHeader || "")
        .split(";").map((p) => p.trim())
        .find((p) => p.startsWith("insight_session="))?.slice("insight_session=".length);
      if (!token) return null;
      if (token === "admin") return { userId: "admin-1", sessionId: "s-admin", roles: ["ddi_admin"], expiresAt: "2099-01-01T00:00:00Z" };
      if (token === "doc") return { userId: "doc-1", sessionId: "s-doc", roles: ["psychiatrist"], expiresAt: "2099-01-01T00:00:00Z" };
      return null;
    }
  };
}

function startServer(options = {}) {
  const server = createDdiServer({
    knowledgeStore: memoryStorage(),
    activeVersion: "ikb-test",
    auth: adminAuth(),
    allowAdminWithoutAuth: options.allowAdminWithoutAuth ?? false,
  });
  return server;
}

async function call(server, method, path, { body, headers } = {}) {
  const init = {
    method,
    headers: headers || { "content-type": "application/json", accept: "application/json" },
  };
  if (body !== undefined) init.body = body === undefined ? undefined : (typeof body === "string" ? body : JSON.stringify(body));
  const response = await server.fetch(`http://localhost${path}`, init);
  return response;
}

function asJson(response) {
  return response.status === 204 ? null : response.json();
}

test("canonical routes /health /ready /contract /openapi.json /schemas/{version}/{name} are mounted", async () => {
  const server = startServer();
  const health = await call(server, "GET", "/health");
  assert.equal(health.status, 200);
  assert.equal((await asJson(health)).status, "ok");

  const ready = await call(server, "GET", "/ready");
  assert.equal(ready.status, 200);
  assert.deepEqual((await asJson(ready)).checks, {
    migrations: "ok",
    configuration: "ok",
    contractCompatibility: "ok",
    dependencies: "ok",
  });

  const contract = await call(server, "GET", "/contract");
  assert.equal(contract.status, 200);
  const contractBody = await asJson(contract);
  assert.equal(contractBody.moduleId, "ddi-checker");
  assert.equal(contractBody.basePath, "/api/ddi-checker/v1");
  assert.equal(contractBody.interfaceVersion, "1.0.0");
  assert.ok(contractBody.capabilities.includes("ddi.interaction-check"));
  assert.ok(contractBody.capabilities.includes("ddi.medication-resolve"));
  assert.ok(contractBody.capabilities.includes("ddi.knowledge-base.read"));
  assert.equal(contractBody.auth.required, true);
  assert.ok(contractBody.auth.schemes.includes("session"));

  const openapi = await call(server, "GET", "/openapi.json");
  assert.equal(openapi.status, 200);
  const openapiJson = await asJson(openapi);
  assert.ok(openapiJson.openapi);
  assert.ok(openapiJson.paths["/api/ddi-checker/v1/medications/resolve"]);
  assert.ok(openapiJson.paths["/api/ddi-checker/v1/interaction-checks"]);
  assert.ok(openapiJson.paths["/api/ddi-checker/v1/knowledge-bases/{version}"]);

  const schema = await call(server, "GET", "/schemas/1.0.0/problem-details");
  assert.equal(schema.status, 200);
  assert.equal((await asJson(schema)).$id, "https://insight.example/contracts/common/1.0.0/problem-details.schema.json");
});

test("POST /api/ddi-checker/v1/medications/resolve delegates to the deep module engine.resolveDrug", async () => {
  const server = startServer();
  const response = await call(server, "POST", "/api/ddi-checker/v1/medications/resolve", {
    body: {
      knowledgeBaseVersion: "ikb-test",
      input: "Prozac"
    }
  });
  assert.equal(response.status, 200);
  const body = await asJson(response);
  assert.equal(body.status, "resolved");
  assert.equal(body.drug.id, "rxnorm:4493");
});

test("POST /api/ddi-checker/v1/medications/resolve rejects unknown KB version with 404 problem-details", async () => {
  const server = startServer();
  const response = await call(server, "POST", "/api/ddi-checker/v1/medications/resolve", {
    body: { knowledgeBaseVersion: "missing", input: "Prozac" }
  });
  assert.equal(response.status, 404);
  assert.ok((await asJson(response)).code);
});

test("POST /api/ddi-checker/v1/interaction-checks fulfils the TP-13 contract", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-1",
    planSemanticHash: "plan-1",
    medicationSetHash: "set-1",
    medications: [
      { originalText: "fluoxetine", codeSystem: "rxnorm", dose: "20 mg", route: "oral", frequency: "daily" },
      { originalText: "pimozide", codeSystem: "rxnorm", dose: "1 mg", route: "oral", frequency: "daily" }
    ]
  };
  const response = await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request });
  assert.equal(response.status, 200);
  const body = await asJson(response);
  assert.equal(body.schemaVersion, "1.0.0");
  assert.equal(body.medicationSetHash, "set-1");
  assert.ok(body.knowledgeBaseId);
  assert.equal(body.knowledgeBaseVersion, "ikb-test");
  assert.ok(Array.isArray(body.normalizedMedications));
  assert.ok(Array.isArray(body.pairsChecked));
  assert.ok(Array.isArray(body.alerts));
  assert.equal(body.alerts.length, 1);
  assert.equal(body.alerts[0].severity, "contraindicated");
  assert.deepEqual(body.alerts[0].medicationInputIndexes, [0, 1]);
});

test("POST /api/ddi-checker/v1/interaction-checks fails fast when idempotency-key is missing", async () => {
  const server = startServer();
  const request = {
    planSemanticHash: "plan-1",
    medicationSetHash: "set-1",
    medications: [{ originalText: "fluoxetine" }]
  };
  const response = await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request });
  assert.equal(response.status, 400);
  assert.equal((await asJson(response)).code, "INVALID_REQUEST");
});

test("successful no-interaction check returns a TP13-distinguishable knowledgeBaseId and version", async () => {
  const server = startServer();
  const request = {
    idempotencyKey: "idem-clean",
    planSemanticHash: "p-clean",
    medicationSetHash: "s-clean",
    medications: [{ originalText: "fluoxetine", codeSystem: "rxnorm" }]
  };
  const response = await call(server, "POST", "/api/ddi-checker/v1/interaction-checks", { body: request });
  const body = await asJson(response);
  assert.equal(body.alerts.length, 0);
  assert.equal(body.unresolvedMedications.length, 0);
  assert.ok(body.knowledgeBaseId);
  assert.equal(body.knowledgeBaseVersion, "ikb-test");
});

test("GET /api/ddi-checker/v1/knowledge-bases/{version} returns the active KB summary", async () => {
  const server = startServer();
  const response = await call(server, "GET", "/api/ddi-checker/v1/knowledge-bases/ikb-test");
  assert.equal(response.status, 200);
  const body = await asJson(response);
  assert.equal(body.version, "ikb-test");
  assert.equal(body.schemaVersion, "1.0.0");
  assert.equal(body.status, "draft_parsed_pending_admin_review");
  assert.equal(body.interactions.length, 1);
  assert.equal(body.drugs.length, 2);
  assert.equal(body.interactions[0].reviewStatus, "approved");
});

test("GET /api/ddi-checker/v1/knowledge-bases/{version} 404s on unknown version", async () => {
  const server = startServer();
  const response = await call(server, "GET", "/api/ddi-checker/v1/knowledge-bases/missing");
  assert.equal(response.status, 404);
});

test("deprecated /api/ddi/v1 alias routes are mounted and forward to the canonical handlers", async () => {
  const server = startServer();
  const resolveAlias = await call(server, "POST", "/api/ddi/v1/medications/resolve", {
    body: { knowledgeBaseVersion: "ikb-test", input: "fluoxetine" }
  });
  assert.equal(resolveAlias.status, 200);
  assert.equal((await asJson(resolveAlias)).drug.id, "rxnorm:4493");

  const contract = await call(server, "GET", "/contract");
  const contractBody = await asJson(contract);
  assert.ok(contractBody.compatibilityRoutes.find((route) => route.path === "/api/ddi/v1" && route.deprecated === true));
});

test("protected admin draft/review/activate/retire/rollback routes reject unauthenticated callers", async () => {
  const server = startServer();
  for (const path of [
    "/api/ddi-checker/v1/knowledge-bases",
    "/api/ddi-checker/v1/knowledge-bases/ikb-test/review",
    "/api/ddi-checker/v1/knowledge-bases/ikb-test/activate",
    "/api/ddi-checker/v1/knowledge-bases/ikb-test/retire",
    "/api/ddi-checker/v1/knowledge-bases/ikb-test/rollback"
  ]) {
    const method = path.endsWith("/knowledge-bases") ? "GET" : "POST";
    const response = await call(server, method, path);
    assert.equal(response.status, 401, `${method} ${path}`);
    assert.equal((await asJson(response)).code, "UNAUTHENTICATED");
  }
});

test("readonly reviewers cannot call admin mutation routes", async () => {
  const server = startServer();
  const auth = { headers: { cookie: "insight_session=doc", "content-type": "application/json" } };
  const response = await call(server, "POST", "/api/ddi-checker/v1/knowledge-bases/ikb-test/activate", {
    ...auth,
    body: {}
  });
  assert.equal(response.status, 403);
  assert.equal((await asJson(response)).code, "FORBIDDEN");
});

test("admin listing returns KB versions when authenticated", async () => {
  const server = startServer();
  const response = await call(server, "GET", "/api/ddi-checker/v1/knowledge-bases", {
    headers: { cookie: "insight_session=admin", accept: "application/json" }
  });
  assert.equal(response.status, 200);
  const body = await asJson(response);
  assert.ok(Array.isArray(body));
  assert.ok(body.find((kb) => kb.version === "ikb-test"));
});

test("static UI assets are served from the existing files (UI stays, calls REST)", async () => {
  const server = startServer({ serveStatic: true });
  const html = await call(server, "GET", "/", { headers: { accept: "text/html" } });
  assert.equal(html.status, 200);
  assert.ok((await html.text()).includes("data-view=\"checker\""));
});
