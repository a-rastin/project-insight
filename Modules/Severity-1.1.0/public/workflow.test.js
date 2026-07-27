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
    document: { getElementById: () => ({}) }
  };
  vm.createContext(context);
  vm.runInContext(script, context);
  return { ...context, location };
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

const missingCodeCalls = [];
const missingCodeWorkflow = loadWorkflow(async (...args) => missingCodeCalls.push(args));
await assert.rejects(() => missingCodeWorkflow.continueToMedicalHistory(), /No active patient is available/);
assert.deepEqual(missingCodeCalls, []);

assert.match(html, /onclick="startMedicalHistoryTransition\(currentPatientCode\)"/);
assert.match(html, />\s*Continue to Medical History\s*</);

console.log("severity workflow navigation ok");
