// DDI-04: server-owned SQLite KB lifecycle and audit tests.
// Covers migration from bundled JSON, lifecycle transitions
// (draft -> reviewed -> active -> retired), review/audit
// persistence, the clinical activation gate (rxnorm-pending blocked),
// and transactional rollback. No native binding is required for the
// memory-backed path; a real better-sqlite3 file is exercised when
// available, gated behind the DDI_SQLITE_E2E env flag so the unit CI
// stays dependency-free.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const require = createRequire(import.meta.url);
const engine = require("../src/ddi-engine.js");
// DDI-04: validation gate tested indirectly through activate() rejections;
// the shared canonical rules live in src/kb-validator.cjs and are re-exported
// by scripts/validate-kb.mjs for the CLI.
const { createKbSqliteStore, createMemoryKbStore, migrateKbIntoStore } = require("../src/kb-sqlite.cjs");

const rxnormSeeded = (id, name, aliases = []) => ({
  id, name, aliases, rxcui: id.split(":")[1], doseSuggestions: [],
  isSourceReportDrug: false, identityStatus: "rxnorm_seeded",
});

const rxnormPending = (id, name) => ({
  id, name, aliases: [], rxcui: null, doseSuggestions: [],
  isSourceReportDrug: false, identityStatus: "pending_rxnorm_review",
});

function draftKb(version, { interactions, drugs, clinicalUse = { allowedForProduction: true, reason: "fixture" } } = {}) {
  return JSON.parse(JSON.stringify({
    schemaVersion: "1.0.0",
    version,
    status: "draft_parsed_pending_admin_review",
    generatedAt: "2026-01-01T00:00:00.000Z",
    activatedAt: null,
    clinicalUse,
    drugs: drugs || [rxnormSeeded("rxnorm:1", "drugA"), rxnormSeeded("rxnorm:2", "drugB")],
    interactions: interactions || [{
      id: "ddi-1",
      drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewedBy: null, reviewedAt: null,
      reviewStatus: "parsed_pending_review",
      parserConfidence: "medium",
      knowledgeBaseVersion: version,
    }],
    reports: [],
  }));
}

const adminPrincipal = { userId: "clinician-1", sessionId: "s-1", roles: ["ddi_admin"], expiresAt: "2099-01-01T00:00:00Z" };

// ---------------------------------------------------------------------------
// Migration
// ---------------------------------------------------------------------------

test("migrateKbIntoStore imports a bundled KB on first boot and is idempotent", async () => {
  const store = createMemoryKbStore();
  const kb = draftKb("ikb-migrate");
  await migrateKbIntoStore(store, kb);
  assert.equal((await store.list()).length, 1);
  assert.equal((await store.list())[0].version, "ikb-migrate");
  assert.equal((await store.list())[0].status, "draft_parsed_pending_admin_review");
  const loaded = await store.load("ikb-migrate");
  assert.equal(loaded.drugs.length, 2);
  assert.equal(loaded.interactions.length, 1);

  // Re-migrating the same version must NOT duplicate or overwrite reviewed work.
  await migrateKbIntoStore(store, kb);
  assert.equal((await store.list()).length, 1);
  assert.equal((await store.load("ikb-migrate")).interactions.length, 1);
});

