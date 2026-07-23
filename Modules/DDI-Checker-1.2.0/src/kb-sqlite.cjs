// DDI-04: server-owned KB lifecycle and audit store.
//
// Replaces the browser-side client KB state with a server-authoritative
// store. Two concrete adapters share the same public surface:
//   - createMemoryKbStore(): in-process Map-backed store used by tests
//     and any deployment without a persistent filesystem. No native deps.
//   - createKbSqliteStore({ databaseFile }): better-sqlite3-backed store
//     used by src/server.mjs in production. WAL mode, foreign keys ON,
//     per-mutation transactions for rollback.
//
// Lifecycle is immutable and attributable:
//   draft_parsed_pending_admin_review -> reviewed -> active -> retired
// Each transition requires a non-blank reviewer identity (the verified
// principal). Activation is gated by scripts/validate-kb.mjs clinical
// mode so rxnorm-pending identities or low-confidence approved records
// can never become silently production-active.
//
// Audit entries produced by ddi-engine.createAuditEntry() land in the
// kb_audit_entries table for durable attribution; overrides without a
// rationale are rejected (the engine also enforces this, but the store
// defends in depth).
"use strict";

const fs = require("node:fs");
const path = require("node:path");

const { validateKnowledgeBase } = require("./kb-validator.cjs");

const REVIEW_FIELDS = new Set([
  "severity", "mechanism", "clinicalEffect", "recommendation", "monitoring",
  "evidenceSource", "evidenceExcerpt", "sourceReportPath",
]);
const ADMIN_ACTIONS = new Set(["review", "activate", "retire", "rollback"]);

function clone(value) {
  return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
}

function nowIso() {
  return new Date().toISOString();
}

function ensureReviewer(principal, explicitReviewer) {
  const reviewer = typeof explicitReviewer === "string" && explicitReviewer.trim()
    ? explicitReviewer.trim()
    : (principal && typeof principal.userId === "string" ? principal.userId.trim() : "");
  if (!reviewer) throw new Error("Attributable reviewer identity is required for lifecycle mutations.");
  return reviewer;
}

function requireAdmin(principal) {
  if (!principal || !Array.isArray(principal.roles) || !principal.roles.includes("ddi_admin")) {
    const error = new Error("ddi_admin role is required for knowledge-base administration.");
    error.code = "FORBIDDEN";
    throw error;
  }
}

function applyReviewEdits(interaction, edits) {
  const next = { ...interaction };
  for (const [field, value] of Object.entries(edits || {})) {
    if (!REVIEW_FIELDS.has(field)) continue;
    if (typeof value !== "string") continue;
    next[field] = value;
  }
  return next;
}

function clinicalActivationErrors(kb) {
  return validateKnowledgeBase(kb, { clinicalActive: true });
}

function findInteraction(kb, interactionId) {
  const match = kb.interactions.find((row) => row.id === interactionId);
  if (!match) {
    const error = new Error(`interaction ${interactionId} not found in ${kb.version}`);
    error.code = "INTERACTION_NOT_FOUND";
    throw error;
  }
  return match;
}

// ---------------------------------------------------------------------------
// Memory adapter (no native deps; used by the unit test suite and any
// ephemeral deployment that does not need durable persistence).
// ---------------------------------------------------------------------------

class MemoryKbStore {
  constructor() {
    this._kbs = new Map();        // version -> KB object
    this._previousActive = null;  // version string retained for rollback
    this._audits = [];
  }

  async load(version) {
    if (!version) return null;
    return this._kbs.has(version) ? clone(this._kbs.get(version)) : null;
  }

  async list() {
    return [...this._kbs.values()].map((kb) => ({
      version: kb.version, status: kb.status, activatedAt: kb.activatedAt || null,
    }));
  }

