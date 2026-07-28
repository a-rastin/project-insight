(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.MedicationAutocomplete = api;
})(typeof globalThis === "object" ? globalThis : this, function () {
  "use strict";

  async function defaultFetchSuggestions(query, { signal }) {
    const response = await fetch(`/api/internal/medical-history/drug-suggestions?q=${encodeURIComponent(query)}&limit=20`, {
      credentials: "same-origin",
      signal,
    });
    if (!response.ok) throw new Error("suggestion service unavailable");
    const body = await response.json();
    return Array.isArray(body.items) ? body.items : [];
  }

  function attachMedicationAutocomplete({ input, datalist, status, fetchSuggestions = defaultFetchSuggestions, debounceMs = 200 }) {
    let timer;
    let controller;
    let requestNumber = 0;
    let suggestions = [];

    function render(items) {
      const options = items.map((item) => {
        const option = datalist.ownerDocument.createElement("option");
        option.value = item.name;
        option.textContent = item.identityStatus === "approved" ? item.name : `${item.name} (identity unresolved)`;
        return option;
      });
      datalist.replaceChildren(...options);
    }

    input.addEventListener("input", () => {
      if (input.selectedMedication && input.value !== input.selectedMedication.name) input.selectedMedication = null;
      clearTimeout(timer);
      controller?.abort();
      const query = input.value.trim().replace(/\s+/g, " ");
      const currentRequest = ++requestNumber;
      if (query.length < 2) {
        suggestions = [];
        render([]);
        status.textContent = "";
        return;
      }
      status.textContent = "Loading medication suggestions...";
      timer = setTimeout(async () => {
        controller = new AbortController();
        try {
          const items = await fetchSuggestions(query, { signal: controller.signal });
          if (currentRequest !== requestNumber) return;
          suggestions = items.filter((item) => item && typeof item.id === "string" && typeof item.name === "string");
          render(suggestions);
          status.textContent = suggestions.length ? `${suggestions.length} medication suggestion(s) available.` : "No matching medications found. Free-text entry remains available.";
        } catch (error) {
          if (currentRequest !== requestNumber || error?.name === "AbortError") return;
          suggestions = [];
          render([]);
          status.textContent = "Medication suggestions are temporarily unavailable. Free-text entry remains available.";
        }
      }, debounceMs);
    });

    input.addEventListener("change", () => {
      const value = input.value.trim().toLowerCase();
      const selected = suggestions.find((item) => item.name.toLowerCase() === value);
      input.selectedMedication = selected ? { ...selected } : null;
    });

    return {
      get selection() { return input.selectedMedication || null; },
      destroy() {
        clearTimeout(timer);
        controller?.abort();
      },
    };
  }

  function medicationValue(input, fields) {
    const name = input.value.trim();
    const selected = input.selectedMedication;
    const approved = selected?.identityStatus === "approved" && typeof selected.rxcui === "string" && selected.rxcui;
    return {
      name,
      dose: String(fields.dose || "").trim(),
      route: String(fields.route || "").trim(),
      frequency: String(fields.frequency || "").trim(),
      rxNorm: approved ? {
        system: "http://www.nlm.nih.gov/research/umls/rxnorm",
        code: selected.rxcui,
        display: selected.name,
        resolutionStatus: "approved",
      } : {
        system: null,
        code: null,
        display: name,
        resolutionStatus: "unresolved",
      },
    };
  }

  return { attachMedicationAutocomplete, medicationValue };
});
