import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { createApp, createJsonAssessmentStore, createMemoryAssessmentStore } from "./server.js";

const assessmentMetadata = {
  patientId: "11111111-1111-4111-8111-111111111111",
  encounterId: "22222222-2222-4222-8222-222222222222",
  scale: "PANSS",
  scaleVersion: "1.0.0",
  rater: "rater-1",
  assessedAt: "2026-01-02T03:04:05Z",
  status: "in_progress",
  provenance: {
    sourceModule: "severity",
    sourceResourceId: "33333333-3333-4333-8333-333333333333",
    recordedAt: "2026-01-02T03:04:06Z",
    recordedBy: "rater-1"
  }
};

const panssItems = Object.fromEntries([
  ...Array.from({ length: 7 }, (_, index) => [`P${index + 1}`, 1]),
  ...Array.from({ length: 7 }, (_, index) => [`N${index + 1}`, 1]),
  ...Array.from({ length: 16 }, (_, index) => [`G${index + 1}`, 1])
]);

function createCanonicalAssessment(baseUrl) {
  return fetch(`${baseUrl}/api/v1/severity-assessments`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(assessmentMetadata)
  }).then(response => response.json());
}

async function withServer(store, callback) {
  const server = createApp({ assessmentStore: store }).listen(0);
  try {
    const address = server.address();
    const baseUrl = `http://127.0.0.1:${address.port}`;
    return await callback(baseUrl);
  } finally {
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
}

async function exerciseHttpContract(baseUrl, patientCode) {
  const initial = await fetch(`${baseUrl}/api/severity/${patientCode}`);
  assert.equal(initial.status, 200);
  assert.equal((await initial.json()).status, "pending");

  const saved = await fetch(`${baseUrl}/api/severity/${patientCode}`, {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      status: "completed",
      scores: { total: 30, positive: 7, negative: 7, general: 16 },
      items: panssItems
    })
  });
  assert.equal(saved.status, 200);
  assert.equal((await saved.json()).data.status, "completed");
}

test("HTTP interface works with the in-memory test adapter", async () => {
  await withServer(createMemoryAssessmentStore(), baseUrl =>
    exerciseHttpContract(baseUrl, `memory-${process.pid}-${Date.now()}`));
});

test("canonical assessment interface creates, reads, and conditionally updates a versioned resource", async () => {
  await withServer(createMemoryAssessmentStore(), async baseUrl => {
    const createdResponse = await fetch(`${baseUrl}/api/v1/severity-assessments`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(assessmentMetadata)
    });

    assert.equal(createdResponse.status, 201);
    const created = await createdResponse.json();
    assert.match(created.assessmentId, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
    assert.equal(created.patientId, assessmentMetadata.patientId);
    assert.equal(created.encounterId, assessmentMetadata.encounterId);
    assert.equal(created.scale, "PANSS");
    assert.equal(created.scaleVersion, assessmentMetadata.scaleVersion);
    assert.equal(created.rater, assessmentMetadata.rater);
    assert.equal(created.assessedAt, assessmentMetadata.assessedAt);
    assert.equal(created.status, "in_progress");
    assert.equal(created.version, 1);
    assert.equal(created.etag, createdResponse.headers.get("etag"));
    assert.deepEqual(created.provenance, assessmentMetadata.provenance);

    const readResponse = await fetch(`${baseUrl}/api/v1/severity-assessments/${created.assessmentId}`);
    assert.equal(readResponse.status, 200);
    assert.deepEqual(await readResponse.json(), created);
    assert.equal(readResponse.headers.get("etag"), created.etag);

    const updatedResponse = await fetch(`${baseUrl}/api/v1/severity-assessments/${created.assessmentId}`, {
      method: "PUT",
      headers: {
        "content-type": "application/json",
        "if-match": created.etag
      },
      body: JSON.stringify({ rater: "rater-2" })
    });

    assert.equal(updatedResponse.status, 200);
    const updated = await updatedResponse.json();
    assert.equal(updated.rater, "rater-2");
    assert.equal(updated.status, "in_progress");
    assert.equal(updated.version, 2);
    assert.notEqual(updated.etag, created.etag);
    assert.equal(updatedResponse.headers.get("etag"), updated.etag);

    const staleResponse = await fetch(`${baseUrl}/api/v1/severity-assessments/${created.assessmentId}`, {
      method: "PUT",
      headers: {
        "content-type": "application/json",
        "if-match": created.etag
      },
      body: JSON.stringify({ rater: "stale" })
    });
    assert.equal(staleResponse.status, 412);
  });
});

