import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

// DDI-03 — One authoritative engine.
//
// CLI ingestion (scripts/ingest.mjs), the browser UI (src/app.js via
// src/ddi-engine.js), and the REST seam (src/ddi-rest-adapter.cjs) must all
// invoke the same domain implementation for parsing a drug report, deriving
// severity, inferring mechanism / recommendation / monitoring, and resolving
// drug identity. This file pins that contract: whenever the adapters can be
// exercised against the same fixture, they must agree, and the adapter code
// must not re-implement parse / severity / inference helpers.

const require = createRequire(import.meta.url);
const engine = require("../src/ddi-engine.js");
const reportParser = require("../src/report-parser.js");

const here = path.dirname(fileURLToPath(import.meta.url));
const repoScripts = path.resolve(here, "..", "scripts");
const fixtureDir = path.join(here, "fixtures", "reports");

const REPORT = `
fluoxetine (Rx)
Brand and Other Names: Prozac
Dosage Forms & Strengths
capsule
10mg
20mg
Major Depressive Disorder
Initial: 20 mg PO qDay
Interactions
Contraindicated (1)

pimozide
fluoxetine and pimozide both increase QTc interval. Contraindicated.

Serious (1)

amitriptyline
fluoxetine will increase the level or effect of amitriptyline by affecting hepatic enzyme CYP2C19 metabolism. Avoid or Use Alternate Drug.

Adverse Effects
`;

const ENGINE_FUNCTIONS = [
  "normalizeName",
  "hashString",
  "pairKey",
  "buildIndex",
  "resolveDrug",
  "suggestDrugs",
  "checkInteractions",
  "createAuditEntry",
  "parseReportText",
  "extractDoseSuggestions",
  "isInteractionEligible"
];
const ENGINE_VALUES = ["SEVERITY_ORDER", "DISPLAY_SEVERITY"];

test("the engine exposes the single set of parsing, severity, and inference entrypoints the adapters depend on", () => {
  // These names are the authoritative surface. Adapters MUST call these, never
  // re-implement them. Asserting their presence keeps accidental re-derivation
  // visible.
  for (const name of ENGINE_FUNCTIONS) {
    assert.equal(typeof engine[name], "function", `engine.${name} must stay exported`);
  }
  for (const name of ENGINE_VALUES) {
    assert.ok(engine[name] && typeof engine[name] === "object", `engine.${name} must stay exported as a value`);
  }
  for (const name of ["PARSER_VERSION", "parseReport", "extractDoseSuggestions", "normalizeDrugName"]) {
    assert.ok(name in reportParser, `reportParser.${name} must stay exported`);
  }
});

test("the engine carries the only severity ordering and display labels; severity inference routes through report-parser", () => {
  // Severity vocabulary lives in the engine; report-parser maps section
  // headings onto it. Adapters must not declare their own severity sets.
  assert.deepEqual(engine.SEVERITY_ORDER, {
    contraindicated: 0,
    major: 1,
    moderate: 2,
    minor: 3,
    unknown: 4
  });
  assert.deepEqual(engine.DISPLAY_SEVERITY, {
    contraindicated: "Contraindicated",
    major: "Major",
    moderate: "Moderate",
    minor: "Minor",
    unknown: "Unknown"
  });

  const parsed = reportParser.parseReport(REPORT, "Fluoxetine.txt");
  const severities = parsed.interactions.map((row) => row.severity).sort();
  assert.deepEqual(severities, ["contraindicated", "major"]);
  // Mechanism / recommendation / monitoring are inferred by the parser, not by
  // adapter-side code; confirm the QTc inference path is exercised.
  const pimozide = parsed.interactions.find((row) => row.drugBName === "pimozide");
  assert.equal(pimozide.mechanism, "QTc prolongation / torsades risk");
  assert.match(pimozide.recommendation, /Do not coadminister/);
  assert.match(pimozide.monitoring, /ECG\/QTc/);
});

