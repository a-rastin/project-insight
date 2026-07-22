import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { createApp, createJsonAssessmentStore, createMemoryAssessmentStore } from "./server.js";

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
      scores: { total: 37, positive: 4, negative: 2, general: 1 },
      items: { P1: 4, N1: 2, G1: 1 }
    })
  });
  assert.equal(saved.status, 200);
  assert.equal((await saved.json()).data.status, "completed");
}

test("HTTP interface works with the in-memory test adapter", async () => {
  await withServer(createMemoryAssessmentStore(), baseUrl =>
    exerciseHttpContract(baseUrl, `memory-${process.pid}-${Date.now()}`));
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