test("server reads the bundled active-kb.json as a draft on cold boot", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "ddi-kb-"));
  try {
    const store = createMemoryKbStore({ databaseFile: path.join(tmp, "kb.sqlite") });
    const bundledKbPath = path.resolve(__dirname, "..", "data", "active-kb.json");
    const bundled = JSON.parse(fs.readFileSync(bundledKbPath, "utf8"));
    await migrateKbIntoStore(store, bundled);
    const loaded = await store.load(bundled.version);
    assert.ok(loaded);
    assert.equal(loaded.status, "draft_parsed_pending_admin_review");
    assert.equal(loaded.drugs.length, bundled.drugs.length);
    assert.equal(loaded.interactions.length, bundled.interactions.length);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

// ---------------------------------------------------------------------------
// Lifecycle transitions
// ---------------------------------------------------------------------------

test("review() applies reviewer edits, marks approved, and records attribution", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-review"));
  const result = await store.admin("review", "ikb-review", {
    interactionId: "ddi-1",
    reviewStatus: "approved",
    edits: { recommendation: "Updated do-not-coadminister.", severity: "major" },
    reviewer: "pharmacist-1",
  }, adminPrincipal);
  assert.equal(result.reviewStatus, "approved");
  assert.equal(result.recommendation, "Updated do-not-coadminister.");
  assert.equal(result.severity, "major");
  assert.equal(result.reviewedBy, "pharmacist-1");
  assert.match(result.reviewedAt, /^\d{4}-\d{2}-\d{2}T/);

  const loaded = await store.load("ikb-review");
  assert.equal(loaded.interactions[0].reviewStatus, "approved");
  assert.equal(loaded.interactions[0].reviewedBy, "pharmacist-1");
});

test("review() rejects without a non-blank reviewer identity", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-review-noauth"));
  await assert.rejects(
    () => store.admin("review", "ikb-review-noauth", {
      interactionId: "ddi-1", reviewStatus: "approved", edits: {},
    }, { ...adminPrincipal, userId: "  " }),
    /reviewer/i,
  );
});

test("review() rolls back edits when the resulting KB fails structural validation", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-review-invalid"));
  await assert.rejects(
    () => store.admin("review", "ikb-review-invalid", {
      interactionId: "ddi-1",
      reviewStatus: "approved",
      edits: { severity: "not-a-severity-value" },
      reviewer: "pharmacist-1",
    }, adminPrincipal),
  );
  const loaded = await store.load("ikb-review-invalid");
  assert.equal(loaded.interactions[0].severity, "moderate");
  assert.equal(loaded.interactions[0].reviewStatus, "parsed_pending_review");
  assert.equal(loaded.interactions[0].reviewedBy, null);
});

// ---------------------------------------------------------------------------
// Activation gate
// ---------------------------------------------------------------------------

test("activate() blocks a draft with no approved interactions", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-noapproved"));
  await assert.rejects(() => store.admin("activate", "ikb-noapproved", {}, adminPrincipal), /approved interaction/i);
  const loaded = await store.load("ikb-noapproved");
  assert.equal(loaded.status, "draft_parsed_pending_admin_review");
  assert.equal(loaded.activatedAt, null);
});

test("activate() blocks a draft whose approved interactions reference rxnorm-pending identities", async () => {
  const store = createMemoryKbStore();
  const kb = draftKb("ikb-pending", {
    drugs: [rxnormPending("rxnorm-pending:foo", "foo"), rxnormSeeded("rxnorm:2", "drugB")],
    interactions: [{
      id: "ddi-pending",
      drugAId: "rxnorm-pending:foo", drugAName: "foo",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewStatus: "approved", reviewedBy: "pharmacist-1", reviewedAt: "2026-01-01T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-pending",
    }],
  });
  await migrateKbIntoStore(store, kb);
  await assert.rejects(() => store.admin("activate", "ikb-pending", {}, adminPrincipal), /rxnorm|identity|RxNorm/i);
  assert.equal((await store.load("ikb-pending")).status, "draft_parsed_pending_admin_review");
});

test("activate() blocks a low-confidence approved interaction", async () => {
  const store = createMemoryKbStore();
  const kb = draftKb("ikb-low", {
    interactions: [{
      id: "ddi-low", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewStatus: "approved", reviewedBy: "pharmacist-1", reviewedAt: "2026-01-01T00:00:00Z",
      parserConfidence: "low", knowledgeBaseVersion: "ikb-low",
    }],
  });
  await migrateKbIntoStore(store, kb);
  await assert.rejects(() => store.admin("activate", "ikb-low", {}, adminPrincipal), /parserConfidence|low/i);
});

