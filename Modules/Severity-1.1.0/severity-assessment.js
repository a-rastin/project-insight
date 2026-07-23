import { createHash, randomUUID } from "node:crypto";

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const UTC_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/;
const PANSS_ITEM_CODES = [
  ...Array.from({ length: 7 }, (_, index) => `P${index + 1}`),
  ...Array.from({ length: 7 }, (_, index) => `N${index + 1}`),
  ...Array.from({ length: 16 }, (_, index) => `G${index + 1}`)
];

export class AssessmentError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.name = "AssessmentError";
    this.status = status;
  }
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function requireUuid(value, field) {
  if (typeof value !== "string" || !UUID_PATTERN.test(value) || /^0{8}-0{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-0{12}$/i.test(value)) {
    throw new AssessmentError(`${field} must be a UUID`);
  }
}

function requireUtcTimestamp(value, field) {
  if (typeof value !== "string" || !UTC_PATTERN.test(value) || !Number.isFinite(Date.parse(value))) {
    throw new AssessmentError(`${field} must be a UTC timestamp`);
  }
}

function validateProvenance(provenance) {
  if (!provenance || typeof provenance !== "object" || Array.isArray(provenance)) {
    throw new AssessmentError("provenance is required");
  }
  if (typeof provenance.sourceModule !== "string" || !/^[a-z][a-z0-9.-]{0,63}$/.test(provenance.sourceModule)) {
    throw new AssessmentError("provenance.sourceModule is invalid");
  }
  requireUuid(provenance.sourceResourceId, "provenance.sourceResourceId");
  requireUtcTimestamp(provenance.recordedAt, "provenance.recordedAt");
  if (provenance.recordedBy !== undefined && (typeof provenance.recordedBy !== "string" || !provenance.recordedBy)) {
    throw new AssessmentError("provenance.recordedBy is invalid");
  }
  if (provenance.sourceReference !== undefined && (typeof provenance.sourceReference !== "string" || !provenance.sourceReference)) {
    throw new AssessmentError("provenance.sourceReference is invalid");
  }
}

function validateAssessmentFields(input, { requireStatus = true } = {}) {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    throw new AssessmentError("assessment payload must be an object");
  }
  requireUuid(input.patientId, "patientId");
  requireUuid(input.encounterId, "encounterId");
  if (input.scale !== "PANSS") throw new AssessmentError("scale must be 'PANSS'");
  if (typeof input.scaleVersion !== "string" || !input.scaleVersion.trim()) {
    throw new AssessmentError("scaleVersion is required");
  }
  if (typeof input.rater !== "string" || !input.rater.trim()) {
    throw new AssessmentError("rater is required");
  }
  requireUtcTimestamp(input.assessedAt, "assessedAt");
  if (requireStatus && !["in_progress", "completed"].includes(input.status)) {
    throw new AssessmentError("status must be 'in_progress' or 'completed'");
  }
  validateProvenance(input.provenance);
}

function validatePanssItems(items, requireComplete) {
  if (!items || typeof items !== "object" || Array.isArray(items)) {
    throw new AssessmentError("items must be an object");
  }
  const allowed = new Set(PANSS_ITEM_CODES);
  for (const [code, value] of Object.entries(items)) {
    if (!allowed.has(code)) throw new AssessmentError(`Unknown PANSS item: ${code}`);
    if (!Number.isInteger(value) || value < 1 || value > 7) {
      throw new AssessmentError(`${code} must be an integer from 1 to 7`);
    }
  }
  const missing = PANSS_ITEM_CODES.filter(code => !Object.hasOwn(items, code));
  if (requireComplete && missing.length) {
    throw new AssessmentError(`Missing PANSS items: ${missing.join(", ")}`);
  }
}

function scoresForItems(items) {
  const positive = PANSS_ITEM_CODES.filter(code => code.startsWith("P")).reduce((sum, code) => sum + (items[code] || 0), 0);
  const negative = PANSS_ITEM_CODES.filter(code => code.startsWith("N")).reduce((sum, code) => sum + (items[code] || 0), 0);
  const general = PANSS_ITEM_CODES.filter(code => code.startsWith("G")).reduce((sum, code) => sum + (items[code] || 0), 0);
  return { positive, negative, general, total: positive + negative + general };
}

function scoresMatch(actual, expected) {
  return actual && typeof actual === "object" &&
    ["positive", "negative", "general", "total"].every(field => actual[field] === expected[field]);
}

