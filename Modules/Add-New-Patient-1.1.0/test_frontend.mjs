import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import vm from "node:vm";

const here = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(resolve(here, "index.html"), "utf8");
const appSource = readFileSync(resolve(here, "app.js"), "utf8");

function loadApp(overrides = {}) {
  const source = appSource.replace(
    /window\.createAddNewPatientModule[\s\S]*$/,
    "globalThis.appUnderTest = { createAddNewPatientModule, normalizePatientInput, validatePatientPayload };"
  );
  const context = { URLSearchParams, ...overrides };
  vm.runInNewContext(source, context);
  return context.appUnderTest;
}

test("dashboard view renders with activate control", () => {
  assert.match(html, /id="dashboardView"/);
  assert.match(html, /id="activateModuleButton"[^>]*type="button"/);
  assert.match(html, /id="dashboardTitle"[\s\S]*?>Add New Patient</);
  assert.match(html, /id="listPatientsButton"[^>]*type="button"/);
  assert.match(html, /id="patientsView"/);
  assert.match(html, /id="patientList"/);
});

test("form exposes demographics only", () => {
  for (const name of [
    "firstName",
    "lastName",
    "sex",
    "dob",
    "phoneNumber"
  ]) {
    assert.ok(html.includes(`name="${name}"`), `missing form field: ${name}`);
  }
  for (const name of [
    "presentingComplaint",
    "provisionalDiagnosis",
    "treatmentHistory",
    "allergies",
    "currentMedications",
    "suicidality",
    "substanceUse"
  ]) {
    assert.ok(!html.includes(`name="${name}"`), `unexpected clinical field: ${name}`);
  }
  assert.match(html, />Save and Continue to Severity</);
});

test("status message exposes aria-live region", () => {
  assert.match(html, /id="statusMessage"[^>]*role="status"[^>]*aria-live="polite"/);
});

test("demographics payload validates without clinical fields", () => {
  const { normalizePatientInput, validatePatientPayload } = loadApp();
  const payload = normalizePatientInput({
    firstName: " Jane ",
    lastName: " Doe ",
    sex: "Female",
    dob: "1980-01-01",
    phoneNumber: "(555) 123-4567"
  });

  assert.deepEqual(JSON.parse(JSON.stringify(payload)), {
    demographics: {
      firstName: "Jane",
      lastName: "Doe",
      sex: "Female",
      dob: "1980-01-01",
      phoneNumber: "5551234567"
    }
  });
  assert.deepEqual(JSON.parse(JSON.stringify(validatePatientPayload(payload))), {});
  assert.ok("demographics.firstName" in validatePatientPayload({ demographics: {} }));
  assert.ok("demographics.dob" in validatePatientPayload({ demographics: { dob: "2999-01-01" } }));
  assert.ok("demographics.phoneNumber" in validatePatientPayload({ demographics: { phoneNumber: "123" } }));
});

async function submitWorkflowPatient(patientCode) {
  const handlers = {};
  const assigned = [];
  const values = {
    firstName: "Jane",
    lastName: "Doe",
    sex: "Female",
    dob: "1980-01-01",
    phoneNumber: "555-123-4567"
  };
  const node = () => ({
    dataset: {},
    addEventListener(type, listener) { handlers[type] = listener; },
    removeEventListener() {},
    focus() {},
    replaceChildren() {},
    append() {}
  });
  const patientForm = node();
  patientForm.elements = { firstName: node(), phoneNumber: node() };
  patientForm.querySelectorAll = () => [];
  patientForm.reset = () => {};
  const nodes = {
    "#dashboardView": node(), "#patientView": node(), "#activateModuleButton": node(),
    "#listPatientsButton": node(), "#patientsView": node(), "#patientsBackButton": node(),
    "#patientList": node(), "#backButton": node(), "#patientForm": patientForm,
    "#patientCode": node(), "#statusMessage": node(), "#workflowStatus": node()
  };
  const root = { querySelector: (selector) => nodes[selector], querySelectorAll: () => [] };
  const window = { location: { search: "?workflow=draft-1", assign: (url) => assigned.push(url) } };
  const requests = [];
  const response = (body) => ({ ok: true, json: async () => body });
  const fetch = async (url, options = {}) => {
    requests.push({ url, options });
    if (url.endsWith("/workflow-drafts/draft-1")) return response({ workflowDraft: { id: "draft-1", patientCode: "A B/C", phase: "patient-information" } });
    if (url.endsWith("/csrf")) return response({ csrfToken: "csrf" });
    return response({ patient: patientCode ? { patientCode } : {} });
  };
  class TestFormData { constructor() {} get(name) { return values[name] ?? null; } }
  const { createAddNewPatientModule } = loadApp({
    window,
    document: { createElement: node },
    fetch,
    FormData: TestFormData,
    RadioNodeList: class {}
  });
  createAddNewPatientModule({ root });
  await new Promise((resolve) => setImmediate(resolve));
  await handlers.submit({ preventDefault() {} });

  return { assigned, nodes, requests };
}

test("successful save sends demographics then opens Severity", async () => {
  const { assigned, requests } = await submitWorkflowPatient("A B/C");

  const saveRequest = requests.at(-1);
  assert.deepEqual(JSON.parse(saveRequest.options.body), {
    demographics: {
      firstName: "Jane", lastName: "Doe", sex: "Female", dob: "1980-01-01", phoneNumber: "5551234567"
    }
  });
  assert.deepEqual(assigned, ["/modules/severity?patient_code=A%20B%2FC"]);
});

test("missing patient code reports error without navigation", async () => {
  const { assigned, nodes } = await submitWorkflowPatient("");

  assert.deepEqual(assigned, []);
  assert.equal(nodes["#statusMessage"].dataset.tone, "error");
});
