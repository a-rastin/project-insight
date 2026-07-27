(function () {
  "use strict";

  const QUESTIONS = [
    {
      id: "q1",
      number: 1,
      text: "Have you wished you were dead or wished you could go to sleep and not wake up?",
      required: () => true,
    },
    {
      id: "q2",
      number: 2,
      text: "Have you actually had any thoughts of killing yourself?",
      required: () => true,
    },
    {
      id: "q3",
      number: 3,
      text: "Have you been thinking about how you might do this?",
      example:
        "Example: thought about taking an overdose, but no specific plan for when, where, or how, and no intent to go through with it.",
      required: (answers) => answers.q2 === true,
    },
    {
      id: "q4",
      number: 4,
      text: "Have you had these thoughts and had some intention of acting on them?",
      example: "As opposed to having the thoughts but definitely not doing anything about them.",
      required: (answers) => answers.q2 === true,
    },
    {
      id: "q5",
      number: 5,
      text: "Have you started to work out or worked out the details of how to kill yourself? Do you intend to carry out this plan?",
      required: (answers) => answers.q2 === true,
    },
    {
      id: "q6",
      number: 6,
      text: "Have you ever done anything, started to do anything, or prepared to do anything to end your life?",
      example:
        "Examples include collecting pills, obtaining a gun, writing a suicide note, interrupted or aborted attempts, or an actual attempt.",
      required: () => true,
    },
    {
      id: "q6Recent",
      number: "6a",
      text: "Was this within the past three months?",
      required: (answers) => answers.q6 === true,
    },
  ];

  function createRestAdapter(apiBase) {
    const base = apiBase.replace(/\/$/, "");
    return {
      async getPatient(patientCode) {
        return request(`${base}/api/suicide-score/patients/${encodeURIComponent(patientCode)}`);
      },
      async putScreen(patientCode, payload) {
        return request(`${base}/api/suicide-score/patients/${encodeURIComponent(patientCode)}/screen`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      },
    };
  }

  function createDemoAdapter() {
    return {
      async getPatient(patientCode) {
        return {
          patientCode,
          displayName: "Demo patient",
          source: "standalone-demo",
        };
      },
      async putScreen(patientCode, payload) {
        localStorage.setItem(`suicide-score:${patientCode}`, JSON.stringify(payload));
        return { ok: true };
      },
    };
  }

  async function request(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`Request failed with HTTP ${response.status}`);
    }
    if (response.status === 204) return {};
    return response.json();
  }

  function blankAnswers() {
    return {
      q1: null,
      q2: null,
      q3: null,
      q4: null,
      q5: null,
      q6: null,
      q6Recent: null,
    };
  }

  function evaluate(answers) {
    const required = QUESTIONS.filter((question) => question.required(answers));
    const missing = required.filter((question) => answers[question.id] === null);
    if (missing.length) {
      return {
        completed: false,
        score: null,
        result: "Incomplete",
        riskLevel: "incomplete",
        summary: `Answer ${missing.map((question) => question.number).join(", ")} to complete this screen.`,
        flags: [],
      };
    }

    let score = 0;
    for (const question of QUESTIONS.slice(0, 5)) {
      if (answers[question.id] === true) score = Math.max(score, question.number);
    }
    if (answers.q6Recent === true) score = Math.max(score, 6);

    const flags = [];
    if (answers.q6 === true) flags.push("Lifetime suicidal behavior/preparation endorsed.");
    if (answers.q6Recent === true) flags.push("Suicidal behavior/preparation within the past three months endorsed.");

    if (answers.q4 || answers.q5 || answers.q6Recent) {
      return {
        completed: true,
        score,
        result: "High risk",
        riskLevel: "high",
        summary:
          "Positive screen for high suicide risk. This requires immediate clinician review and local safety workflow.",
        flags,
      };
    }

    if (answers.q3 || answers.q6) {
      return {
        completed: true,
        score,
        result: "Moderate risk",
        riskLevel: "moderate",
        summary:
          "Positive screen for moderate suicide risk. Review protective factors, safety planning, and follow-up needs.",
        flags,
      };
    }

    if (answers.q1 || answers.q2) {
      return {
        completed: true,
        score,
        result: "Low risk",
        riskLevel: "low",
        summary: "Positive screen for suicidal ideation without endorsed method, intent, plan, or behavior.",
        flags,
      };
    }

    return {
      completed: true,
      score,
      result: "No current risk endorsed",
      riskLevel: "none",
      summary: "No C-SSRS screener items were endorsed in the required path.",
      flags,
    };
  }

  function mount(root, options) {
    const params = new URLSearchParams(window.location.search);
    const config = {
      apiBase: params.get("apiBase") || "",
      patientCode: params.get("patientCode") || "",
      dashboardUrl: params.get("dashboardUrl") || "",
      ...(options || {}),
    };
    const adapter = config.adapter || (config.apiBase ? createRestAdapter(config.apiBase) : createDemoAdapter());

    const state = {
      patient: null,
      patientCode: config.patientCode,
      answers: blankAnswers(),
      status: "",
      error: "",
      loading: false,
    };

    function render() {
      root.innerHTML = state.patient ? renderScreen(state, config) : renderLoad(state, config);
      bind(root, state, adapter, config, render);
    }

    render();
    if (state.patientCode) loadPatient(state.patientCode, state, adapter, render);
  }

  function renderLoad(state, config) {
    return `
      <section class="ss-shell">
        <div class="ss-load-panel ss-panel">
          <h1 class="ss-title">Suicide Score</h1>
          <p class="ss-subtitle">C-SSRS Screen Version - Recent</p>
          <form class="ss-loader" data-load-form>
            <input data-patient-code aria-label="Patient code" placeholder="Patient code" value="${escapeHtml(
              state.patientCode
            )}" autocomplete="off" />
            <button class="ss-button primary" type="submit">${state.loading ? "Loading..." : "Load"}</button>
          </form>
          <p class="ss-status ${state.error ? "error" : ""}">${escapeHtml(
            state.error || state.status || (config.apiBase ? "Connected to REST adapter." : "Standalone demo mode.")
          )}</p>
        </div>
      </section>
    `;
  }

  function renderScreen(state, config) {
    const conclusion = evaluate(state.answers);
    const patientLabel = state.patient.displayName
      ? `${state.patient.displayName} · ${state.patient.patientCode}`
      : state.patient.patientCode;
    return `
      <section class="ss-shell">
        <div class="ss-frame">
          <header class="ss-header">
            <div>
              <h1 class="ss-title">Suicide Score</h1>
              <p class="ss-subtitle">C-SSRS Screen Version - Recent · Patient <span class="ss-code">${escapeHtml(
                patientLabel
              )}</span></p>
            </div>
            <button class="ss-button" type="button" data-back>Back to dashboard</button>
          </header>
          <section class="ss-main ss-panel" aria-labelledby="questionnaire-title">
            <h2 class="ss-section-title" id="questionnaire-title">Past month ideation and behavior screen</h2>
            <p class="ss-instruction">Ask Q1 and Q2. Ask Q3-Q5 only when Q2 is yes. Ask the past-three-month behavior follow-up only when Q6 is yes.</p>
            <div class="ss-question-list">
              ${QUESTIONS.map((question) => renderQuestion(question, state.answers)).join("")}
            </div>
          </section>
          <aside class="ss-sidebar ss-panel" aria-live="polite">
            <span class="ss-result-badge ${conclusion.riskLevel}">${escapeHtml(conclusion.result)}</span>
            <div class="ss-score">${conclusion.score === null ? "--" : conclusion.score}</div>
            <p class="ss-summary">${escapeHtml(conclusion.summary)}</p>
            ${renderFlags(conclusion.flags)}
            <div class="ss-actions">
              <button class="ss-button primary" type="button" data-submit ${conclusion.completed ? "" : "disabled"}>Save result</button>
            </div>
            <p class="ss-status ${state.error ? "error" : ""}">${escapeHtml(
              state.error || state.status || "Result updates in real time. Final action remains clinician-controlled."
            )}</p>
          </aside>
        </div>
      </section>
    `;
  }

  function renderQuestion(question, answers) {
    const enabled = question.required(answers);
    const value = answers[question.id];
    const disabled = enabled ? "" : "disabled";
    return `
      <fieldset class="ss-question" aria-disabled="${enabled ? "false" : "true"}">
        <legend class="ss-question-legend">
          <span class="ss-number">${question.number}</span>
          <span class="ss-question-text">${escapeHtml(question.text)}</span>
        </legend>
        ${question.example ? `<p class="ss-example">${escapeHtml(question.example)}</p>` : ""}
        <div class="ss-options">
          ${renderChoice(question.id, true, "Yes", value, disabled)}
          ${renderChoice(question.id, false, "No", value, disabled)}
        </div>
      </fieldset>
    `;
  }

  function renderChoice(name, value, label, current, disabled) {
    return `
      <label class="ss-choice">
        <input type="radio" name="${name}" value="${value}" ${current === value ? "checked" : ""} ${disabled} data-answer="${name}" />
        <span>${label}</span>
      </label>
    `;
  }

  function renderFlags(flags) {
    if (!flags.length) return "";
    return `<ul class="ss-detail-list">${flags.map((flag) => `<li>${escapeHtml(flag)}</li>`).join("")}</ul>`;
  }

  function bind(root, state, adapter, config, render) {
    const loadForm = root.querySelector("[data-load-form]");
    if (loadForm) {
      loadForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const input = root.querySelector("[data-patient-code]");
        loadPatient(input.value.trim(), state, adapter, render);
      });
    }

    root.querySelectorAll("[data-answer]").forEach((input) => {
      input.addEventListener("change", () => {
        state.answers[input.dataset.answer] = input.value === "true";
        if (input.dataset.answer === "q2" && input.value === "false") {
          state.answers.q3 = null;
          state.answers.q4 = null;
          state.answers.q5 = null;
        }
        if (input.dataset.answer === "q6" && input.value === "false") {
          state.answers.q6Recent = null;
        }
        state.status = "";
        state.error = "";
        render();
      });
    });

    const submit = root.querySelector("[data-submit]");
    if (submit) {
      submit.addEventListener("click", () => submitResult(state, adapter, render));
    }

    const back = root.querySelector("[data-back]");
    if (back) {
      back.addEventListener("click", () => {
        if (config.dashboardUrl) window.location.assign(config.dashboardUrl);
        else if (history.length > 1) history.back();
        else state.status = "No dashboard URL was provided.";
        render();
      });
    }
  }

  async function loadPatient(patientCode, state, adapter, render) {
    if (!patientCode) {
      state.error = "Enter a patient code.";
      render();
      return;
    }
    state.patientCode = patientCode;
    state.loading = true;
    state.error = "";
    state.status = "";
    render();
    try {
      state.patient = await adapter.getPatient(patientCode);
      state.patient.patientCode = state.patient.patientCode || patientCode;
      state.answers = blankAnswers();
      state.status = "Patient loaded.";
    } catch (error) {
      state.error = error.message;
    } finally {
      state.loading = false;
      render();
    }
  }

  async function submitResult(state, adapter, render) {
    const conclusion = evaluate(state.answers);
    if (!conclusion.completed) return;
    await save(state, adapter, render, {
      status: "completed",
      score: conclusion.score,
      result: conclusion.result,
      riskLevel: conclusion.riskLevel,
      answers: state.answers,
      completedAt: new Date().toISOString(),
    });
  }

  async function save(state, adapter, render, payload) {
    state.error = "";
    state.status = "Saving...";
    render();
    try {
      await adapter.putScreen(state.patient.patientCode, payload);
      state.status = payload.status === "completed" ? "Result saved." : "Screen marked not completed.";
    } catch (error) {
      state.error = error.message;
    }
    render();
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  window.SuicideScore = {
    mount,
    evaluate,
    createRestAdapter,
    createDemoAdapter,
  };
})();