test("browser-upload adapter and CLI ingestion adapter both derive interactions through the same engine parseReportText", async () => {
  // Browser (app.js) calls engine.parseReportText for uploaded reports. The
  // console CLI must build interactions through the SAME engine routine for
  // its parsing path — i.e. it has to delegate rather than re-implement a
  // second parser. The cliParseReport() helper below reproduces how the
  // CLI adapter converts an engine-parse into KB rows; both adapters are
  // therefore identical for the parser-input portion of the output.
  const cli = await import("../scripts/ingest.mjs");

  const browserParsed = engine.parseReportText(REPORT, "Fluoxetine.txt", { version: "ikb-ddi03" });
  // CLI adapter: it ingests a single report through its own parseReport shim,
  // which must now funnel severity/inference/aliases/doseSuggestions through
  // the engine rather than duplicate them. Compare the parser-derived fields
  // only (CLI stamps its own ids / reviewStatus / evidenceSource for the
  // production KB — those are CLI-policy, not parser behavior).
  const drugs = new Map();
  const cliParsed = cli.parseReport(REPORT, "Fluoxetine.txt", { drugs, version: "ikb-ddi03" });

  const browserInteractions = browserParsed.interactions.map((row) => ({
    drugBName: row.drugBName,
    severity: row.severity,
    mechanism: row.mechanism,
    clinicalEffect: row.clinicalEffect,
    recommendation: row.recommendation,
    monitoring: row.monitoring,
    evidenceExcerpt: row.evidenceExcerpt,
    sequence: row.sequence
  }));
  const cliInteractions = cliParsed.interactions.map((row) => ({
    drugBName: row.drugBName,
    severity: row.severity,
    mechanism: row.mechanism,
    clinicalEffect: row.clinicalEffect,
    recommendation: row.recommendation,
    monitoring: row.monitoring,
    evidenceExcerpt: row.evidenceExcerpt,
    sequence: row.sequence
  }));

  assert.equal(browserInteractions.length, cliInteractions.length);
  assert.deepEqual(browserInteractions, cliInteractions);
});

test("REST interaction checks reuse the same checkInteractions engine the browser uses", async () => {
  const { createDdiServer } = require("../src/ddi-rest-adapter.cjs");
  const fixtureKb = {
    version: "ikb-ddi03",
    status: "draft_parsed_pending_admin_review",
    drugs: [
      { id: "rxnorm:4493", name: "fluoxetine", aliases: ["Prozac"] },
      { id: "rxnorm:8332", name: "pimozide", aliases: [] }
    ],
    interactions: [
      {
        id: "ddi-1",
        drugAId: "rxnorm:4493",
        drugAName: "fluoxetine",
        drugBId: "rxnorm:8332",
        drugBName: "pimozide",
        severity: "contraindicated",
        mechanism: "QTc prolongation",
        clinicalEffect: "fluoxetine and pimozide both increase QTc interval.",
        recommendation: "Do not coadminister.",
        monitoring: "ECG/QTc monitoring",
        evidenceSource: "fixture",
        evidenceExcerpt: "fixture",
        sourceReportPath: "fixture",
        reviewStatus: "approved",
        knowledgeBaseVersion: "ikb-ddi03"
      }
    ]
  };
  const store = {
    async load(version) { return version === "ikb-ddi03" ? structuredClone(fixtureKb) : null; },
    async list() { return [{ version: "ikb-ddi03", status: fixtureKb.status }]; }
  };
  const server = createDdiServer({ knowledgeStore: store, activeVersion: "ikb-ddi03", allowAdminWithoutAuth: true });

  const restResult = await server.fetch("http://x/api/ddi-checker/v1/interaction-checks", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      idempotencyKey: "k1",
      medicationSetHash: "h1",
      medications: [
        { name: "Prozac", dose: "20 mg daily" },
        { name: "pimozide", dose: "1 mg daily" }
      ]
    })
  });
  assert.equal(restResult.status, 200);
  const rest = await restResult.json();

  // The REST adapter's alerts must come from engine.checkInteractions: same
  // interacting drugs, severity, and label as a direct browser-style call.
  const browser = engine.checkInteractions(
    [{ name: "Prozac", dose: "20 mg daily" }, { name: "pimozide", dose: "1 mg daily" }],
    fixtureKb
  );
  assert.equal(rest.alerts.length, browser.alerts.length);
  assert.equal(rest.alerts[0].severity, browser.alerts[0].severity);
  assert.deepEqual(rest.alerts[0].medicationInputIndexes.sort((a, b) => a - b), [0, 1]);
  assert.equal(rest.alerts[0].severity, "contraindicated");
  assert.deepEqual(rest.alerts[0].evidence[0], {
    source: browser.alerts[0].evidenceSource,
    excerpt: browser.alerts[0].evidenceExcerpt
  });
});

