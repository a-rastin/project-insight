import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const html = fs.readFileSync(new URL("./index.html", import.meta.url), "utf8");
const script = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].at(-1)[1];

function loadWorkflow(fetchImpl, consoleImpl = console) {
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
    console: consoleImpl,
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

await workflow.continueToSuicideRisk("E98PQ5");
assert.deepEqual(JSON.parse(JSON.stringify(calls)), [
  {
    url: "/api/suicide-risk/v1/csrf",
    options: { credentials: "same-origin", headers: { Accept: "application/json" } }
  },
  {
    url: "/api/suicide-risk/v1/activate",
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
assert.equal(workflow.location.assigned, "/modules/suicide-risk/?code=E98PQ5");

const loggedErrors = [];
const failedActivationWorkflow = loadWorkflow(async (url) => {
  if (url.endsWith("/csrf")) return { ok: true, json: async () => ({ token: "csrf-token" }) };
  return { ok: false, status: 422, json: async () => ({ error: { message: "Code must contain six alphanumeric characters." } }) };
}, { ...console, error: (...args) => loggedErrors.push(args) });
await assert.rejects(
  () => failedActivationWorkflow.continueToSuicideRisk("E98PQ5"),
  /Code must contain six alphanumeric characters/
);
assert.equal(failedActivationWorkflow.location.assigned, null);
assert.deepEqual(JSON.parse(JSON.stringify(loggedErrors)), [[
  "Suicide Risk request failed",
  { endpoint: "/api/suicide-risk/v1/activate", status: 422 }
]]);

for (const status of ["completed", "passed"]) {
  const persistenceCalls = [];
  const persistenceWorkflow = loadWorkflow(async (url, options = {}) => {
    persistenceCalls.push({ url, options });
    if (url === "/api/v1/csrf") return { ok: true, json: async () => ({ token: "severity-csrf" }) };
    if (url.startsWith("/api/severity/")) return { ok: true, json: async () => ({ success: true }) };
    if (url.endsWith("/csrf")) return { ok: true, json: async () => ({ token: "suicide-risk-csrf" }) };
    return { ok: true, json: async () => ({ code: "E98PQ5" }) };
  });
  vm.runInContext('currentPatientCode = "E98PQ5"', persistenceWorkflow);
  await persistenceWorkflow.submitAssessment(status);
  assert.deepEqual(JSON.parse(JSON.stringify(persistenceCalls)), [
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
    },
    {
      url: "/api/suicide-risk/v1/csrf",
      options: { credentials: "same-origin", headers: { Accept: "application/json" } }
    },
    {
      url: "/api/suicide-risk/v1/activate",
      options: {
        method: "POST",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRF-Token": "suicide-risk-csrf"
        },
        body: JSON.stringify({ code: "E98PQ5", requestedByModule: "severity", returnUrl: "/dashboard/" })
      }
    }
  ]);
  assert.equal(vm.runInContext("currentPatientCode", persistenceWorkflow), "E98PQ5");
  assert.equal(persistenceWorkflow.location.assigned, "/modules/suicide-risk/?code=E98PQ5");
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
await assert.rejects(() => missingCodeWorkflow.continueToSuicideRisk(), /No active patient is available/);
assert.deepEqual(missingCodeCalls, []);

assert.match(html, /onclick="startSuicideRiskTransition\(currentPatientCode\)"/);
assert.match(html, />\s*Continue to Suicide Risk\s*</);

console.log("severity workflow navigation ok");