  async admin(action, version, body = {}, principal) {
    requireAdmin(principal);
    if (!ADMIN_ACTIONS.has(action)) {
      const error = new Error(`Unknown knowledge-base admin action: ${action}`);
      error.code = "INVALID_ACTION";
      throw error;
    }
    const kb = this._kbs.get(version);
    if (!kb) {
      const error = new Error(`Knowledge-base version ${version} not found.`);
      error.code = "KNOWLEDGE_BASE_NOT_FOUND";
      throw error;
    }
    if (action === "review") return this._review(kb, body, principal);
    if (action === "activate") return this._activate(kb, principal);
    if (action === "retire") return this._retire(kb, body, principal);
    if (action === "rollback") return this._rollback(kb, principal);
  }

  _review(kb, body, principal) {
    const reviewer = ensureReviewer(principal, body.reviewer);
    const target = findInteraction(kb, body.interactionId);
    const reviewStatus = body.reviewStatus || "approved";
    if (!["approved", "rejected", "edited_pending_review"].includes(reviewStatus)) {
      throw new Error(`Invalid reviewStatus for review(): ${reviewStatus}`);
    }
    const candidate = applyReviewEdits(target, body.edits);
    candidate.reviewStatus = reviewStatus;
    candidate.reviewedBy = reviewer;
    const reviewedAt = typeof body.reviewedAt === "string" && body.reviewedAt ? body.reviewedAt : nowIso();
    candidate.reviewedAt = reviewedAt;

    const candidateKb = clone(kb);
    const idx = candidateKb.interactions.findIndex((row) => row.id === target.id);
    candidateKb.interactions[idx] = candidate;

    const errors = validateKnowledgeBase(candidateKb);
    if (errors.length) {
      const error = new Error(`Review rejected: resulting KB failed validation: ${errors.join("; ")}`);
      error.code = "INVALID_RESULT";
      throw error;
    }

    this._kbs.set(kb.version, candidateKb);
    return clone(candidate);
  }

  _activate(kb, principal) {
    ensureReviewer(principal);
    const candidate = clone(kb);
    candidate.status = "active";
    candidate.activatedAt = nowIso();
    // Activation must NOT silently flip clinicalUse.allowedForProduction —
    // the clinical gate (validate-kb.mjs) requires the reviewer to have
    // set it to true before activation; otherwise activation is blocked.
    // We do not mutate it here; the gate enforces it.

    const errors = clinicalActivationErrors(candidate);
    if (errors.length) {
      const error = new Error(`Activation blocked by clinical gate: ${errors.join("; ")}`);
      error.code = "ACTIVATION_GATE";
      throw error;
    }

    const previousActive = [...this._kbs.values()].find((row) => String(row.status).startsWith("active"));
    if (previousActive && previousActive.version !== candidate.version) {
      previousActive.status = "retired";
      this._kbs.set(previousActive.version, clone(previousActive));
      this._previousActive = previousActive.version;
    } else if (!previousActive) {
      this._previousActive = null;
    }

    this._kbs.set(candidate.version, candidate);
    return clone({ ...candidate, interactions: undefined, drugs: undefined });
  }

  _retire(kb, body, principal) {
    ensureReviewer(principal);
    if (!String(kb.status).startsWith("active")) {
      throw new Error(`Only an active knowledge-base can be retired (current: ${kb.status}).`);
    }
    const next = clone(kb);
    next.status = "retired";
    this._kbs.set(kb.version, next);
    return { version: next.version, status: next.status, reason: (body && body.reason) || null, retiredBy: principal && principal.userId };
  }

  _rollback(kb, principal) {
    ensureReviewer(principal);
    if (!String(kb.status).startsWith("active")) {
      throw new Error(`Rollback requires the current version to be active (current: ${kb.status}).`);
    }
    const target = this._previousActive && this._kbs.get(this._previousActive);
    if (!target) {
      throw new Error("No prior active knowledge-base version is available to roll back to.");
    }
    const restored = clone(target);
    restored.status = "active";
    restored.activatedAt = restored.activatedAt || nowIso();
    const retiredCurrent = clone(kb);
    retiredCurrent.status = "retired";
    this._kbs.set(restored.version, restored);
    this._kbs.set(retiredCurrent.version, retiredCurrent);
    this._previousActive = retiredCurrent.version;
    return clone({ ...restored, interactions: undefined, drugs: undefined });
  }