export function computePanssScores(items) {
  validatePanssItems(items, true);
  return scoresForItems(items);
}

function applyPanssScores(input) {
  const hasItems = input.items !== undefined;
  const hasScores = input.scores !== undefined;
  if (!hasItems) {
    if (hasScores || input.status === "completed") {
      throw new AssessmentError("completed assessments require all 30 PANSS items");
    }
    return input;
  }

  validatePanssItems(input.items, input.status === "completed");
  const scores = scoresForItems(input.items);
  if (hasScores && !scoresMatch(input.scores, scores)) {
    throw new AssessmentError("supplied scores do not match PANSS item responses");
  }
  return { ...input, items: clone(input.items), scores };
}

function calculateEtag(resource) {
  const content = JSON.stringify({ ...resource, etag: undefined });
  const digest = createHash("sha256").update(content).digest("hex");
  return `"sha256:${digest}"`;
}

export function createSeverityAssessmentModule({ assessmentStore, idFactory = randomUUID, clock = () => new Date() }) {
  if (!assessmentStore || typeof assessmentStore.read !== "function" || typeof assessmentStore.write !== "function") {
    throw new TypeError("assessmentStore must implement read() and write()");
  }

  return {
    create(input) {
      validateAssessmentFields(input);
      const assessed = applyPanssScores(input);
      const assessmentId = assessed.assessmentId || idFactory();
      requireUuid(assessmentId, "assessmentId");
      const resource = {
        assessmentId,
        patientId: assessed.patientId,
        encounterId: assessed.encounterId,
        scale: assessed.scale,
        scaleVersion: assessed.scaleVersion,
        rater: assessed.rater,
        assessedAt: assessed.assessedAt,
        status: assessed.status,
        version: 1,
        updatedAt: clock().toISOString(),
        provenance: clone(assessed.provenance)
      };
      if (assessed.items) resource.items = assessed.items;
      if (assessed.scores) resource.scores = assessed.scores;
      resource.etag = calculateEtag(resource);
      if (typeof assessmentStore.insert === "function") {
        if (!assessmentStore.insert(resource)) throw new AssessmentError("assessmentId already exists", 409);
      } else {
        const assessments = assessmentStore.read();
        if (assessments[assessmentId]) throw new AssessmentError("assessmentId already exists", 409);
        assessments[assessmentId] = resource;
        if (!assessmentStore.write(assessments)) throw new AssessmentError("Failed to write to database", 500);
      }
      return clone(resource);
    },

    read(assessmentId) {
      const assessments = assessmentStore.read();
      return assessments[assessmentId] ? clone(assessments[assessmentId]) : null;
    },

    update(assessmentId, patch, { ifMatch } = {}) {
      const current = typeof assessmentStore.get === "function"
        ? assessmentStore.get(assessmentId)
        : assessmentStore.read()[assessmentId];
      if (!current) return null;
      const expectedEtag = ifMatch || patch?.etag;
      if (expectedEtag !== current.etag) throw new AssessmentError("ETag does not match current resource", 412);

      const next = { ...current, ...clone(patch) };
      if (patch.items !== undefined && patch.scores === undefined) delete next.scores;
      delete next.etag;
      delete next.version;
      delete next.updatedAt;
      delete next.assessmentId;
      validateAssessmentFields(next);
      const assessed = applyPanssScores(next);

      const resource = {
        ...assessed,
        assessmentId,
        version: current.version + 1,
        updatedAt: clock().toISOString()
      };
      resource.etag = calculateEtag(resource);
      if (typeof assessmentStore.compareAndSwap === "function") {
        const updated = assessmentStore.compareAndSwap(assessmentId, expectedEtag, resource);
        if (!updated) throw new AssessmentError("ETag does not match current resource", 412);
        return clone(updated);
      }
      if (typeof assessmentStore.update === "function") {
        const updated = assessmentStore.update(assessmentId, expectedEtag, () => resource);
        if (!updated) throw new AssessmentError("ETag does not match current resource", 412);
        return clone(updated);
      }
      const assessments = assessmentStore.read();
      assessments[assessmentId] = resource;
      if (!assessmentStore.write(assessments)) throw new AssessmentError("Failed to write to database", 500);
      return clone(resource);
    }
  };
}

export { calculateEtag };