test("CLI ingest adapter does not re-implement parsing helpers — severity/inference come from the shared parser", () => {
  // If ingest.mjs reintroduced duplicate parsing helpers, they would either
  // diverge from report-parser or shadow it. Assert the adapter imports the
  // shared parser module rather than defining its own severity/inference
  // tables or noise/line-cleaning helpers.
  const source = fs.readFileSync(path.join(repoScripts, "ingest.mjs"), "utf8");
  // It must require the engine's report parser for severity/inference.
  assert.match(source, /require\(["']\.\.\/src\/report-parser\.js["']\)/);
  // And must not declare a local SECTION_MAP / SEVERITY set / inference tables.
  assert.equal(source.match(/\bconst\s+SEVERITY\b/g), null);
  assert.equal(source.match(/\bconst\s+SECTION_MAP\b/g), null);
  // Deduplicated token-cleaning helpers must live in the parser, not here.
  assert.equal(source.match(/\bfunction\s+inferMechanism\b/g), null);
  assert.equal(source.match(/\bfunction\s+inferRecommendation\b/g), null);
  assert.equal(source.match(/\bfunction\s+inferMonitoring\b/g), null);
  // The parser-line / drug-name / dose-extraction helpers must be imported
  // from the parser, not redeclared in the CLI adapter.
  assert.equal(source.match(/\bfunction\s+normalizeDrugName\b/g), null);
  assert.equal(source.match(/\bfunction\s+cleanLine\b/g), null);
  assert.equal(source.match(/\bfunction\s+isNoiseLine\b/g), null);
  assert.equal(source.match(/\bfunction\s+extractDoseSuggestions\b/g), null);
  // addDoseSuggestions is a CLI-only KB-row mutator (unique-push + 30-entry
  // cap), NOT a parser/severity/inference helper — the deduplicated inference
  // is reportParser.extractDoseSuggestions, which is now imported. Instead of
  // forbidding the CLI mutator's declaration, assert its body routes line
  // cleaning through the shared parser's cleanLine (no local duplicate).
  assert.match(source, /function\s+addDoseSuggestions[\s\S]*?cleanLine\(/);
  assert.equal(source.match(/\bfunction\s+cleanLine\b/g), null);
  // The CLI must normalize drug names through engine.normalizeName (alias of
  // report-parser.normalizeDrugName) rather than a local copy.
  assert.match(source, /engine\.normalizeName\b|reportParser\.normalizeDrugName\b/);
});

test("UI source still resolves drugs and checks interactions through the shared engine", () => {
  // app.js uses window.DDIEngine exports for resolution / checking. The REST
  // adapter uses the same engine exports. Make sure the engine exports still
  // drive the browser-facing surface that app.js depends on.
  const appSource = fs.readFileSync(path.join(repoScripts, "..", "src", "app.js"), "utf8");
  for (const api of ["engine.normalizeName(", "engine.resolveDrug(", "engine.checkInteractions(", "engine.parseReportText("]) {
    assert.ok(appSource.includes(api), `app.js must keep routing through ${api}`);
  }
});
