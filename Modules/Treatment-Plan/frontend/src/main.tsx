import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { createReviewWorkspace, updateReviewField, type ReviewCase, type ReviewField, type ReviewWorkspace } from "./review-workspace";
import "./styles.css";

const reviewCase: ReviewCase = {
  patient: { displayId: "Synthetic patient · PT-2048", ageBand: "Adult · 30–39 years", encounterLabel: "Medication review · 14 Jul 2026" },
  dataWarnings: [
    { id: "history-stale", title: "Medical history is stale", detail: "Last verified 38 days ago. Reconcile allergies and conditions before finalization.", stale: true },
    { id: "monitoring-missing", title: "Monitoring capacity not confirmed", detail: "A current monitoring-capacity response is missing from this snapshot." },
  ],
  recommendation: {
    setting: "Outpatient",
    medication: { name: "Candidate A", code: "RXCUI-0001", dose: { amount: "2", unit: "mg" }, route: "Oral", frequency: "Once daily" },
    followUp: { amount: "7", unit: "days" },
  },
  rationale: [
    "Outpatient care ranked highest after deterministic safety exclusions were applied.",
    "Candidate A retained a preferred safety disposition and the highest eligible posterior probability.",
    "A seven-day review interval was selected because monitoring capacity is not yet confirmed.",
  ],
  alternatives: [
    { name: "Candidate B · 5 mg oral", summary: "Eligible alternative", reason: "Lower model probability; no recorded exclusion." },
    { name: "Intensive outpatient", summary: "Setting alternative", reason: "Consider if community support cannot be confirmed." },
  ],
  safetyFindings: [
    { id: "suicide-risk", level: "urgent", title: "Urgent suicide-risk review required", detail: "Conflicting risk evidence requires psychiatrist assessment. No emergency action has been recorded by INSIGHT." },
    { id: "ddi-coverage", level: "warning", title: "Interaction coverage incomplete", detail: "One current medication identity is unresolved; a no-interactions claim is not permitted." },
  ],
  provenance: {
    modelVersion: "pharmacotherapy-bn@3.2.1 · sha256:9f31…a82c",
    policyVersion: "schizophrenia-research-primary-plan@1.0.0",
    knowledgeVersion: "medication-knowledge@2026.07",
  },
};

function ComparisonField({ workspace, field, label, children }: { workspace: ReviewWorkspace; field: ReviewField; label: string; children: React.ReactNode }) {
  const comparison = workspace.comparisons[field];
  return <div className={`comparison-field${comparison.changed ? " is-changed" : ""}`}>
    <div className="field-heading"><label htmlFor={field}>{label}</label>{comparison.changed && <span className="changed-badge"><span aria-hidden="true">↺</span> Edited</span>}</div>
    {children}
    <p className="recommended-value"><span>Recommended</span><span className="old-value" aria-label={`Recommended value: ${comparison.recommended}`}>{comparison.recommended}</span></p>
  </div>;
}

