import { createHash, randomUUID } from "node:crypto";

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const UTC_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/;

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
      const assessmentId = input.assessmentId || idFactory();
      requireUuid(assessmentId, "assessmentId");
      const assessments = assessmentStore.read();
      if (assessments[assessmentId]) throw new AssessmentError("assessmentId already exists", 409);

      const resource = {
        assessmentId,
        patientId: input.patientId,
        encounterId: input.encounterId,
        scale: input.scale,
        scaleVersion: input.scaleVersion,
        rater: input.rater,
        assessedAt: input.assessedAt,
        status: input.status,
        version: 1,
        updatedAt: clock().toISOString(),
        provenance: clone(input.provenance)
      };
      resource.etag = calculateEtag(resource);
      assessments[assessmentId] = resource;
      if (!assessmentStore.write(assessments)) throw new AssessmentError("Failed to write to database", 500);
      return clone(resource);
    },

    read(assessmentId) {
      const assessments = assessmentStore.read();
      return assessments[assessmentId] ? clone(assessments[assessmentId]) : null;
    },

    update(assessmentId, patch, { ifMatch } = {}) {
      const assessments = assessmentStore.read();
      const current = assessments[assessmentId];
      if (!current) return null;
      const expectedEtag = ifMatch || patch?.etag;
      if (expectedEtag !== current.etag) throw new AssessmentError("ETag does not match current resource", 412);

      const next = { ...current, ...clone(patch) };
      delete next.etag;
      delete next.version;
      delete next.updatedAt;
      delete next.assessmentId;
      validateAssessmentFields(next);

      const resource = {
        ...next,
        assessmentId,
        version: current.version + 1,
        updatedAt: clock().toISOString()
      };
      resource.etag = calculateEtag(resource);
      assessments[assessmentId] = resource;
      if (!assessmentStore.write(assessments)) throw new AssessmentError("Failed to write to database", 500);
      return clone(resource);
    }
  };
}

export { calculateEtag };