test("activate() blocks when clinicalUse.allowedForProduction is false", async () => {
  const store = createMemoryKbStore();
  const kb = draftKb("ikb-noclinical", {
    clinicalUse: { allowedForProduction: false, reason: "not yet" },
    interactions: [{
      id: "ddi-ok", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewStatus: "approved", reviewedBy: "pharmacist-1", reviewedAt: "2026-01-01T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-noclinical",
    }],
  });
  await migrateKbIntoStore(store, kb);
  await assert.rejects(() => store.admin("activate", "ikb-noclinical", {}, adminPrincipal), /allowedForProduction|clinical/i);
});

test("activate() promotes a clinically eligible draft to active, retiring the previous active", async () => {
  const store = createMemoryKbStore();
  // First active KB.
  const kbA = draftKb("ikb-activeA", {
    interactions: [{
      id: "ddi-a", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewStatus: "approved", reviewedBy: "p1", reviewedAt: "2026-01-01T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-activeA",
    }],
  });
  await migrateKbIntoStore(store, kbA);
  const activationA = await store.admin("activate", "ikb-activeA", {}, adminPrincipal);
  assert.match(activationA.status, /^active/);
  assert.ok(activationA.activatedAt);

  // Second draft gets activated; the first must retire.
  const kbB = draftKb("ikb-activeB", {
    drugs: [rxnormSeeded("rxnorm:1", "drugA"), rxnormSeeded("rxnorm:2", "drugB"), rxnormSeeded("rxnorm:3", "drugC")],
    interactions: [{
      id: "ddi-b", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:3", drugBName: "drugC",
      severity: "minor", mechanism: "m2", clinicalEffect: "e2",
      recommendation: "r2", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p2",
      reviewStatus: "approved", reviewedBy: "p2", reviewedAt: "2026-01-02T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-activeB",
    }],
  });
  await migrateKbIntoStore(store, kbB);
  const activationB = await store.admin("activate", "ikb-activeB", {}, adminPrincipal);
  assert.match(activationB.status, /^active/);

  const reloadedA = await store.load("ikb-activeA");
  assert.equal(reloadedA.status, "retired");
  const reloadedB = await store.load("ikb-activeB");
  assert.match(reloadedB.status, /^active/);

  const versions = await store.list();
  const active = versions.filter((row) => String(row.status).startsWith("active"));
  assert.equal(active.length, 1, "exactly one active KB at a time");
  assert.equal(active[0].version, "ikb-activeB");
});

// ---------------------------------------------------------------------------
// Retire + rollback
// ---------------------------------------------------------------------------

test("retire() moves an active KB to retired and is attributed", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-retire", {
    interactions: [{
      id: "ddi-r", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewStatus: "approved", reviewedBy: "p1", reviewedAt: "2026-01-01T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-retire",
    }],
  }));
  await store.admin("activate", "ikb-retire", {}, adminPrincipal);
  const retired = await store.admin("retire", "ikb-retire", { reason: "superseded" }, adminPrincipal);
  assert.equal(retired.status, "retired");
  const versions = await store.list();
  assert.equal(versions.find((row) => row.version === "ikb-retire").status, "retired");
  assert.equal(versions.filter((row) => String(row.status).startsWith("active")).length, 0);
});

test("rollback() restores the previously active KB but never a pending rxnorm draft", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-rollback-a", {
    interactions: [{
      id: "ddi-a", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewStatus: "approved", reviewedBy: "p1", reviewedAt: "2026-01-01T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-rollback-a",
    }],
  }));
  await store.admin("activate", "ikb-rollback-a", {}, adminPrincipal);

  await migrateKbIntoStore(store, draftKb("ikb-rollback-b", {
    interactions: [{
      id: "ddi-b", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m2", clinicalEffect: "e2",
      recommendation: "r2", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p2",
      reviewStatus: "approved", reviewedBy: "p2", reviewedAt: "2026-01-02T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-rollback-b",
    }],
  }));
  await store.admin("activate", "ikb-rollback-b", {}, adminPrincipal);
  assert.match((await store.load("ikb-rollback-a")).status, /^retired/);

  const rolled = await store.admin("rollback", "ikb-rollback-b", {}, adminPrincipal);
  assert.match(rolled.status, /^active/);
  assert.equal(rolled.version, "ikb-rollback-a");
  assert.match((await store.load("ikb-rollback-b")).status, /^retired/);
});

