const crypto = require("crypto");

const SUBMISSION_SCHEMA_VERSION = "1.0.0";

class SubmissionValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "SubmissionValidationError";
    this.status = 422;
  }
}

function isCanonicalUuid(value) {
  return typeof value === "string"
    && /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(value)
    && value !== "00000000-0000-0000-0000-000000000000";
}

function clone(value) {
  return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
}

function freeze(value) {
  if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
  Object.freeze(value);
  Object.values(value).forEach(freeze);
  return value;
}

function assertUuid(value, field) {
  if (!isCanonicalUuid(value)) throw new SubmissionValidationError(`${field} must be a canonical non-nil UUID`);
}

function assertAuthor(author) {
  if ((typeof author !== "string" || author.trim() === "") && (!author || typeof author !== "object")) {
    throw new SubmissionValidationError("author is required");
  }
}

function calculateEtag(resource) {
  const source = JSON.stringify(resource);
  return `"${crypto.createHash("sha256").update(source).digest("hex")}"`;
}

function unresolvedCoding(text) {
  return {
    system: null,
    code: null,
    display: text,
    resolutionStatus: "unresolved",
  };
}

function isApprovedCoding(coding) {
  return Boolean(
    coding
    && typeof coding === "object"
    && coding.resolutionStatus === "approved"
    && typeof coding.system === "string"
    && coding.system.trim() !== ""
    && typeof coding.code === "string"
    && coding.code.trim() !== ""
    && typeof coding.display === "string"
    && coding.display.trim() !== "",
  );
}

function normalizeCoding(coding, fallbackText) {
  if (isApprovedCoding(coding)) {
    return {
      system: String(coding.system).trim(),
      code: String(coding.code).trim(),
      display: String(coding.display).trim(),
      resolutionStatus: "approved",
    };
  }
  const display = coding && typeof coding.display === "string" && coding.display.trim() !== ""
    ? coding.display.trim()
    : fallbackText;
  return unresolvedCoding(display);
}

function structureCondition(entry) {
  if (typeof entry === "string") {
    const originalText = entry.trim();
    return { originalText, coding: unresolvedCoding(originalText) };
  }
  if (!entry || typeof entry !== "object") {
    throw new SubmissionValidationError("condition entry must be a string or object");
  }
  const originalText = String(entry.originalText ?? entry.text ?? entry.name ?? "").trim();
  if (!originalText) throw new SubmissionValidationError("condition originalText is required");
  return {
    originalText,
    coding: normalizeCoding(entry.coding, originalText),
  };
}

function structureMedication(drug = {}) {
  if (!drug || typeof drug !== "object") {
    throw new SubmissionValidationError("medication entry must be an object");
  }
  const originalText = String(drug.originalText ?? drug.name ?? "").trim();
  if (!originalText) throw new SubmissionValidationError("medication originalText is required");
  const doseAmount = drug.doseAmount === null || drug.doseAmount === undefined || drug.doseAmount === ""
    ? null
    : Number(drug.doseAmount);
  if (doseAmount !== null && !Number.isFinite(doseAmount)) {
    throw new SubmissionValidationError("medication doseAmount must be a finite number when provided");
  }
  const doseUnit = drug.doseUnit === null || drug.doseUnit === undefined || drug.doseUnit === ""
    ? null
    : String(drug.doseUnit).trim();
  return {
    originalText,
    rxNorm: normalizeCoding(drug.rxNorm ?? drug.coding, originalText),
    doseAmount,
    doseUnit,
    dose: drug.dose ? String(drug.dose).trim() : "",
    route: drug.route ? String(drug.route).trim() : "",
    frequency: drug.frequency ? String(drug.frequency).trim() : "",
  };
}

class MedicalHistorySubmissionStore {
  constructor({ repository, now = () => new Date(), uuid = crypto.randomUUID } = {}) {
    if (!repository) throw new Error("repository is required");
    this.repository = repository;
    this.now = now;
    this.uuid = uuid;
  }

  buildResource({ patientId, encounterId, author, data = {}, status = "submitted", code, source, allowLegacyIdentity = false, legacyPatientId, legacyEncounterId } = {}) {
    if (!allowLegacyIdentity) {
      assertUuid(patientId, "patientId");
      assertUuid(encounterId, "encounterId");
    } else {
      if (patientId !== null && patientId !== undefined) assertUuid(patientId, "patientId");
      if (encounterId !== null && encounterId !== undefined) assertUuid(encounterId, "encounterId");
    }
    assertAuthor(author);
    if (typeof status !== "string" || status.trim() === "") throw new SubmissionValidationError("status is required");

    const timestamp = this.now();
    if (!(timestamp instanceof Date) || !Number.isFinite(timestamp.getTime())) throw new Error("now must return a valid Date");
    const id = this.uuid();
    assertUuid(id, "submission UUID");
    const submissionData = clone(data) || {};
    const resource = {
      ...submissionData,
      id,
      submissionId: id,
      patientId: patientId ?? null,
      encounterId: encounterId ?? null,
      schemaVersion: SUBMISSION_SCHEMA_VERSION,
      author: clone(author),
      createdAt: timestamp.toISOString(),
      updatedAt: timestamp.toISOString(),
      submittedAt: timestamp.toISOString(),
      status: status.trim(),
      version: 1,
      data: submissionData,
    };
    if (code !== undefined) resource.code = code;
    if (source !== undefined) resource.source = source;
    if (legacyPatientId !== undefined) resource.legacyPatientId = legacyPatientId;
    if (legacyEncounterId !== undefined) resource.legacyEncounterId = legacyEncounterId;
    resource.etag = calculateEtag(resource);
    return resource;
  }

  async create(options = {}) {
    const resource = this.buildResource(options);
    return this.repository.appendSubmission(resource);
  }

  async createLegacy(options = {}) {
    return this.create({ ...options, allowLegacyIdentity: true });
  }

  async findById(id) {
    return this.repository.findSubmissionById(id);
  }

  async getHistory({ patientId, encounterId }) {
    assertUuid(patientId, "patientId");
    assertUuid(encounterId, "encounterId");
    return this.repository.getSubmissionHistory({ patientId, encounterId });
  }

  async getLatest(identity) {
    const history = await this.getHistory(identity);
    return history.length ? history[history.length - 1] : null;
  }
}

module.exports = {
  MedicalHistorySubmissionStore,
  SubmissionValidationError,
  SUBMISSION_SCHEMA_VERSION,
  isCanonicalUuid,
  unresolvedCoding,
  structureCondition,
  structureMedication,
};
