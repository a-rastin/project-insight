const fs = require("fs");
const path = require("path");

function clone(value) {
  return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
}

function freeze(value) {
  if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
  Object.freeze(value);
  Object.values(value).forEach(freeze);
  return value;
}

function readJsonFile(filePath, fallback) {
  if (!fs.existsSync(filePath)) return fallback;
  const parsed = JSON.parse(fs.readFileSync(filePath, "utf8") || "null");
  return parsed == null ? fallback : parsed;
}

function assertArray(value, label) {
  if (!Array.isArray(value)) throw new TypeError(`${label} must be an array`);
}

class MemoryMedicalHistoryRepository {
  constructor({ activations = [], submissions = [], audits = [] } = {}) {
    assertArray(activations, "activations");
    assertArray(submissions, "submissions");
    assertArray(audits, "audits");
    this._activations = clone(activations);
    this._submissions = clone(submissions);
    this._audits = clone(audits);
    this._lock = Promise.resolve();
  }

  async _withLock(work) {
    const run = this._lock.then(work, work);
    this._lock = run.then(() => undefined, () => undefined);
    return run;
  }

  ping() {
    return true;
  }

  listActivations() {
    return clone(this._activations);
  }

  getActivationByCode(code) {
    const normalized = String(code || "").trim().toUpperCase();
    const match = this._activations.find((row) => row.code === normalized);
    return match ? clone(match) : null;
  }

  upsertActivation(activation) {
    return this._withLock(async () => {
      const code = String(activation.code || "").trim().toUpperCase();
      const next = clone({ ...activation, code });
      const index = this._activations.findIndex((row) => row.code === code && row.status !== "expired");
      if (index >= 0) this._activations[index] = next;
      else this._activations.push(next);
      return clone(next);
    });
  }

  replaceActivation(activation) {
    return this._withLock(async () => {
      const code = String(activation.code || "").trim().toUpperCase();
      const next = clone({ ...activation, code });
      const index = this._activations.findIndex((row) => row.code === code);
      if (index >= 0) this._activations[index] = next;
      else this._activations.push(next);
      return clone(next);
    });
  }

  listSubmissions({ code } = {}) {
    const rows = code
      ? this._submissions.filter((row) => row.code === String(code).trim().toUpperCase())
      : this._submissions;
    return clone(rows);
  }

  findSubmissionById(id) {
    const row = this._submissions.find((candidate) => candidate.id === id || candidate.submissionId === id);
    return row ? freeze(clone(row)) : null;
  }

  getSubmissionHistory({ patientId, encounterId }) {
    return freeze(clone(
      this._submissions.filter((row) => row.patientId === patientId && row.encounterId === encounterId),
    ));
  }

  appendSubmission(resource) {
    return this._withLock(async () => {
      const next = clone(resource);
      this._submissions.push(next);
      return freeze(clone(next));
    });
  }

  submitLegacyWithActivation({ activation, submission }) {
    return this._withLock(async () => {
      const code = String(activation.code || "").trim().toUpperCase();
      const nextActivation = clone({ ...activation, code });
      const nextSubmission = clone(submission);
      const index = this._activations.findIndex((row) => row.code === code);
      if (index >= 0) this._activations[index] = nextActivation;
      else this._activations.push(nextActivation);
      this._submissions.push(nextSubmission);
      return {
        activation: clone(nextActivation),
        submission: freeze(clone(nextSubmission)),
      };
    });
  }

  appendAudit(entry) {
    const next = clone({
      id: this._audits.length + 1,
      createdAt: entry.createdAt || new Date().toISOString(),
      ...entry,
    });
    this._audits.push(next);
    return clone(next);
  }

  listAudits({ patientId, submissionId } = {}) {
    return clone(this._audits.filter((row) => {
      if (patientId && row.patientId !== patientId) return false;
      if (submissionId && row.submissionId !== submissionId) return false;
      return true;
    }));
  }