test("rollback() fails when there is no prior active version", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-rollback-empty", {
    interactions: [{
      id: "ddi-e", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewStatus: "approved", reviewedBy: "p1", reviewedAt: "2026-01-01T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-rollback-empty",
    }],
  }));
  await store.admin("activate", "ikb-rollback-empty", {}, adminPrincipal);
  await assert.rejects(() => store.admin("rollback", "ikb-rollback-empty", {}, adminPrincipal), /prior|previous/i);
});

// ---------------------------------------------------------------------------
// Audit persistence
// ---------------------------------------------------------------------------

test("audit() stores engine.createAuditEntry output and listAudit() returns it", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-audit", {
    interactions: [{
      id: "ddi-audit", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "contraindicated", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewStatus: "approved", reviewedBy: "p1", reviewedAt: "2026-01-01T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-audit",
    }],
  }));
  await store.admin("activate", "ikb-audit", {}, adminPrincipal);
  const loaded = await store.load("ikb-audit");
  const alert = {
    id: "alert-1", interactionId: "ddi-audit",
    interactingDrugs: ["drugA", "drugB"],
    severity: "contraindicated",
    knowledgeBaseVersion: "ikb-audit",
    sourceReportPath: "p",
  };
  const entry = engine.createAuditEntry(alert, "overridden", {
    reason: "Patient-specific override documented in chart.",
    clinician: "doc-1", patientId: "p-100", sessionCode: "ENC-42",
  });
  await store.audit(entry);
  const listed = await store.listAudit({ version: "ikb-audit" });
  assert.equal(listed.length, 1);
  assert.equal(listed[0].action, "overridden");
  assert.equal(listed[0].patientId, "p-100");
  assert.equal(listed[0].knowledgeBaseVersion, "ikb-audit");
  assert.match(listed[0].reason, /chart/);
});

test("audit() rejects an overridden entry without a rationale", async () => {
  const store = createMemoryKbStore();
  await assert.rejects(
    () => store.audit({ action: "overridden", reason: "", alertId: "x", severity: "moderate", knowledgeBaseVersion: "v1" }),
    /rationale/i,
  );
});

// ---------------------------------------------------------------------------
// Admin dispatch validation
// ---------------------------------------------------------------------------

test("admin() rejects an unknown action", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-bad-action"));
  await assert.rejects(
    () => store.admin("bogus", "ikb-bad-action", {}, adminPrincipal),
    /unknown .* admin action|invalid action/i,
  );
});

test("admin() rejects callers without the ddi_admin role", async () => {
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-no-role"));
  const noRole = { userId: "doc", sessionId: "s", roles: ["psychiatrist"], expiresAt: "2099-01-01T00:00:00Z" };
  await assert.rejects(
    () => store.admin("activate", "ikb-no-role", {}, noRole),
    /admin forbidden|forbidden|role/i,
  );
});

test("admin() rejects when the target KB version does not exist", async () => {
  const store = createMemoryKbStore();
  await assert.rejects(
    () => store.admin("activate", "no-such-version", {}, adminPrincipal),
    /not found|unknown/i,
  );
});

// ---------------------------------------------------------------------------
// Endpoint-to-end better-sqlite3 cycle (gated to avoid native-build CI needs)
// ---------------------------------------------------------------------------