function App() {
  const [workspace, setWorkspace] = useState(() => createReviewWorkspace(reviewCase));
  const [statusMessage, setStatusMessage] = useState("Draft review in progress.");
  const modifiedCount = useMemo(() => Object.values(workspace.comparisons).filter((comparison) => comparison.changed).length, [workspace]);
  const urgentFinding = workspace.urgentFindings[0];
  const edit = (field: ReviewField, value: string) => {
    setWorkspace((current) => updateReviewField(current, field, value));
    setStatusMessage("Draft updated. Safety findings remain open.");
  };
  const reset = () => {
    setWorkspace(createReviewWorkspace(reviewCase));
    setStatusMessage("All fields restored to the recommendation.");
  };

  return <>
    <a className="skip-link" href="#review-form">Skip to structured plan editor</a>
    <header className="app-header">
      <div className="brand-lockup"><img src="/insight-logo.png" alt="INSIGHT" /><span>Treatment Plan</span></div>
      <div className="header-meta"><span className="environment-badge"><span aria-hidden="true">ℹ</span> Research candidate</span><span>Psychiatrist review</span></div>
    </header>

    {urgentFinding && <div className="urgent-banner" role="alert" aria-labelledby="urgent-title">
      <div className="status-icon" aria-hidden="true">!</div>
      <div><p className="status-kicker">Urgent · action not recorded</p><h1 id="urgent-title">{urgentFinding.title}</h1><p>{urgentFinding.detail}</p></div>
      <a href="#safety-findings">Review safety findings</a>
    </div>}

    <main className="workspace-shell">
      <section className="patient-strip" aria-labelledby="patient-context-title">
        <div><p className="eyebrow">Patient context</p><h2 id="patient-context-title">{workspace.patient.displayId}</h2></div>
        <dl>
          <div><dt>Age band</dt><dd>{workspace.patient.ageBand}</dd></div>
          <div><dt>Encounter</dt><dd>{workspace.patient.encounterLabel}</dd></div>
          <div><dt>Draft status</dt><dd><span className="status-text"><span aria-hidden="true">●</span> Editing</span></dd></div>
        </dl>
      </section>

      <div className="content-grid">
        <aside aria-label="Review context">
          <section className="context-card warning-card" aria-labelledby="input-warnings-title">
            <div className="section-title-row"><span className="section-icon warning-icon" aria-hidden="true">!</span><div><p className="eyebrow">Input quality</p><h2 id="input-warnings-title">Needs attention</h2></div></div>
            <ul className="finding-list">{workspace.dataWarnings.map((warning) => <li key={warning.id}><strong>{warning.stale ? "Stale: " : "Missing: "}{warning.title}</strong><span>{warning.detail}</span></li>)}</ul>
          </section>
          <section className="context-card" aria-labelledby="rationale-title">
            <p className="eyebrow">Explainability</p><h2 id="rationale-title">Why this plan</h2>
            <ol className="rationale-list">{workspace.rationale.map((reason) => <li key={reason}>{reason}</li>)}</ol>
          </section>
          <section className="context-card" aria-labelledby="versions-title">
            <p className="eyebrow">Provenance</p><h2 id="versions-title">Versions used</h2>
            <dl className="version-list"><div><dt>Model</dt><dd>{workspace.provenance.modelVersion}</dd></div><div><dt>Policy</dt><dd>{workspace.provenance.policyVersion}</dd></div><div><dt>Knowledge</dt><dd>{workspace.provenance.knowledgeVersion}</dd></div></dl>
          </section>
        </aside>

        <div className="review-column">
          <form id="review-form" className="editor-card" onSubmit={(event) => event.preventDefault()}>
            <div className="editor-header"><div><p className="eyebrow">Structured editor</p><h2>Recommended plan</h2><p>Edited values are labelled and remain paired with the recommendation.</p></div><div className="edit-count" aria-live="polite"><strong>{modifiedCount}</strong><span>fields edited</span></div></div>
            <fieldset>
              <legend>Treatment setting</legend>
              <ComparisonField workspace={workspace} field="setting" label="Care setting"><select id="setting" value={workspace.draft.setting} onChange={(event) => edit("setting", event.target.value)}><option>Outpatient</option><option>Intensive outpatient</option><option>Inpatient</option><option>Emergency</option></select></ComparisonField>
            </fieldset>
            <fieldset>
              <legend>Pharmacotherapy</legend>
              <div className="two-column-fields">
                <ComparisonField workspace={workspace} field="medication.name" label="Medication candidate"><select id="medication.name" value={workspace.draft.medication.name} onChange={(event) => edit("medication.name", event.target.value)}><option>Candidate A</option><option>Candidate B</option><option>Candidate C</option></select></ComparisonField>
                <ComparisonField workspace={workspace} field="medication.code" label="Medication code"><input id="medication.code" value={workspace.draft.medication.code} onChange={(event) => edit("medication.code", event.target.value)} autoComplete="off" /></ComparisonField>
              </div>
              <div className="dose-group" role="group" aria-labelledby="dose-label"><span id="dose-label" className="group-label">Dose</span><div className="two-column-fields">
                <ComparisonField workspace={workspace} field="medication.dose.amount" label="Amount"><input id="medication.dose.amount" type="number" inputMode="decimal" min="0" step="0.5" value={workspace.draft.medication.dose.amount} onChange={(event) => edit("medication.dose.amount", event.target.value)} /></ComparisonField>
                <ComparisonField workspace={workspace} field="medication.dose.unit" label="Unit"><select id="medication.dose.unit" value={workspace.draft.medication.dose.unit} onChange={(event) => edit("medication.dose.unit", event.target.value)}><option>mg</option><option>mcg</option><option>mL</option></select></ComparisonField>
              </div></div>
              <div className="two-column-fields">
                <ComparisonField workspace={workspace} field="medication.route" label="Route"><select id="medication.route" value={workspace.draft.medication.route} onChange={(event) => edit("medication.route", event.target.value)}><option>Oral</option><option>Intramuscular</option><option>Subcutaneous</option></select></ComparisonField>
                <ComparisonField workspace={workspace} field="medication.frequency" label="Frequency"><select id="medication.frequency" value={workspace.draft.medication.frequency} onChange={(event) => edit("medication.frequency", event.target.value)}><option>Once daily</option><option>Twice daily</option><option>At bedtime</option></select></ComparisonField>
              </div>
            </fieldset>
            <fieldset>
              <legend>Next appointment</legend>
              <div className="two-column-fields">
                <ComparisonField workspace={workspace} field="followUp.amount" label="Interval"><input id="followUp.amount" type="number" inputMode="numeric" min="1" step="1" value={workspace.draft.followUp.amount} onChange={(event) => edit("followUp.amount", event.target.value)} /></ComparisonField>
                <ComparisonField workspace={workspace} field="followUp.unit" label="Unit"><select id="followUp.unit" value={workspace.draft.followUp.unit} onChange={(event) => edit("followUp.unit", event.target.value)}><option>days</option><option>weeks</option><option>months</option></select></ComparisonField>
              </div>
            </fieldset>
            <div className="editor-actions"><p className="sr-status" role="status" aria-live="polite">{statusMessage}</p><button className="secondary-button" type="button" onClick={reset} disabled={modifiedCount === 0}>Reset changes</button><button className="primary-button" type="button" onClick={() => setStatusMessage("Review recorded for this in-memory session. Finalization is unavailable in this research build.")}>Mark ready for review</button></div>
          </form>

          <section className="support-card" aria-labelledby="alternatives-title"><p className="eyebrow">Clinical options</p><h2 id="alternatives-title">Alternatives considered</h2><div className="alternative-list">{workspace.alternatives.map((alternative) => <article key={alternative.name}><div><h3>{alternative.name}</h3><span className="info-badge"><span aria-hidden="true">ℹ</span> {alternative.summary}</span></div><p>{alternative.reason}</p></article>)}</div></section>
          <section id="safety-findings" className="support-card" aria-labelledby="safety-title"><p className="eyebrow">Safety review</p><h2 id="safety-title">Open findings</h2><div className="safety-list">{workspace.safetyFindings.map((finding) => <article className={`safety-item ${finding.level}`} key={finding.id}><span className="section-icon" aria-hidden="true">{finding.level === "urgent" ? "!" : "△"}</span><div><p className="status-kicker">{finding.level === "urgent" ? "Urgent" : "Warning"} · Open</p><h3>{finding.title}</h3><p>{finding.detail}</p></div></article>)}</div></section>
        </div>
      </div>
    </main>
  </>;
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
