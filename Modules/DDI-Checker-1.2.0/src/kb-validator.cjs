// DDI-04: clinical and structural KB validation shared between the
// ESM CLI (scripts/validate-kb.mjs) and the CJS server store
// (src/kb-sqlite.cjs). Pure JS, no module-system-specific syntax so
// both CommonJS require() and ESM import can load the same source.
//
// Kept in lockstep with the clinical activation gate declared in
// validate-kb.mjs: rxnorm-pending identities, low-confidence approved
// records, clinicalUse.allowedForProduction, at least one approved
// interaction, and an active root status are all enforced here.

const REQUIRED = ["id", "drugAId", "drugBId", "severity", "mechanism", "clinicalEffect", "recommendation", "monitoring", "evidenceSource", "evidenceExcerpt", "sourceReportPath", "reviewedBy", "reviewedAt", "reviewStatus", "parserConfidence", "knowledgeBaseVersion"];
const SEVERITY = new Set(["contraindicated", "major", "moderate", "minor", "unknown"]);
const STATES = new Set(["parsed_pending_review", "uploaded_pending_review", "manual_pending_review", "edited_pending_review", "approved", "rejected"]);
const CONFIDENCE = new Set(["low", "medium", "high"]);

function object(v) { return v !== null && typeof v === "object" && !Array.isArray(v); }
function text(v) { return typeof v === "string" && v.trim().length > 0; }
function label(v) { return String(v || "").trim().toLowerCase().replace(/\s+/g, " "); }
function timestamp(v) { return text(v) && !Number.isNaN(Date.parse(v)); }
function pair(r) { return [r.drugAId, r.drugBId].sort().join("::"); }
function fingerprint(r) { return JSON.stringify([r.severity, r.mechanism, r.clinicalEffect, r.recommendation, r.monitoring, r.evidenceSource, r.evidenceExcerpt, r.sourceReportPath]); }

function validateKnowledgeBase(kb, { clinicalActive = false } = {}) {
  const errors = [];
  if (!object(kb)) return ["root must be a JSON object"];
  for (const field of ["schemaVersion", "version", "status"]) if (!text(kb[field])) errors.push(`root.${field} must be a non-empty string`);
  if (!Array.isArray(kb.drugs)) errors.push("root.drugs must be an array");
  if (!Array.isArray(kb.interactions)) errors.push("root.interactions must be an array");
  if (!object(kb.clinicalUse)) errors.push("root.clinicalUse must be an object");
  if (kb.reports !== undefined && !Array.isArray(kb.reports)) errors.push("root.reports must be an array when present");
  if (!Array.isArray(kb.drugs) || !Array.isArray(kb.interactions)) return errors;

  const drugIds = new Set(), drugs = new Map(), labels = new Map();
  kb.drugs.forEach((drug, i) => {
    const at = `drug[${i}]`;
    if (!object(drug)) return errors.push(`${at} must be an object`);
    if (!text(drug.id)) errors.push(`${at}.id must be a non-empty string`);
    else if (drugIds.has(drug.id)) errors.push(`${at} has duplicate drug id ${drug.id}`);
    else { drugIds.add(drug.id); drugs.set(drug.id, drug); }
    if (!text(drug.name)) errors.push(`${at}.name must be a non-empty string`);
    if (!Array.isArray(drug.aliases) || drug.aliases.some(a => !text(a))) errors.push(`${at}.aliases must be an array of non-empty strings`);
    const names = [["canonical name", drug.name], ...(Array.isArray(drug.aliases) ? drug.aliases.map(a => ["alias", a]) : [])];
    for (const [kind, name] of names) {
      const key = label(name), owner = labels.get(key);
      if (!key || !text(drug.id)) continue;
      if (owner && owner.id !== drug.id) errors.push(`${at} ${kind} "${name}" is ambiguous with ${owner.at} (${owner.id})`);
      else if (!owner) labels.set(key, { id: drug.id, at: `${at}.${kind}` });
    }
  });

  const ids = new Set(), pairs = new Map();
  let approved = 0;
  kb.interactions.forEach((r, i) => {
    const at = `interaction[${i}]`;
    if (!object(r)) return errors.push(`${at} must be an object`);
    for (const field of REQUIRED) if (!(field in r)) errors.push(`${at} missing ${field}`);
    if (!text(r.id)) errors.push(`${at}.id must be a non-empty string`);
    else if (ids.has(r.id)) errors.push(`${at} has duplicate interaction id ${r.id}`);
    else ids.add(r.id);
    if (!SEVERITY.has(r.severity)) errors.push(`${at} has invalid severity ${String(r.severity)}`);
    if (!STATES.has(r.reviewStatus)) errors.push(`${at} has invalid reviewStatus ${String(r.reviewStatus)}`);
    if (!CONFIDENCE.has(r.parserConfidence)) errors.push(`${at} has invalid parserConfidence ${String(r.parserConfidence)}`);
    if (!drugIds.has(r.drugAId)) errors.push(`${at} missing drugA reference ${String(r.drugAId)}`);
    if (!drugIds.has(r.drugBId)) errors.push(`${at} missing drugB reference ${String(r.drugBId)}`);
    if (r.drugAId === r.drugBId) errors.push(`${at} is self-referential`);
    if (r.knowledgeBaseVersion !== kb.version) errors.push(`${at} knowledgeBaseVersion must match root.version ${String(kb.version)}`);
    if (r.reviewStatus === "approved" || r.reviewStatus === "rejected") {
      if (!text(r.reviewedBy)) errors.push(`${at} ${r.reviewStatus} record requires reviewedBy`);
      if (!timestamp(r.reviewedAt)) errors.push(`${at} ${r.reviewStatus} record requires a valid reviewedAt timestamp`);
    } else if (STATES.has(r.reviewStatus) && (r.reviewedBy != null || r.reviewedAt != null)) {
      errors.push(`${at} pending record must not have reviewedBy or reviewedAt`);
    }
    const key = pair(r), prior = pairs.get(key);
    if (prior) errors.push(`${at} is an ${prior.fingerprint === fingerprint(r) ? "exact duplicate" : "conflicting record"} for pair ${key}; first defined by ${prior.id}`);
    else if (text(r.drugAId) && text(r.drugBId)) pairs.set(key, { id: r.id || at, fingerprint: fingerprint(r) });
    if (r.reviewStatus === "approved") {
      approved++;
      if (clinicalActive) {
        for (const id of [r.drugAId, r.drugBId]) if (drugs.get(id) && drugs.get(id).identityStatus !== "rxnorm_seeded") errors.push(`${at} approved record is clinically ineligible: ${id} is not RxNorm-resolved`);
        if (r.parserConfidence === "low") errors.push(`${at} approved record is clinically ineligible: parserConfidence is low`);
      }
    }
  });
  if (clinicalActive) {
    if (!approved) errors.push("clinical-active mode requires at least one approved interaction");
    if (kb.clinicalUse && kb.clinicalUse.allowedForProduction !== true) errors.push("clinical-active mode requires clinicalUse.allowedForProduction to be true");
    if (!text(kb.status) || !kb.status.toLowerCase().startsWith("active")) errors.push("clinical-active mode requires an active root.status");
    if (!timestamp(kb.activatedAt)) errors.push("clinical-active mode requires a valid activatedAt timestamp");
  }
  return errors;
}

module.exports = { validateKnowledgeBase, REQUIRED, SEVERITY, STATES, CONFIDENCE };
