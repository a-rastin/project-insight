import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const html = fs.readFileSync(new URL("./index.html", import.meta.url), "utf8");
const script = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].at(-1)[1];

function loadWorkflow(fetchImpl) {
  const location = {
    href: "https://gateway.test/modules/severity?patient_code=E98PQ5",
    search: "?patient_code=E98PQ5",
    assigned: null,
    assign(url) { this.assigned = url; }
  };
  const context = {
    URL,
    URLSearchParams,
    confirm: () => true,
    console,
    fetch: fetchImpl,
    localStorage: { getItem: () => null, setItem: () => {} },
    setTimeout: () => 0,
    window: {
      location,
      history: { pushState: () => {} },
      addEventListener: () => {}
    },
    document: {
      getElementById: () => ({
        classList: { add: () => {}, remove: () => {} },
        style: {},
        removeAttribute: () => {},
        setAttribute: () => {}
      })
    }
  };
  vm.createContext(context);
  vm.runInContext(script, context);
  context.location = location;
  return context;
}

const calls = [];
const workflow = loadWorkflow(async (url, options = {}) => {
  calls.push({ url, options });
  if (url.endsWith("/csrf")) return { ok: true, json: async () => ({ token: "csrf-token" }) };
  return { ok: true, json: async () => ({ code: "E98PQ5" }) };
});

await workflow.continueToMedicalHistory("E98PQ5");
assert.deepEqual(JSON.parse(JSON.stringify(calls)), [
  {
    url: "/api/internal/medical-history/csrf",
    options: { credentials: "same-origin", headers: { Accept: "application/json" } }
  },
  {
    url: "/api/internal/medical-history/activate",
    options: {
      method: "POST",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRF-Token": "csrf-token"
      },
      body: JSON.stringify({ code: "E98PQ5", requestedByModule: "severity", returnUrl: "/dashboard/" })
    }
  }
]);
assert.equal(workflow.location.assigned, "/modules/medical-history?code=E98PQ5");

const failedActivationWorkflow = loadWorkflow(async (url) => {
  if (url.endsWith("/csrf")) return { ok: true, json: async () => ({ token: "csrf-token" }) };
  return { ok: false, status: 422, json: async () => ({ error: { message: "Code must contain six alphanumeric characters." } }) };
});
await assert.rejects(
  () => failedActivationWorkflow.continueToMedicalHistory("E98PQ5"),
  /Code must contain six alphanumeric characters/
);
assert.equal(failedActivationWorkflow.location.assigned, null);

for (const status of ["completed", "passed"]) {
  const persistenceCalls = [];
  const persistenceWorkflow = loadWorkflow(async (url, options = {}) => {
    persistenceCalls.push({ url, options });
    if (url === "/api/v1/csrf") return { ok: true, json: async () => ({ token: "severity-csrf" }) };
    if (url.startsWith("/api/severity/")) return { ok: true, json: async () => ({ success: true }) };
    if (url.endsWith("/csrf")) return { ok: true, json: async () => ({ token: "medical-history-csrf" }) };
    return { ok: true, json: async () => ({ code: "E98PQ5" }) };
  });
  vm.runInContext('currentPatientCode = "E98PQ5"', persistenceWorkflow);
  await persistenceWorkflow.submitAssessment(status);
  assert.deepEqual(JSON.parse(JSON.stringify(persistenceCalls.slice(0, 2))), [
    {
      url: "/api/v1/csrf",
      options: { credentials: "same-origin", headers: { Accept: "application/json" } }
    },
    {
      url: "/api/severity/E98PQ5",
      options: {
        method: "PUT",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": "severity-csrf"
        },
        body: JSON.stringify(status === "completed"
          ? { status, scores: { total: 0, positive: 0, negative: 0, general: 0 }, items: {} }
          : { status })
      }
    }
  ]);
  assert.equal(vm.runInContext("currentPatientCode", persistenceWorkflow), "E98PQ5");
  assert.equal(persistenceWorkflow.location.assigned, "/modules/medical-history?code=E98PQ5");
}

const failedPersistenceCalls = [];
const failedPersistenceWorkflow = loadWorkflow(async (url, options = {}) => {
  failedPersistenceCalls.push({ url, options });
  if (url === "/api/v1/csrf") return { ok: true, json: async () => ({ token: "severity-csrf" }) };
  return { ok: false, status: 500, json: async () => ({}) };
});
vm.runInContext('currentPatientCode = "E98PQ5"', failedPersistenceWorkflow);
await failedPersistenceWorkflow.submitAssessment("passed");
assert.equal(failedPersistenceCalls.length, 2);
assert.equal(vm.runInContext("currentPatientCode", failedPersistenceWorkflow), "E98PQ5");
assert.equal(failedPersistenceWorkflow.location.assigned, null);

const missingCodeCalls = [];
const missingCodeWorkflow = loadWorkflow(async (...args) => missingCodeCalls.push(args));
await assert.rejects(() => missingCodeWorkflow.continueToMedicalHistory(), /No active patient is available/);
assert.deepEqual(missingCodeCalls, []);

assert.match(html, /onclick="startMedicalHistoryTransition\(currentPatientCode\)"/);
assert.match(html, />\s*Continue to Medical History\s*</);

console.log("severity workflow navigation ok");