  applyRetention({ cutoffIso, redactedAtIso }) {
    let submissionsRedacted = 0;
    this._submissions = this._submissions.map((row) => {
      const stamp = row.submittedAt || row.createdAt;
      if (!stamp || stamp > cutoffIso) return row;
      if (row.phiRedactedAt) return row;
      submissionsRedacted += 1;
      return {
        id: row.id,
        submissionId: row.submissionId || row.id,
        patientId: row.patientId ?? null,
        encounterId: row.encounterId ?? null,
        schemaVersion: row.schemaVersion,
        author: "[redacted]",
        createdAt: row.createdAt,
        updatedAt: row.updatedAt,
        submittedAt: row.submittedAt,
        status: row.status,
        version: row.version,
        etag: row.etag,
        code: row.code,
        source: row.source,
        phiRedactedAt: redactedAtIso,
        data: null,
      };
    });
    return { submissionsRedacted, auditsPreserved: this._audits.length };
  }
}

function openSqlite(databaseFile) {
  // Lazy require keeps pure-memory tests free of the native binding.
  const Database = require("better-sqlite3");
  const db = new Database(databaseFile);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  db.exec(`
    CREATE TABLE IF NOT EXISTS activations (
      code TEXT PRIMARY KEY,
      resource_json TEXT NOT NULL,
      status TEXT,
      updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS submissions (
      submission_id TEXT PRIMARY KEY,
      patient_id TEXT,
      encounter_id TEXT,
      code TEXT,
      submitted_at TEXT,
      resource_json TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_submissions_identity
      ON submissions(patient_id, encounter_id, submitted_at, submission_id);
    CREATE INDEX IF NOT EXISTS idx_submissions_code ON submissions(code);
    CREATE TABLE IF NOT EXISTS audit_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      action TEXT NOT NULL,
      actor TEXT,
      role TEXT,
      patient_id TEXT,
      submission_id TEXT,
      detail_json TEXT,
      created_at TEXT NOT NULL
    );
  `);
  return db;
}

class SqliteMedicalHistoryRepository {
  constructor({
    dataDir = process.env.MEDICAL_HISTORY_DATA_DIR || path.join(__dirname, "data"),
    databaseFile = "medical_history.sqlite",
  } = {}) {
    fs.mkdirSync(dataDir, { recursive: true });
    this.databaseFilePath = path.isAbsolute(databaseFile)
      ? databaseFile
      : path.join(dataDir, databaseFile);
    this.db = openSqlite(this.databaseFilePath);
    this._insertActivation = this.db.prepare(`
      INSERT INTO activations (code, resource_json, status, updated_at)
      VALUES (@code, @resource_json, @status, @updated_at)
      ON CONFLICT(code) DO UPDATE SET
        resource_json = excluded.resource_json,
        status = excluded.status,
        updated_at = excluded.updated_at
    `);
    this._insertSubmission = this.db.prepare(`
      INSERT INTO submissions (submission_id, patient_id, encounter_id, code, submitted_at, resource_json)
      VALUES (@submission_id, @patient_id, @encounter_id, @code, @submitted_at, @resource_json)
    `);
    this._insertAudit = this.db.prepare(`
      INSERT INTO audit_events (action, actor, role, patient_id, submission_id, detail_json, created_at)
      VALUES (@action, @actor, @role, @patient_id, @submission_id, @detail_json, @created_at)
    `);
  }

  ping() {
    return this.db.prepare("SELECT 1 AS ok").get().ok === 1;
  }

  close() {
    this.db.close();
  }

  listActivations() {
    return this.db.prepare("SELECT resource_json FROM activations ORDER BY code")
      .all()
      .map((row) => JSON.parse(row.resource_json));
  }

  getActivationByCode(code) {
    const normalized = String(code || "").trim().toUpperCase();
    const row = this.db.prepare("SELECT resource_json FROM activations WHERE code = ?").get(normalized);
    return row ? JSON.parse(row.resource_json) : null;
  }

  upsertActivation(activation) {
    const code = String(activation.code || "").trim().toUpperCase();
    const next = clone({ ...activation, code });
    const tx = this.db.transaction(() => {
      const existing = this.getActivationByCode(code);
      if (existing && existing.status === "expired") {
        // Keep expired rows addressable; still allow replace for re-activate.
      }
      this._insertActivation.run({
        code,
        resource_json: JSON.stringify(next),
        status: next.status || null,
        updated_at: next.receivedAt || next.submittedAt || new Date().toISOString(),
      });
      return next;
    });
    return tx();
  }

