// DDI-05 — Repair identity/evidence governance.
//
// The bundled knowledge base has to satisfy identity/evidence governance:
// records cannot silently slip in ambiguous identities, conflicting
// unordered medication pairs, or missing provenance. This test pins the
// repair contract: the parser/normalization must not produce junk drug
// identities (doses, ages, clinical phrases), kg-validator must quarantine
// ambiguous/conflicting records rather than emit a sea of generated errors,
// and the KB must record source/version/freshness/evidence plus reviewer
// provenance for every active-record candidate. The duplicate browser JS KB
// artifact (data/active-kb.js) must not exist — the UI reads the canonical
// server interface.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const reportParser = require("../src/report-parser.js");
const { validateKnowledgeBase } = require("../src/kb-validator.cjs");

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const moduleRoot = path.resolve(__dirname, "..");

test("report-parser looksLikeDrugHeading rejects doses, ages, and clinical phrases that the corrupt corpus leaked in", () => {
  const junk = [
    "400mg",
    "200 mg PO qDay",
    "Initial: 20 mg PO qDay",
    "10mg",
    "1-9 years",
    "14-18 years",
    "65 years",
    "129 mg daily for 1-2 weeks before discontinuing",
    "coadministration with medications that cause fluid",
    "and renal impairment",
    "arrhythmias",
    "1 5-ag assay is not recommended as measurements of 1 5-ag are unreliable",
  ];
  for (const candidate of junk) {
    assert.equal(
      reportParser.looksLikeDrugHeading(candidate),
      false,
      `looksLikeDrugHeading must reject junk heading: ${candidate}`,
    );
  }
  assert.equal(reportParser.looksLikeDrugHeading("fluoxetine"), true);
  assert.equal(reportParser.looksLikeDrugHeading("pimozide"), true);
});

test("parseReport() does not turn malformed sections into drug identities", () => {
  const raw = `
acetaminophen (Rx)
Interactions
Contraindicated (1)
400mg
acetaminophen and 400mg both increase something. Contraindicated.
Adverse Effects
`;
  const parsed = reportParser.parseReport(raw, "Acetaminophen.txt");
  const drugBNames = parsed.interactions.map((row) => row.drugBName);
  assert.ok(!drugBNames.includes("400mg"), "a dose line must never become a drug identity");
});

test("the duplicate browser JS KB artifact has been removed — UI reads the canonical server interface", () => {
  const jsArtifact = path.join(moduleRoot, "data", "active-kb.js");
  assert.equal(
    fs.existsSync(jsArtifact),
    false,
    "data/active-kb.js is a duplicate generated KB artifact; the UI must read the server /knowledge-bases interface instead",
  );
  const html = fs.readFileSync(path.join(moduleRoot, "index.html"), "utf8");
  const app = fs.readFileSync(path.join(moduleRoot, "src", "app.js"), "utf8");
  assert.doesNotMatch(html, /src="data\/active-kb\.js"/, "index.html must not load the duplicate active-kb.js artifact");
  assert.doesNotMatch(app, /window\.DDI_ACTIVE_KB/, "app.js must not reference the removed window.DDI_ACTIVE_KB artifact");
  assert.match(app, /\/api\/ddi-checker\/v1\/knowledge-bases\/active/, "app.js must load the KB from the canonical server interface");
});

test("every unordered medication pair in the active KB is unique or explicitly versioned — conflicts are quarantined, not flattened", () => {
  const kb = JSON.parse(fs.readFileSync(path.join(moduleRoot, "data", "active-kb.json"), "utf8"));
  const activeInteractions = kb.interactions.filter((row) => row.reviewStatus === "approved");
  const pairs = new Map();
  for (const row of activeInteractions) {
    const key = [row.drugAId, row.drugBId].sort().join("::");
    if (!pairs.has(key)) pairs.set(key, []);
    pairs.get(key).push(row);
  }
  for (const [key, records] of pairs) {
    assert.equal(
      records.length,
      1,
      `unordered medication pair ${key} is duplicated in the active KB; conflicts must be quarantined, not flattened`,
    );
  }
});

test("ambiguous/unresolved identities cannot yield a definitive safe result — resolveDrug stays non-resolved", () => {
  const kb = {
    schemaVersion: "1.0.0", version: "ikb-ambig", status: "active", activatedAt: "2026-07-23T00:00:00Z",
    clinicalUse: { allowedForProduction: true },
    drugs: [
      { id: "rxnorm:1", name: "drugA", aliases: ["Shared"], identityStatus: "rxnorm_seeded" },
      { id: "rxnorm:2", name: "drugB", aliases: ["Shared"], identityStatus: "rxnorm_seeded" },
    ],
    interactions: [],
  };
  const engine = require("../src/ddi-engine.js");
  const index = engine.buildIndex(kb);
  const resolution = engine.resolveDrug("shared", index);
  assert.equal(resolution.status, "ambiguous");
  assert.ok(!resolution.drug, "an ambiguous identity must not yield a definitive drug reference");
});

