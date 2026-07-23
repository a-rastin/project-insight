import assert from "node:assert/strict";
import test from "node:test";

import {
  redactProblemDetail,
  redactLogFields,
  redactExportPayload,
  redactAnalyticsPoint,
  redactCacheValue,
  safeResponseHeaders,
  clinicalResponsePolicyDefault,
} from "../contracts/adapters/node/index.mjs";

test("redactProblemDetail strips PHI from title/detail/instance and keeps structure", () => {
  const input = {
    type: "https://insight.example/problems/invalid_request",
    title: "Invalid Request",
    status: 400,
    detail: "Patient Alice (MRN abc-123) is missing an encounter date for clozapine",
    instance: "/api/ddi-checker/v1/interaction-checks?patientId=alice-99",
    code: "INVALID_REQUEST",
    requestId: "40ae4c8b-6f7e-4e54-9d3e-7e0a1a2b3c4d",
    correlationId: "11111111-2222-3333-4444-555555555555",
  };
  const redacted = redactProblemDetail(input);
  for (const forbidden of ["Alice", "abc-123", "alice-99", "clozapine", "patientId"]) {
    assert.ok(!JSON.stringify(redacted).includes(forbidden), `expected ${forbidden} removed`);
  }
  assert.equal(redacted.code, "INVALID_REQUEST");
  assert.equal(redacted.status, 400);
  assert.equal(redacted.type, input.type);
  assert.match(redacted.title, /Invalid Request/);
  assert.equal(redacted.instance, "/api/ddi-checker/v1/interaction-checks");
});

test("redactLogFields keeps allowlisted structured fields and drops payload/phi", () => {
  const fields = {
    event: "ddi.interaction-check",
    correlation_id: "11111111-2222-3333-4444-555555555555",
    actor_id: "Dr Alice",
    entity_id: "patient://alice-99",
    module: "ddi-checker",
    outcome: "success",
    payload: { patientName: "Alice", medications: ["clozapine"] },
    diagnosis: "F20",
    medication: "clozapine",
  };
  const redacted = redactLogFields(fields);
  for (const forbidden of ["Alice", "alice-99", "F20", "clozapine", "payload", "patientName", "medications"]) {
    assert.ok(!JSON.stringify(redacted).includes(forbidden), `expected ${forbidden} removed`);
  }
  assert.equal(redacted.event, "ddi.interaction-check");
  assert.equal(redacted.module, "ddi-checker");
  assert.equal(redacted.outcome, "success");
  assert.equal(redacted.correlation_id, fields.correlation_id);
  assert.ok(redacted.actor_id && redacted.actor_id.startsWith("sha256:"));
  assert.ok(redacted.entity_id && redacted.entity_id.startsWith("sha256:"));
});

test("redactLogFields rejects unallowlisted structured keys (deny-by-default)", () => {
  const redacted = redactLogFields({ event: "x.y", dosage: "5mg", patientName: "Alice" });
  for (const forbidden of ["dosage", "5mg", "patientName", "Alice"]) {
    assert.ok(!JSON.stringify(redacted).includes(forbidden));
  }
  assert.deepEqual(redacted, { event: "x.y" });
});