  replaceActivation(activation) {
    return this.upsertActivation(activation);
  }

  listSubmissions({ code } = {}) {
    if (code) {
      const normalized = String(code).trim().toUpperCase();
      return this.db.prepare("SELECT resource_json FROM submissions WHERE code = ? ORDER BY submitted_at, submission_id")
        .all(normalized)
        .map((row) => JSON.parse(row.resource_json));
    }
    return this.db.prepare("SELECT resource_json FROM submissions ORDER BY submitted_at, submission_id")
      .all()
      .map((row) => JSON.parse(row.resource_json));
  }

  findSubmissionById(id) {
    const row = this.db.prepare("SELECT resource_json FROM submissions WHERE submission_id = ?").get(id);
    return row ? freeze(JSON.parse(row.resource_json)) : null;
  }

  getSubmissionHistory({ patientId, encounterId }) {
    const rows = this.db.prepare(`
      SELECT resource_json FROM submissions
      WHERE patient_id = ? AND encounter_id = ?
      ORDER BY submitted_at, submission_id
    `).all(patientId, encounterId)
      .map((row) => freeze(JSON.parse(row.resource_json)));
    return rows;
  }

  appendSubmission(resource) {
    const next = clone(resource);
    const tx = this.db.transaction(() => {
      this._insertSubmission.run({
        submission_id: next.submissionId || next.id,
        patient_id: next.patientId ?? null,
        encounter_id: next.encounterId ?? null,
        code: next.code ?? null,
        submitted_at: next.submittedAt || next.createdAt || null,
        resource_json: JSON.stringify(next),
      });
      return freeze(clone(next));
    });
    return tx();
  }

  submitLegacyWithActivation({ activation, submission }) {
    const nextActivation = clone(activation);
    const nextSubmission = clone(submission);
    const tx = this.db.transaction(() => {
      this._insertActivation.run({
        code: String(nextActivation.code).trim().toUpperCase(),
        resource_json: JSON.stringify(nextActivation),
        status: nextActivation.status || null,
        updated_at: nextActivation.submittedAt || nextActivation.receivedAt || new Date().toISOString(),
      });
      this._insertSubmission.run({
        submission_id: nextSubmission.submissionId || nextSubmission.id,
        patient_id: nextSubmission.patientId ?? null,
        encounter_id: nextSubmission.encounterId ?? null,
        code: nextSubmission.code ?? null,
        submitted_at: nextSubmission.submittedAt || nextSubmission.createdAt || null,
        resource_json: JSON.stringify(nextSubmission),
      });
      return {
        activation: clone(nextActivation),
        submission: freeze(clone(nextSubmission)),
      };
    });
    return tx();
  }

  appendAudit(entry) {
    const createdAt = entry.createdAt || new Date().toISOString();
    const info = this._insertAudit.run({
      action: entry.action,
      actor: entry.actor ?? null,
      role: entry.role ?? null,
      patient_id: entry.patientId ?? null,
      submission_id: entry.submissionId ?? null,
      detail_json: JSON.stringify(entry.detail || {}),
      created_at: createdAt,
    });
    return {
      id: Number(info.lastInsertRowid),
      action: entry.action,
      actor: entry.actor ?? null,
      role: entry.role ?? null,
      patientId: entry.patientId ?? null,
      submissionId: entry.submissionId ?? null,
      detail: entry.detail || {},
      createdAt,
    };
  }

  listAudits({ patientId, submissionId } = {}) {
    let sql = "SELECT id, action, actor, role, patient_id, submission_id, detail_json, created_at FROM audit_events WHERE 1=1";
    const params = [];
    if (patientId) {
      sql += " AND patient_id = ?";
      params.push(patientId);
    }
    if (submissionId) {
      sql += " AND submission_id = ?";
      params.push(submissionId);
    }
    sql += " ORDER BY id";
    return this.db.prepare(sql).all(...params).map((row) => ({
      id: row.id,
      action: row.action,
      actor: row.actor,
      role: row.role,
      patientId: row.patient_id,
      submissionId: row.submission_id,
      detail: JSON.parse(row.detail_json || "{}"),
      createdAt: row.created_at,
    }));
  }