test("better-sqlite3 file-backed store round-trips migrate-review-activate-audit", { skip: !process.env.DDI_SQLITE_E2E }, async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "ddi-sqlite-"));
  try {
    const store = createKbSqliteStore({ databaseFile: path.join(tmp, "kb.sqlite") });
    await migrateKbIntoStore(store, draftKb("ikb-e2e", {
      interactions: [{
        id: "ddi-e2e", drugAId: "rxnorm:1", drugAName: "drugA",
        drugBId: "rxnorm:2", drugBName: "drugB",
        severity: "moderate", mechanism: "m", clinicalEffect: "e",
        recommendation: "r", monitoring: "",
        evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
        reviewStatus: "parsed_pending_review",
        parserConfidence: "medium", knowledgeBaseVersion: "ikb-e2e",
      }],
    }));
    await store.admin("review", "ikb-e2e", {
      interactionId: "ddi-e2e", reviewStatus: "approved",
      edits: { recommendation: "ok" }, reviewer: "p1",
    }, adminPrincipal);
    const activation = await store.admin("activate", "ikb-e2e", {}, adminPrincipal);
    assert.match(activation.status, /^active/);

    const entry = engine.createAuditEntry({
      id: "a", interactionId: "ddi-e2e", interactingDrugs: ["drugA", "drugB"],
      severity: "moderate", knowledgeBaseVersion: "ikb-e2e", sourceReportPath: "p",
    }, "acknowledged", { reason: "noted" });
    await store.audit(entry);
    const audited = await store.listAudit({ version: "ikb-e2e" });
    assert.equal(audited.length, 1);

    store.close();
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

// ---------------------------------------------------------------------------
// REST adapter admin wiring (501 stub replaced)
// ---------------------------------------------------------------------------

test("REST admin routes return real results when knowledgeStore.admin is implemented", async () => {
  const { createDdiServer } = require("../src/ddi-rest-adapter.cjs");
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-rest", {
    interactions: [{
      id: "ddi-rest", drugAId: "rxnorm:1", drugAName: "drugA",
      drugBId: "rxnorm:2", drugBName: "drugB",
      severity: "moderate", mechanism: "m", clinicalEffect: "e",
      recommendation: "r", monitoring: "",
      evidenceSource: "s", evidenceExcerpt: "x", sourceReportPath: "p",
      reviewStatus: "approved", reviewedBy: "p1", reviewedAt: "2026-01-01T00:00:00Z",
      parserConfidence: "medium", knowledgeBaseVersion: "ikb-rest",
    }],
  }));
  const auth = {
    async verify(cookieHeader) {
      const token = String(cookieHeader || "").split(";").map((p) => p.trim())
        .find((p) => p.startsWith("insight_session="))?.slice("insight_session=".length);
      if (token === "admin") return adminPrincipal;
      return null;
    },
  };
  const server = createDdiServer({
    knowledgeStore: store,
    activeVersion: "ikb-rest",
    auth,
  });
  const response = await server.fetch(`http://localhost/api/ddi-checker/v1/knowledge-bases/ikb-rest/activate`, {
    method: "POST",
    headers: { cookie: "insight_session=admin", "content-type": "application/json" },
    body: JSON.stringify({}),
  });
  const body = await response.json();
  assert.equal(response.status, 200, `expected 200, got ${response.status}: ${JSON.stringify(body)}`);
  assert.match(body.status, /^active/);
});

test("REST admin routes pass principal to knowledgeStore.admin for role enforcement", async () => {
  const { createDdiServer } = require("../src/ddi-rest-adapter.cjs");
  let sawPrincipal = null;
  const store = createMemoryKbStore();
  await migrateKbIntoStore(store, draftKb("ikb-rest-principal"));
  const wrapped = {
    load: (v) => store.load(v),
    list: () => store.list(),
    audit: (e) => store.audit(e),
    listAudit: (q) => store.listAudit(q),
    admin: (action, version, body, principal) => { sawPrincipal = principal; return store.admin(action, version, body, principal); },
  };
  const auth = {
    async verify() { return adminPrincipal; },
  };
  const server = createDdiServer({ knowledgeStore: wrapped, activeVersion: "ikb-rest-principal", auth });
  await server.fetch(`http://localhost/api/ddi-checker/v1/knowledge-bases/ikb-rest-principal/review`, {
    method: "POST",
    headers: { cookie: "insight_session=admin", "content-type": "application/json" },
    body: JSON.stringify({ interactionId: "ddi-1", reviewStatus: "rejected", reviewer: "p1" }),
  });
  assert.ok(sawPrincipal, "knowledgeStore.admin must receive the verified principal");
  assert.ok(Array.isArray(sawPrincipal.roles));
  assert.ok(sawPrincipal.roles.includes("ddi_admin"));
});