  async audit(entry) {
    if (!entry || typeof entry !== "object") throw new Error("audit entry must be an object");
    if (entry.action === "overridden" && (typeof entry.reason !== "string" || !entry.reason.trim())) {
      throw new Error("Audit rationale is required for overridden alerts.");
    }
    this._audits.push(clone(entry));
  }

  async listAudit({ version, limit } = {}) {
    let rows = this._audits.slice();
    if (version) rows = rows.filter((row) => row.knowledgeBaseVersion === version);
    if (typeof limit === "number" && limit > 0) rows = rows.slice(0, limit);
    return rows;
  }

  close() { /* no-op */ }
}

// ---------------------------------------------------------------------------
// SQLite adapter (better-sqlite3). Mirrors the Medical-History-1.0.0 pattern:
// WAL mode, foreign keys ON, JSON blobs for mutable resources, prepared
// statements, transaction() wrappers for atomic mutations.
// ---------------------------------------------------------------------------

class SqliteKbStore {
  constructor({ dataDir = null, databaseFile } = {}) {
    if (!databaseFile) throw new Error("createKbSqliteStore requires databaseFile");
    if (dataDir) fs.mkdirSync(dataDir, { recursive: true });
    const Database = require("better-sqlite3");
    this.db = new Database(databaseFile);
    this.db.pragma("journal_mode = WAL");
    this.db.pragma("foreign_keys = ON");
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS knowledge_bases (
        version TEXT PRIMARY KEY,
        schema_version TEXT NOT NULL,
        status TEXT NOT NULL,
        generated_at TEXT,
        activated_at TEXT,
        clinical_use_json TEXT NOT NULL,
        source_json TEXT,
        normalization_json TEXT,
        previous_active TEXT
      );
      CREATE TABLE IF NOT EXISTS kb_drugs (
        kb_version TEXT NOT NULL,
        drug_id TEXT NOT NULL,
        name TEXT NOT NULL,
        resource_json TEXT NOT NULL,
        PRIMARY KEY (kb_version, drug_id),
        FOREIGN KEY (kb_version) REFERENCES knowledge_bases(version) ON DELETE CASCADE
      );
      CREATE TABLE IF NOT EXISTS kb_interactions (
        kb_version TEXT NOT NULL,
        interaction_id TEXT NOT NULL,
        drug_a_id TEXT NOT NULL,
        drug_b_id TEXT NOT NULL,
        severity TEXT,
        review_status TEXT NOT NULL,
        reviewed_by TEXT,
        reviewed_at TEXT,
        parser_confidence TEXT,
        resource_json TEXT NOT NULL,
        PRIMARY KEY (kb_version, interaction_id),
        FOREIGN KEY (kb_version) REFERENCES knowledge_bases(version) ON DELETE CASCADE
      );
      CREATE INDEX IF NOT EXISTS idx_kb_interactions_status
        ON kb_interactions(kb_version, review_status);
      CREATE TABLE IF NOT EXISTS kb_reports (
        kb_version TEXT NOT NULL,
        report_path TEXT NOT NULL,
        resource_json TEXT,
        PRIMARY KEY (kb_version, report_path),
        FOREIGN KEY (kb_version) REFERENCES knowledge_bases(version) ON DELETE CASCADE
      );
      CREATE TABLE IF NOT EXISTS kb_audit_entries (
        id TEXT PRIMARY KEY,
        alert_id TEXT,
        action TEXT NOT NULL,
        reason TEXT,
        clinician TEXT,
        patient_id TEXT,
        session_code TEXT,
        interaction_id TEXT,
        interacting_drugs_json TEXT,
        severity TEXT,
        knowledge_base_version TEXT,
        source_report_path TEXT,
        created_at TEXT NOT NULL
      );
      CREATE INDEX IF NOT EXISTS idx_kb_audit_version
        ON kb_audit_entries(knowledge_base_version, created_at);
    `);

    this._insertKb = this.db.prepare(`
      INSERT INTO knowledge_bases
        (version, schema_version, status, generated_at, activated_at, clinical_use_json, source_json, normalization_json, previous_active)
      VALUES
        (@version, @schema_version, @status, @generated_at, @activated_at, @clinical_use_json, @source_json, @normalization_json, @previous_active)
      ON CONFLICT(version) DO UPDATE SET
        status = excluded.status,
        activated_at = excluded.activated_at,
        clinical_use_json = excluded.clinical_use_json,
        previous_active = excluded.previous_active
    `);
    this._deleteDrugs = this.db.prepare("DELETE FROM kb_drugs WHERE kb_version = ?");
    this._deleteInteractions = this.db.prepare("DELETE FROM kb_interactions WHERE kb_version = ?");
    this._deleteReports = this.db.prepare("DELETE FROM kb_reports WHERE kb_version = ?");
    this._insertDrug = this.db.prepare(`
      INSERT INTO kb_drugs (kb_version, drug_id, name, resource_json)
      VALUES (@kb_version, @drug_id, @name, @resource_json)
    `);
    this._insertInteraction = this.db.prepare(`
      INSERT INTO kb_interactions
        (kb_version, interaction_id, drug_a_id, drug_b_id, severity,
         review_status, reviewed_by, reviewed_at, parser_confidence, resource_json)
      VALUES
        (@kb_version, @interaction_id, @drug_a_id, @drug_b_id, @severity,
         @review_status, @reviewed_by, @reviewed_at, @parser_confidence, @resource_json)
      ON CONFLICT(kb_version, interaction_id) DO UPDATE SET
        drug_a_id = excluded.drug_a_id,
        drug_b_id = excluded.drug_b_id,
        severity = excluded.severity,
        review_status = excluded.review_status,
        reviewed_by = excluded.reviewed_by,
        reviewed_at = excluded.reviewed_at,
        parser_confidence = excluded.parser_confidence,
        resource_json = excluded.resource_json
    `);
    this._insertReport = this.db.prepare(`
      INSERT INTO kb_reports (kb_version, report_path, resource_json)
      VALUES (@kb_version, @report_path, @resource_json)
      ON CONFLICT(kb_version, report_path) DO UPDATE SET
        resource_json = excluded.resource_json
    `);
    this._insertAudit = this.db.prepare(`
      INSERT INTO kb_audit_entries
        (id, alert_id, action, reason, clinician, patient_id, session_code,
         interaction_id, interacting_drugs_json, severity, knowledge_base_version,
         source_report_path, created_at)
      VALUES
        (@id, @alert_id, @action, @reason, @clinician, @patient_id, @session_code,
         @interaction_id, @interacting_drugs_json, @severity, @knowledge_base_version,
         @source_report_path, @created_at)
    `);
  }

  close() {
    if (this.db) this.db.close();
  }

  // ..................... read accessors ..................................

  async load(version) {
    if (!version) return null;
    const row = this.db.prepare("SELECT * FROM knowledge_bases WHERE version = ?").get(version);
    if (!row) return null;
    return this._assembleKb(row);
  }

  async list() {
    return this.db.prepare("SELECT version, status, activated_at AS activatedAt FROM knowledge_bases ORDER BY version")
      .all()
      .map((row) => ({ version: row.version, status: row.status, activatedAt: row.activatedAt || null }));
  }

  _assembleKb(row) {
    const drugs = this.db.prepare("SELECT resource_json FROM kb_drugs WHERE kb_version = ? ORDER BY drug_id").all(row.version)
      .map((r) => JSON.parse(r.resource_json));
    const interactions = this.db.prepare("SELECT resource_json FROM kb_interactions WHERE kb_version = ? ORDER BY interaction_id").all(row.version)
      .map((r) => JSON.parse(r.resource_json));
    const reports = this.db.prepare("SELECT resource_json FROM kb_reports WHERE kb_version = ? ORDER BY report_path").all(row.version)
      .map((r) => JSON.parse(r.resource_json));
    const clinicalUse = row.clinical_use_json ? JSON.parse(row.clinical_use_json) : {};
    const source = row.source_json ? JSON.parse(row.source_json) : null;
    const normalization = row.normalization_json ? JSON.parse(row.normalization_json) : null;
    return {
      schemaVersion: row.schema_version,
      version: row.version,
      status: row.status,
      generatedAt: row.generated_at || null,
      activatedAt: row.activated_at || null,
      clinicalUse,
      ...(source ? { source } : {}),
      ...(normalization ? { normalization } : {}),
      drugs,
      interactions,
      reports,
    };
  }

  // ..................... writers ..........................................

  _writeKbTx(kb, { previousActive = null } = {}) {
    const write = this.db.transaction(() => {
      this._insertKb.run({
        version: kb.version,
        schema_version: kb.schemaVersion || "",
        status: kb.status,
        generated_at: kb.generatedAt || null,
        activated_at: kb.activatedAt || null,
        clinical_use_json: JSON.stringify(kb.clinicalUse || {}),
        source_json: kb.source ? JSON.stringify(kb.source) : null,
        normalization_json: kb.normalization ? JSON.stringify(kb.normalization) : null,
        previous_active: previousActive,
      });
      this._deleteDrugs.run(kb.version);
      for (const drug of kb.drugs || []) {
        this._insertDrug.run({
          kb_version: kb.version, drug_id: drug.id, name: drug.name,
          resource_json: JSON.stringify(drug),
        });
      }
      this._deleteInteractions.run(kb.version);
      for (const interaction of kb.interactions || []) {
        this._insertInteraction.run({
          kb_version: kb.version,
          interaction_id: interaction.id,
          drug_a_id: interaction.drugAId,
          drug_b_id: interaction.drugBId,
          severity: interaction.severity,
          review_status: interaction.reviewStatus,
          reviewed_by: interaction.reviewedBy || null,
          reviewed_at: interaction.reviewedAt || null,
          parser_confidence: interaction.parserConfidence || null,
          resource_json: JSON.stringify(interaction),
        });
      }
      this._deleteReports.run(kb.version);
      for (const report of kb.reports || []) {
        this._insertReport.run({
          kb_version: kb.version,
          report_path: report.path || report.path === "" ? report.path : JSON.stringify(report),
          resource_json: JSON.stringify(report),
        });
      }
    });
    write();
  }

  async admin(action, version, body = {}, principal) {
    requireAdmin(principal);
    if (!ADMIN_ACTIONS.has(action)) {
      const error = new Error(`Unknown knowledge-base admin action: ${action}`);
      error.code = "INVALID_ACTION";
      throw error;
    }
    const row = this.db.prepare("SELECT * FROM knowledge_bases WHERE version = ?").get(version);
    if (!row) {
      const error = new Error(`Knowledge-base version ${version} not found.`);
      error.code = "KNOWLEDGE_BASE_NOT_FOUND";
      throw error;
    }
    const kb = this._assembleKb(row);
    if (action === "review") return this._review(kb, body, principal);
    if (action === "activate") return this._activate(kb, row, principal);
    if (action === "retire") return this._retire(kb, body, principal);
    if (action === "rollback") return this._rollback(kb, row, principal);
  }

  _review(kb, body, principal) {
    const reviewer = ensureReviewer(principal, body.reviewer);
    const target = findInteraction(kb, body.interactionId);
    const reviewStatus = body.reviewStatus || "approved";
    if (!["approved", "rejected", "edited_pending_review"].includes(reviewStatus)) {
      throw new Error(`Invalid reviewStatus for review(): ${reviewStatus}`);
    }
    const candidate = applyReviewEdits(target, body.edits);
    candidate.reviewStatus = reviewStatus;
    candidate.reviewedBy = reviewer;
    candidate.reviewedAt = (typeof body.reviewedAt === "string" && body.reviewedAt) ? body.reviewedAt : nowIso();

    const candidateKb = clone(kb);
    const idx = candidateKb.interactions.findIndex((row) => row.id === target.id);
    candidateKb.interactions[idx] = candidate;

    const errors = validateKnowledgeBase(candidateKb);
    if (errors.length) {
      const error = new Error(`Review rejected: resulting KB failed validation: ${errors.join("; ")}`);
      error.code = "INVALID_RESULT";
      throw error;
    }

    const write = this.db.transaction(() => {
      this._insertInteraction.run({
        kb_version: candidateKb.version,
        interaction_id: candidate.id,
        drug_a_id: candidate.drugAId,
        drug_b_id: candidate.drugBId,
        severity: candidate.severity,
        review_status: candidate.reviewStatus,
        reviewed_by: candidate.reviewedBy,
        reviewed_at: candidate.reviewedAt,
        parser_confidence: candidate.parserConfidence || null,
        resource_json: JSON.stringify(candidate),
      });
      this._insertKb.run({
        version: candidateKb.version,
        schema_version: candidateKb.schemaVersion || "",
        status: candidateKb.status,
        generated_at: candidateKb.generatedAt || null,
        activated_at: candidateKb.activatedAt || null,
        clinical_use_json: JSON.stringify(candidateKb.clinicalUse || {}),
        source_json: candidateKb.source ? JSON.stringify(candidateKb.source) : null,
        normalization_json: candidateKb.normalization ? JSON.stringify(candidateKb.normalization) : null,
        previous_active: null,
      });
    });
    write();
    return clone(candidate);
  }

  _activate(kb, currentRow, principal) {
    ensureReviewer(principal);
    const candidate = clone(kb);
    candidate.status = "active";
    candidate.activatedAt = nowIso();
    // Activation must NOT silently flip clinicalUse.allowedForProduction —
    // the clinical gate (kb-validator.cjs) requires the reviewer to have
    // set it to true before activation; otherwise activation is blocked.
    const errors = clinicalActivationErrors(candidate);
    if (errors.length) {
      const error = new Error(`Activation blocked by clinical gate: ${errors.join("; ")}`);
      error.code = "ACTIVATION_GATE";
      throw error;
    }

    const previousRow = this.db.prepare(
      "SELECT * FROM knowledge_bases WHERE status LIKE 'active%' AND version != ?",
    ).get(candidate.version);

    const write = this.db.transaction(() => {
      if (previousRow) {
        this.db.prepare(
          "UPDATE knowledge_bases SET status = 'retired' WHERE version = ?",
        ).run(previousRow.version);
      }
      this._writeKbTx(candidate, { previousActive: previousRow ? previousRow.version : null });
    });
    try {
      write();
    } catch (err) {
      if (currentRow) {
        this.db.prepare("UPDATE knowledge_bases SET status = ?, activated_at = ? WHERE version = ?")
          .run(currentRow.status, currentRow.activated_at, currentRow.version);
      }
      throw err;
    }

    return clone({ ...candidate, interactions: undefined, drugs: undefined });
  }

  _retire(kb, body, principal) {
    ensureReviewer(principal);
    if (!String(kb.status).startsWith("active")) {
      throw new Error(`Only an active knowledge-base can be retired (current: ${kb.status}).`);
    }
    const write = this.db.transaction(() => {
      this.db.prepare("UPDATE knowledge_bases SET status = 'retired' WHERE version = ?")
        .run(kb.version);
    });
    write();
    return {
      version: kb.version,
      status: "retired",
      reason: (body && body.reason) || null,
      retiredBy: principal && principal.userId,
    };
  }

  _rollback(kb, currentRow, principal) {
    ensureReviewer(principal);
    if (!String(kb.status).startsWith("active")) {
      throw new Error(`Rollback requires the current version to be active (current: ${kb.status}).`);
    }
    const previousVersion = currentRow.previous_active;
    const previousRow = previousVersion
      ? this.db.prepare("SELECT * FROM knowledge_bases WHERE version = ?").get(previousVersion)
      : null;
    if (!previousRow || !String(previousRow.status).startsWith("retired")) {
      throw new Error("No prior active knowledge-base version is available to roll back to.");
    }
    const write = this.db.transaction(() => {
      this.db.prepare("UPDATE knowledge_bases SET status = 'active' WHERE version = ?")
        .run(previousRow.version);
      this.db.prepare("UPDATE knowledge_bases SET status = 'retired', previous_active = ? WHERE version = ?")
        .run(previousRow.version, kb.version);
    });
    write();
    const restored = this._assembleKb(
      this.db.prepare("SELECT * FROM knowledge_bases WHERE version = ?").get(previousRow.version),
    );
    return clone({ ...restored, interactions: undefined, drugs: undefined });
  }

  async audit(entry) {
    if (!entry || typeof entry !== "object") throw new Error("audit entry must be an object");
    if (entry.action === "overridden" && (typeof entry.reason !== "string" || !entry.reason.trim())) {
      throw new Error("Audit rationale is required for overridden alerts.");
    }
    this._insertAudit.run({
      id: entry.id || `audit-${Date.now()}-${Math.random().toString(16).slice(2)}`,
      alert_id: entry.alertId || null,
      action: entry.action,
      reason: entry.reason || "",
      clinician: entry.clinician || "",
      patient_id: entry.patientId || "",
      session_code: entry.sessionCode || "",
      interaction_id: entry.interactionId || null,
      interacting_drugs_json: Array.isArray(entry.interactingDrugs) ? JSON.stringify(entry.interactingDrugs) : null,
      severity: entry.severity || null,
      knowledge_base_version: entry.knowledgeBaseVersion || null,
      source_report_path: entry.sourceReportPath || "",
      created_at: entry.createdAt || nowIso(),
    });
  }

  async listAudit({ version, limit } = {}) {
    let sql = "SELECT * FROM kb_audit_entries";
    const params = [];
    if (version) {
      sql += " WHERE knowledge_base_version = ?";
      params.push(version);
    }
    sql += " ORDER BY created_at ASC";
    if (typeof limit === "number" && limit > 0) {
      sql += " LIMIT ?";
      params.push(limit);
    }
    return this.db.prepare(sql).all(...params).map((row) => ({
      id: row.id,
      alertId: row.alert_id,
      action: row.action,
      reason: row.reason,
      clinician: row.clinician,
      patientId: row.patient_id,
      sessionCode: row.session_code,
      interactionId: row.interaction_id,
      interactingDrugs: row.interacting_drugs_json ? JSON.parse(row.interacting_drugs_json) : [],
      severity: row.severity,
      knowledgeBaseVersion: row.knowledge_base_version,
      sourceReportPath: row.source_report_path,
      createdAt: row.created_at,
    }));
  }
}

// ---------------------------------------------------------------------------
// Migration: import a bundled KB object into the store on first boot.
// Idempotent — a re-migration of an existing version is a no-op so
// reviewer/activation work is never clobbered by a careless restart.
// ---------------------------------------------------------------------------

async function migrateKbIntoStore(store, kb) {
  if (!kb || !kb.version) throw new Error("migrateKbIntoStore requires a KB object with a version");
  const existing = await store.load(kb.version);
  if (existing) return { migrated: false, version: kb.version, reason: "already imported" };

  // store into the underlying backing (memory map or sqlite) bypassing admin,
  // because a fresh draft is not yet an attributable reviewer transition.
  if (store instanceof MemoryKbStore) {
    store._kbs.set(kb.version, clone(kb));
  } else if (store._writeKbTx) {
    store._writeKbTx(clone(kb), { previousActive: null });
  } else {
    throw new Error("Unsupported knowledge store for migration");
  }
  return { migrated: true, version: kb.version };
}

module.exports = {
  createMemoryKbStore: () => new MemoryKbStore(),
  createKbSqliteStore: (options = {}) => new SqliteKbStore(options),
  migrateKbIntoStore,
};
