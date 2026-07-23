const crypto = require("crypto");
const fs = require("fs/promises");
const path = require("path");

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

class MedicalHistorySubmissionStore {
  constructor({ filePath, now = () => new Date(), uuid = crypto.randomUUID } = {}) {
    if (!filePath) throw new Error("filePath is required");
    this.filePath = filePath;
    this.now = now;
    this.uuid = uuid;
  }

  async ensure() {
    await fs.mkdir(path.dirname(this.filePath), { recursive: true });
    try {
      await fs.access(this.filePath);
    } catch {
      await fs.writeFile(this.filePath, "[]\n");
    }
  }

  async readAll() {
    await this.ensure();
    const raw = await fs.readFile(this.filePath, "utf8");
    const records = JSON.parse(raw || "[]");
    if (!Array.isArray(records)) throw new Error("Medical History submissions must be stored as an array");
    return records;
  }

  async writeAll(records) {
    await this.ensure();
    await fs.writeFile(this.filePath, `${JSON.stringify(records, null, 2)}\n`);
  }

  async create({ patientId, encounterId, author, data = {}, status = "submitted", code, source, allowLegacyIdentity = false, legacyPatientId, legacyEncounterId } = {}) {
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

    const records = await this.readAll();
    records.push(resource);
    await this.writeAll(records);
    return freeze(clone(resource));
  }

  async createLegacy(options = {}) {
    return this.create({ ...options, allowLegacyIdentity: true });
  }

  async findById(id) {
    const records = await this.readAll();
    const record = records.find((candidate) => candidate.id === id || candidate.submissionId === id);
    return record ? freeze(clone(record)) : null;
  }

  async getHistory({ patientId, encounterId }) {
    assertUuid(patientId, "patientId");
    assertUuid(encounterId, "encounterId");
    const records = await this.readAll();
    return records
      .filter((record) => record.patientId === patientId && record.encounterId === encounterId)
      .map((record) => freeze(clone(record)));
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
};