test("structural validation passes on the bundled KB; clinical-active is gated on honest reviewer approval", () => {
  const kb = JSON.parse(fs.readFileSync(path.join(moduleRoot, "data", "active-kb.json"), "utf8"));
  const structural = validateKnowledgeBase(kb);
  assert.deepEqual(structural, [], `bundled KB must pass structural validation: ${structural.join("; ")}`);
  // The bundled KB ships as draft_parsed_pending_admin_review with no fabricated
  // clinical approvals (DDI-05 stop condition). Clinical-active validation must
  // reject it unless a real reviewer has approved at least oneRxNorm-resolved,
  // non-low-confidence record. This pins the governance rule, not a test-only
  // approval stamp.
  const clinical = validateKnowledgeBase(kb, { clinicalActive: true }).join("\n");
  assert.match(clinical, /at least one approved interaction/);
});

test("the bundled KB records source, version, freshness, evidence, and reviewer provenance", () => {
  const kb = JSON.parse(fs.readFileSync(path.join(moduleRoot, "data", "active-kb.json"), "utf8"));
  assert.ok(kb.source && text(kb.source.type), "kb.source.type records the source corpus");
  assert.ok(text(kb.source.version) || text(kb.version), "kb records a version/freshness identity");
  assert.ok(text(kb.normalization?.identitySystem), "kb records the identity system provenance");
  for (const row of kb.interactions.filter((r) => r.reviewStatus === "approved")) {
    assert.ok(text(row.evidenceSource), `approved interaction ${row.id} records evidenceSource provenance`);
    assert.ok(text(row.evidenceExcerpt), `approved interaction ${row.id} records evidenceExcerpt`);
    assert.ok(text(row.sourceReportPath) || text(row.sourceReportVersion), `approved interaction ${row.id} records a source report reference`);
    assert.ok(text(row.reviewedBy), `approved interaction ${row.id} records reviewedBy provenance`);
    assert.ok(text(row.reviewedAt) && !Number.isNaN(Date.parse(row.reviewedAt)), `approved interaction ${row.id} records a valid reviewedAt`);
  }
});

test("quarantine partition captures ambiguous/conflicting records instead of aborting validation", () => {
  const kb = {
    schemaVersion: "1.0.0", version: "ikb-q", status: "draft_parsed_pending_admin_review", activatedAt: null,
    clinicalUse: { allowedForProduction: false },
    normalization: { identitySystem: "RxNorm RxCUI" },
    source: { type: "fixture", version: "v1" },
    drugs: [
      { id: "rxnorm:1", name: "drugA", aliases: ["Shared"], identityStatus: "rxnorm_seeded" },
      { id: "rxnorm:2", name: "drugB", aliases: ["Shared"], identityStatus: "rxnorm_seeded" },
    ],
    interactions: [
      {
        id: "ddi-conf-1", drugAId: "rxnorm:1", drugBId: "rxnorm:2",
        severity: "major", mechanism: "M1", clinicalEffect: "E1", recommendation: "R1", monitoring: "",
        evidenceSource: "S1", evidenceExcerpt: "X1", sourceReportPath: "p1",
        reviewedBy: null, reviewedAt: null, reviewStatus: "parsed_pending_review",
        parserConfidence: "medium", knowledgeBaseVersion: "ikb-q",
      },
      {
        id: "ddi-conf-2", drugAId: "rxnorm:2", drugBId: "rxnorm:1",
        severity: "moderate", mechanism: "M2", clinicalEffect: "E2", recommendation: "R2", monitoring: "",
        evidenceSource: "S2", evidenceExcerpt: "X2", sourceReportPath: "p2",
        reviewedBy: null, reviewedAt: null, reviewStatus: "parsed_pending_review",
        parserConfidence: "medium", knowledgeBaseVersion: "ikb-q",
      },
    ],
  };
  const report = validateKnowledgeBase(kb, { returnPartition: true });
  assert.ok(Array.isArray(report.quarantinedInteractions), "validateKnowledgeBase returns a quarantine partition");
  assert.ok(
    report.quarantinedInteractions.some((q) => q.reason === "conflicting_pair"),
    "conflicting unordered pair records are quarantined with a reason",
  );
  assert.ok(
    report.quarantinedIdentities.some((q) => q.reason === "ambiguous_identity"),
    "ambiguous alias/canonical collisions across IDs are quarantined",
  );
  const pairRows = report.interactions.filter((row) => [row.drugAId, row.drugBId].sort().join("::") === "rxnorm:1::rxnorm:2");
  assert.equal(pairRows.length, 1, "one representative record survives for each quarantined pair");
});

function text(v) { return typeof v === "string" && v.trim().length > 0; }
