const test = require("node:test");
const assert = require("node:assert/strict");
const { attachMedicationAutocomplete, medicationValue } = require("../public/medication-autocomplete.js");

class FakeInput extends EventTarget {
  constructor() {
    super();
    this.value = "";
  }
}

function harness(fetchSuggestions) {
  const input = new FakeInput();
  const datalist = {
    options: [],
    ownerDocument: { createElement: () => ({ value: "", textContent: "" }) },
    replaceChildren(...options) { this.options = options; },
  };
  const status = { textContent: "" };
  const autocomplete = attachMedicationAutocomplete({ input, datalist, status, fetchSuggestions, debounceMs: 0 });
  return { input, datalist, status, autocomplete };
}

const tick = () => new Promise((resolve) => setTimeout(resolve, 5));

test("autocomplete discards stale responses and keeps latest suggestions", async () => {
  const pending = [];
  const view = harness((query, { signal }) => new Promise((resolve) => pending.push({ query, signal, resolve })));
  view.input.value = "te";
  view.input.dispatchEvent(new Event("input"));
  await tick();
  view.input.value = "test";
  view.input.dispatchEvent(new Event("input"));
  await tick();
  assert.equal(pending[0].signal.aborted, true);

  pending[1].resolve([{ id: "latest", name: "Latest Drug", rxcui: null, identityStatus: "unknown" }]);
  await tick();
  pending[0].resolve([{ id: "stale", name: "Stale Drug", rxcui: null, identityStatus: "unknown" }]);
  await tick();

  assert.deepEqual(view.datalist.options.map((option) => option.value), ["Latest Drug"]);
});

test("autocomplete retains explicit selection and invalidates it after editing", async () => {
  const item = { id: "test-id", name: "Canonical Drug", rxcui: "test-code", identityStatus: "approved" };
  const view = harness(async () => [item]);
  view.input.value = "can";
  view.input.dispatchEvent(new Event("input"));
  await tick();
  assert.equal(view.autocomplete.selection, null, "suggestions are never selected automatically");
  view.input.value = item.name;
  view.input.dispatchEvent(new Event("change"));
  assert.deepEqual(view.autocomplete.selection, item);

  view.input.value = "Changed Drug";
  view.input.dispatchEvent(new Event("input"));
  assert.equal(view.autocomplete.selection, null);
});

test("autocomplete reports empty results without blocking free text", async () => {
  const view = harness(async () => []);
  view.input.value = "unknown medication";
  view.input.dispatchEvent(new Event("input"));
  await tick();
  assert.deepEqual(view.datalist.options, []);
  assert.match(view.status.textContent, /no matching medications/i);
  assert.equal(view.input.value, "unknown medication");
});

test("autocomplete failure leaves free text usable and reports non-blocking status", async () => {
  const view = harness(async () => { throw new Error("offline"); });
  view.input.value = "free text";
  view.input.dispatchEvent(new Event("input"));
  await tick();
  assert.equal(view.input.value, "free text");
  assert.match(view.status.textContent, /temporarily unavailable/i);
});

test("medication payload codes only approved selections with RxCUI", () => {
  const input = new FakeInput();
  input.value = "Canonical Drug";
  input.selectedMedication = { id: "test-id", name: "Canonical Drug", rxcui: "test-code", identityStatus: "approved" };
  assert.deepEqual(medicationValue(input, { dose: "10 mg", route: "Oral", frequency: "Daily" }).rxNorm, {
    system: "http://www.nlm.nih.gov/research/umls/rxnorm",
    code: "test-code",
    display: "Canonical Drug",
    resolutionStatus: "approved",
  });

  input.selectedMedication.identityStatus = "pending_rxnorm_review";
  assert.deepEqual(medicationValue(input, {}).rxNorm, {
    system: null,
    code: null,
    display: "Canonical Drug",
    resolutionStatus: "unresolved",
  });
});