test("redactExportPayload redacts patient medications and audit entries while preserving schemaVersion", () => {
  const payload = {
    schemaVersion: "1.0.0",
    exportedAt: "2026-07-23T19:00:00Z",
    sessionCode: "DDI-20260723-AB12CD",
    medications: [
      { name: "Clozapine", dose: "300mg" },
      { name: "Lithium", dose: "600mg" },
    ],
    audit: [
      { action: "overridden", severity: "critical", clinician: "Dr Alice", patientId: "alice-99", reason: "rationale" },
    ],
  };
  const redacted = redactExportPayload(payload);
  for (const forbidden of ["Clozapine", "Lithium", "300mg", "600mg", "Alice", "alice-99", "rationale", "DDI-20260723-AB12CD"]) {
    assert.ok(!JSON.stringify(redacted).includes(forbidden), `expected ${forbidden} removed`);
  }
  assert.equal(redacted.schemaVersion, "1.0.0");
  assert.equal(redacted.exportedAt, payload.exportedAt);
  assert.deepEqual(redacted.medications, [{ name: "[redacted]", dose: "[redacted]" }, { name: "[redacted]", dose: "[redacted]" }]);
  assert.equal(redacted.audit.length, 1);
  assert.equal(redacted.audit[0].action, "overridden");
  assert.equal(redacted.audit[0].severity, "critical");
  assert.match(redacted.audit[0].actor_id, /^sha256:/);
  assert.match(redacted.audit[0].entity_id, /^sha256:/);
});

test("redactAnalyticsPoint keeps allowlisted metric labels and drops phi dimensions", () => {
  const point = {
    name: "ddi_interaction_checks_total",
    value: 1,
    labels: { module: "ddi-checker", outcome: "success", dependency: "bn-manager", diagnosis: "F20", patientName: "Alice" },
    correlationId: "11111111-2222-3333-4444-555555555555",
  };
  const redacted = redactAnalyticsPoint(point);
  assert.equal(redacted.name, point.name);
  assert.equal(redacted.value, 1);
  assert.deepEqual(redacted.labels, { module: "ddi-checker", outcome: "success", dependency: "bn-manager" });
  for (const forbidden of ["F20", "Alice", "diagnosis", "patientName"]) {
    assert.ok(!JSON.stringify(redacted).includes(forbidden));
  }
});

test("redactCacheValue redacts cached clinical bodies and keeps opaque bookkeeping", () => {
  const cache = {
    etag: "v1",
    updatedAt: "2026-07-23T19:00:00Z",
    cachedAt: "2026-07-23T19:01:00Z",
    body: { medications: ["clozapine"], patientId: "alice-99" },
  };
  const redacted = redactCacheValue(cache);
  for (const forbidden of ["clozapine", "alice-99", "medications", "patientId"]) {
    assert.ok(!JSON.stringify(redacted).includes(forbidden));
  }
  assert.equal(redacted.etag, "v1");
  assert.equal(redacted.updatedAt, cache.updatedAt);
  assert.equal(redacted.cachedAt, cache.cachedAt);
  assert.deepEqual(redacted.body, { phiRedacted: true });
});

test("safeResponseHeaders sets Cache-Control: no-store and Pragma: no-cache for clinical responses", () => {
  const headers = safeResponseHeaders({ clinical: true });
  assert.equal(headers.get("Cache-Control"), "no-store");
  assert.equal(headers.get("Pragma"), "no-cache");
  assert.equal(headers.get("X-Content-Type-Options"), "nosniff");
});

test("safeResponseHeaders leaves non-clinical responses cacheable", () => {
  const headers = safeResponseHeaders({ clinical: false });
  assert.ok(!headers.has("Cache-Control"));
});

test("clinicalResponsePolicyDefault requires TLS in production and never embeds keys", () => {
  const policy = clinicalResponsePolicyDefault({
    environment: "production",
    encryptionAtRestKeyRef: "kms://insight/clinical/tp",
  });
  assert.equal(policy.requireTls, true);
  assert.equal(policy.embedEncryptionKeys, false);
  assert.equal(policy.encryptionAtRestKeyRef, "kms://insight/clinical/tp");
  assert.ok(!JSON.stringify(policy).match(/[a-f0-9]{32,}/i), "no raw key material allowed");
});

test("secure cookie config flags production sessions as Secure and SameSite=Lax", () => {
  const headers = safeResponseHeaders({ clinical: true, environment: "production" });
  const setCookie = headers.get("Set-Cookie");
  if (setCookie) {
    assert.match(setCookie, /Secure/);
    assert.match(setCookie, /SameSite=Lax/);
  }
});