  applyRetention({ cutoffIso, redactedAtIso }) {
    const selectExpired = this.db.prepare(`
      SELECT submission_id, resource_json FROM submissions
      WHERE submitted_at IS NOT NULL AND submitted_at <= ?
    `);
    const update = this.db.prepare(`
      UPDATE submissions SET resource_json = ? WHERE submission_id = ?
    `);
    const auditCount = this.db.prepare("SELECT COUNT(*) AS n FROM audit_events").get().n;
    const tx = this.db.transaction(() => {
      let submissionsRedacted = 0;
      for (const row of selectExpired.all(cutoffIso)) {
        const resource = JSON.parse(row.resource_json);
        if (resource.phiRedactedAt) continue;
        const redacted = {
          id: resource.id,
          submissionId: resource.submissionId || resource.id,
          patientId: resource.patientId ?? null,
          encounterId: resource.encounterId ?? null,
          schemaVersion: resource.schemaVersion,
          author: "[redacted]",
          createdAt: resource.createdAt,
          updatedAt: resource.updatedAt,
          submittedAt: resource.submittedAt,
          status: resource.status,
          version: resource.version,
          etag: resource.etag,
          code: resource.code,
          source: resource.source,
          phiRedactedAt: redactedAtIso,
          data: null,
        };
        update.run(JSON.stringify(redacted), row.submission_id);
        submissionsRedacted += 1;
      }
      return { submissionsRedacted, auditsPreserved: auditCount };
    });
    return tx();
  }
}

function createMemoryMedicalHistoryRepository(seed) {
  return new MemoryMedicalHistoryRepository(seed);
}

function createSqliteMedicalHistoryRepository(options) {
  return new SqliteMedicalHistoryRepository(options);
}

function migrateJsonToRepository({
  dataDir,
  repository,
  activationsFileName = "activation_sessions.json",
  submissionsFileName = "medical_history_submissions.json",
} = {}) {
  if (!repository) throw new TypeError("repository is required");
  const dir = dataDir || process.env.MEDICAL_HISTORY_DATA_DIR || path.join(__dirname, "data");
  const activationsPath = path.join(dir, activationsFileName);
  const submissionsPath = path.join(dir, submissionsFileName);
  const activations = readJsonFile(activationsPath, []);
  const submissions = readJsonFile(submissionsPath, []);
  assertArray(activations, "activation_sessions.json");
  assertArray(submissions, "medical_history_submissions.json");

  let activationsMigrated = 0;
  let submissionsMigrated = 0;

  const migrate = () => {
    for (const activation of activations) {
      if (!activation || typeof activation !== "object") continue;
      const existing = repository.getActivationByCode(activation.code);
      if (!existing) {
        repository.replaceActivation(activation);
        activationsMigrated += 1;
      }
    }
    const known = new Set(repository.listSubmissions().map((row) => row.id || row.submissionId));
    for (const submission of submissions) {
      if (!submission || typeof submission !== "object") continue;
      const id = submission.submissionId || submission.id;
      if (!id || known.has(id)) continue;
      repository.appendSubmission(submission);
      known.add(id);
      submissionsMigrated += 1;
    }
    return { activationsMigrated, submissionsMigrated };
  };

  if (typeof repository.db?.transaction === "function") {
    return repository.db.transaction(migrate)();
  }
  return migrate();
}

function createDefaultMedicalHistoryRepository({
  dataDir = process.env.MEDICAL_HISTORY_DATA_DIR || path.join(__dirname, "data"),
  driver = process.env.MEDICAL_HISTORY_STORE || "sqlite",
} = {}) {
  if (driver === "memory") return createMemoryMedicalHistoryRepository();
  const repository = createSqliteMedicalHistoryRepository({ dataDir });
  migrateJsonToRepository({ dataDir, repository });
  return repository;
}

module.exports = {
  createMemoryMedicalHistoryRepository,
  createSqliteMedicalHistoryRepository,
  createDefaultMedicalHistoryRepository,
  migrateJsonToRepository,
  MemoryMedicalHistoryRepository,
  SqliteMedicalHistoryRepository,
};