test("canonical PANSS scoring computes boundary totals and recomputes deterministically", async () => {
  await withServer(createMemoryAssessmentStore(), async baseUrl => {
    const created = await createCanonicalAssessment(baseUrl);
    const minimumResponse = await fetch(`${baseUrl}/api/v1/severity-assessments/${created.assessmentId}`, {
      method: "PUT",
      headers: { "content-type": "application/json", "if-match": created.etag },
      body: JSON.stringify({ status: "completed", items: panssItems, scores: { positive: 7, negative: 7, general: 16, total: 30 } })
    });
    assert.equal(minimumResponse.status, 200);
    const minimum = await minimumResponse.json();
    assert.deepEqual(minimum.scores, { positive: 7, negative: 7, general: 16, total: 30 });

    const maximumItems = Object.fromEntries(Object.keys(panssItems).map(code => [code, 7]));
    const maximumResponse = await fetch(`${baseUrl}/api/v1/severity-assessments/${created.assessmentId}`, {
      method: "PUT",
      headers: { "content-type": "application/json", "if-match": minimum.etag },
      body: JSON.stringify({ items: maximumItems, scores: { positive: 49, negative: 49, general: 112, total: 210 } })
    });
    assert.equal(maximumResponse.status, 200);
    const maximum = await maximumResponse.json();
    assert.deepEqual(maximum.scores, { positive: 49, negative: 49, general: 112, total: 210 });

    const repeatResponse = await fetch(`${baseUrl}/api/v1/severity-assessments/${created.assessmentId}`, {
      method: "PUT",
      headers: { "content-type": "application/json", "if-match": maximum.etag },
      body: JSON.stringify({ items: maximumItems })
    });
    assert.equal(repeatResponse.status, 200);
    assert.deepEqual((await repeatResponse.json()).scores, maximum.scores);
  });
});

test("canonical PANSS scoring rejects missing items, invalid values, and mismatched totals", async () => {
  await withServer(createMemoryAssessmentStore(), async baseUrl => {
    const missing = await createCanonicalAssessment(baseUrl);
    const missingItems = { ...panssItems };
    delete missingItems.G16;
    const missingResponse = await fetch(`${baseUrl}/api/v1/severity-assessments/${missing.assessmentId}`, {
      method: "PUT",
      headers: { "content-type": "application/json", "if-match": missing.etag },
      body: JSON.stringify({ status: "completed", items: missingItems })
    });
    assert.equal(missingResponse.status, 400);

    const invalid = await createCanonicalAssessment(baseUrl);
    const invalidItems = { ...panssItems, P1: 8 };
    const invalidResponse = await fetch(`${baseUrl}/api/v1/severity-assessments/${invalid.assessmentId}`, {
      method: "PUT",
      headers: { "content-type": "application/json", "if-match": invalid.etag },
      body: JSON.stringify({ status: "completed", items: invalidItems })
    });
    assert.equal(invalidResponse.status, 400);

    const mismatched = await createCanonicalAssessment(baseUrl);
    const mismatchResponse = await fetch(`${baseUrl}/api/v1/severity-assessments/${mismatched.assessmentId}`, {
      method: "PUT",
      headers: { "content-type": "application/json", "if-match": mismatched.etag },
      body: JSON.stringify({
        status: "completed",
        items: panssItems,
        scores: { positive: 7, negative: 7, general: 16, total: 31 }
      })
    });
    assert.equal(mismatchResponse.status, 400);
  });
});

test("canonical assessments reject the legacy passed status", async () => {
  await withServer(createMemoryAssessmentStore(), async baseUrl => {
    const response = await fetch(`${baseUrl}/api/v1/severity-assessments`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ ...assessmentMetadata, status: "passed" })
    });
    assert.equal(response.status, 400);
  });
});

test("HTTP interface works with an isolated production JSON adapter", async () => {
  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), "severity-contract-"));
  const patientCode = `json-${process.pid}-${Date.now()}`;
  try {
    await withServer(createJsonAssessmentStore({ dataDir }), baseUrl =>
      exerciseHttpContract(baseUrl, patientCode));

    await withServer(createJsonAssessmentStore({ dataDir }), async baseUrl => {
      const response = await fetch(`${baseUrl}/api/severity/${patientCode}`);
      assert.equal(response.status, 200);
      assert.equal((await response.json()).status, "completed");
    });
  } finally {
    fs.rmSync(dataDir, { recursive: true, force: true });
  }
});
