import assert from "assert";
import { spawn } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";

const testItems = Object.fromEntries([
  ...Array.from({ length: 7 }, (_, index) => [`P${index + 1}`, 1]),
  ...Array.from({ length: 7 }, (_, index) => [`N${index + 1}`, 1]),
  ...Array.from({ length: 16 }, (_, index) => [`G${index + 1}`, 1])
]);

async function runTests() {
  console.log("Starting Severity API integration test...");

  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), "severity-api-"));
  const port = 4500 + (process.pid % 1000);
  const baseUrl = `http://localhost:${port}`;
  const testPatientCode = `TEST-PATIENT-${process.pid}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const serverProcess = spawn(process.execPath, ["server.js"], {
    env: { ...process.env, PORT: String(port), SEVERITY_DATA_DIR: dataDir },
    stdio: "ignore"
  });

  await new Promise(resolve => setTimeout(resolve, 1500));

  try {
    const getRes1 = await fetch(`${baseUrl}/api/severity/${testPatientCode}`);
    assert.strictEqual(getRes1.status, 200);
    const getJson1 = await getRes1.json();
    assert.strictEqual(getJson1.patient_code, testPatientCode);
    assert.strictEqual(getJson1.status, "pending");
    assert.deepStrictEqual(getJson1.scores, { total: 0, positive: 0, negative: 0, general: 0 });

    const putRes1 = await fetch(`${baseUrl}/api/severity/${testPatientCode}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "passed" })
    });
    assert.strictEqual(putRes1.status, 200);
    const putJson1 = await putRes1.json();
    assert.strictEqual(putJson1.success, true);
    assert.strictEqual(putJson1.data.status, "in_progress");

    const getJson2 = await (await fetch(`${baseUrl}/api/severity/${testPatientCode}`)).json();
    assert.strictEqual(getJson2.status, "in_progress");

    const testScores = { total: 30, positive: 7, negative: 7, general: 16 };
    const putRes2 = await fetch(`${baseUrl}/api/severity/${testPatientCode}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "completed", scores: testScores, items: testItems })
    });
    assert.strictEqual(putRes2.status, 200);
    const putJson2 = await putRes2.json();
    assert.strictEqual(putJson2.success, true);
    assert.strictEqual(putJson2.data.status, "completed");
    assert.deepStrictEqual(putJson2.data.scores, testScores);
    assert.deepStrictEqual(putJson2.data.items, testItems);

    const getJson3 = await (await fetch(`${baseUrl}/api/severity/${testPatientCode}`)).json();
    assert.strictEqual(getJson3.status, "completed");
    assert.deepStrictEqual(getJson3.scores, testScores);
    assert.deepStrictEqual(getJson3.items, testItems);
    console.log("SUCCESS: Severity API integration tests passed");
  } catch (error) {
    console.error("Test execution failed:", error);
    process.exitCode = 1;
  } finally {
    serverProcess.kill();
    fs.rmSync(dataDir, { recursive: true, force: true });
  }
}

runTests();

