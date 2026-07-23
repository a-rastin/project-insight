import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
// DDI-03: one authoritative engine. Names, dose extraction, severity, and
// clinical inference live in src/report-parser.js (the parser surface) and
// src/ddi-engine.js (normalize / severity / index / check). This CLI adapter
// only adds the production-ingestion policy on top: RxNorm-seeded identity,
// revision hashing, evidence/review stamps the browser never sets. It MUST
// NOT re-declare parser, severity, or inference helpers.
const reportParser = require("../src/report-parser.js");
const engine = require("../src/ddi-engine.js");
// DDI-05: run the shared validator's quarantine partition over the candidate KB.
const { validateKnowledgeBase } = require("../src/kb-validator.cjs");
const normalizeDrugName = engine.normalizeName;
const cleanLine = reportParser.cleanLine;
const extractDoseSuggestions = reportParser.extractDoseSuggestions;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, "..");
const DEFAULT_SOURCE_DIR = "C:\\Users\\Amirali Hatami\\Project_Insight\\Tools\\Medscape";
const SOURCE_DIR = process.argv[2] || process.env.SOURCE_DIR || DEFAULT_SOURCE_DIR;
export const KB_SCHEMA_VERSION = "1.0.0";
export const PARSER_VERSION = reportParser.PARSER_VERSION;
export const NORMALIZATION_CONFIG = Object.freeze({
  identitySystem: "RxNorm RxCUI",
  resolver: "seeded RxNorm map with rxnorm-pending placeholders for admin review",
  rxNormApi: "https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html",
  dailyMed: "https://dailymed.nlm.nih.gov/dailymed/",
  openFdaDrugLabeling: "https://open.fda.gov/apis/drug/label/"
});

const RXNORM_SEED = new Map(Object.entries({
  acetaminophen: "161",
  alprazolam: "596",
  amitriptyline: "704",
  amoxicillin: "723",
  aripiprazole: "89013",
  aspirin: "1191",
  atorvastatin: "83367",
  azithromycin: "18631",
  bupropion: "42347",
  buspirone: "1827",
  carbamazepine: "2002",
  citalopram: "2556",
  clonazepam: "2598",
  clonidine: "2599",
  clozapine: "2626",
  diazepam: "3322",
  diphenhydramine: "3498",
  divalproex: "266856",
  doxycycline: "3640",
  duloxetine: "72625",
  escitalopram: "321988",
  fluoxetine: "4493",
  gabapentin: "25480",
  haloperidol: "5093",
  hydrochlorothiazide: "5487",
  hydroxyzine: "5553",
  ibuprofen: "5640",
  lamotrigine: "28439",
  linezolid: "190376",
  lisinopril: "29046",
  lithium: "6448",
  lorazepam: "6470",
  losartan: "52175",
  metformin: "6809",
  methadone: "6813",
  methylphenidate: "6901",
  metoprolol: "6918",
  mirtazapine: "15996",
  naproxen: "7258",
  olanzapine: "61381",
  omeprazole: "7646",
  ondansetron: "26225",
  oxycodone: "7804",
  paroxetine: "32937",
  phenelzine: "8123",
  pimozide: "8332",
  propranolol: "8787",
  quetiapine: "51272",
  risperidone: "35636",
  selegiline: "9639",
  sertraline: "36437",
  simvastatin: "36567",
  thioridazine: "10502",
  tramadol: "10689",
  trazodone: "10737",
  valproic_acid: "11118",
  venlafaxine: "39786",
  ziprasidone: "115698",
  zolpidem: "39993"
}));

// CLI-only id slugger for the RxNorm-seeded identity policy below. It is NOT a
// parser, severity, or inference helper; the shared engine name-normalizer
// (engine.normalizeName) is used everywhere else.
function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/\([^)]*\)/g, "")
    .replace(/['']/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function drugIdFor(name) {
  const normalized = normalizeDrugName(name);
  const key = slugify(normalized);
  const rxcui = RXNORM_SEED.get(normalized) || RXNORM_SEED.get(key);
  if (rxcui) {
    return { id: `rxnorm:${rxcui}`, identityStatus: "rxnorm_seeded" };
  }
  return { id: `rxnorm-pending:${key}`, identityStatus: "pending_rxnorm_review" };
}

function getOrCreateDrug(drugs, name, aliases = []) {
  const normalized = normalizeDrugName(name);
  if (!normalized) return null;
  const identity = drugIdFor(normalized);
  if (!drugs.has(identity.id)) {
    drugs.set(identity.id, {
      id: identity.id,
      rxcui: identity.id.startsWith("rxnorm:") ? identity.id.replace("rxnorm:", "") : null,
      name: normalized,
      aliases: [],
      doseSuggestions: [],
      isSourceReportDrug: false,
      identityStatus: identity.identityStatus
    });
  }
  const drug = drugs.get(identity.id);
  for (const alias of aliases) {
    const cleanAlias = cleanLine(alias);
    if (cleanAlias && !drug.aliases.includes(cleanAlias)) drug.aliases.push(cleanAlias);
  }
  return drug;
}

function addDoseSuggestions(drug, suggestions) {
  if (!drug) return;
  if (!Array.isArray(drug.doseSuggestions)) drug.doseSuggestions = [];
  for (const suggestion of suggestions) {
    const cleanSuggestion = cleanLine(suggestion);
    if (cleanSuggestion && !drug.doseSuggestions.includes(cleanSuggestion)) {
      drug.doseSuggestions.push(cleanSuggestion);
    }
  }
  drug.doseSuggestions = drug.doseSuggestions.slice(0, 30);
}

export { normalizeDrugName, extractDoseSuggestions };

function compareRelativePaths(sourceDir, left, right) {
  const leftRelative = path.relative(sourceDir, left).split(path.sep).join("/");
  const rightRelative = path.relative(sourceDir, right).split(path.sep).join("/");
  return leftRelative < rightRelative ? -1 : leftRelative > rightRelative ? 1 : 0;
}

function readTextFiles(sourceDir) {
  const files = [];
  const skipped = [];

  function visit(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        visit(fullPath);
        continue;
      }

      const ext = path.extname(entry.name).toLowerCase();
      if (ext === ".txt" || ext === ".md") {
        files.push(fullPath);
      } else {
        skipped.push(fullPath);
      }
    }
  }

  visit(sourceDir);
  files.sort((a, b) => compareRelativePaths(sourceDir, a, b));
  skipped.sort((a, b) => compareRelativePaths(sourceDir, a, b));
  return { files, skipped };
}

function hashField(hash, label, value) {
  const bytes = Buffer.isBuffer(value) ? value : Buffer.from(String(value), "utf8");
  hash.update(`${label}:${bytes.length}:`, "utf8");
  hash.update(bytes);
  hash.update("\n", "utf8");
}

export function createRevisionId(sourceDir, files, revisionConfig = {}) {
  const schemaVersion = revisionConfig.schemaVersion || KB_SCHEMA_VERSION;
  const parserVersion = revisionConfig.parserVersion || PARSER_VERSION;
  const normalization = revisionConfig.normalization || NORMALIZATION_CONFIG;
  const hash = crypto.createHash("sha256");
  hashField(hash, "schemaVersion", schemaVersion);
  hashField(hash, "parserVersion", parserVersion);
  hashField(hash, "normalization", JSON.stringify(normalization));
  for (const filePath of [...files].sort((a, b) => compareRelativePaths(sourceDir, a, b))) {
    const relativePath = path.relative(sourceDir, filePath).split(path.sep).join("/");
    hashField(hash, "path", relativePath);
    hashField(hash, "content", fs.readFileSync(filePath));
  }
  return `ikb-${hash.digest("hex")}`;
}

function createInteraction({ drugA, drugB, parsed, sourceReportPath, version }) {
  const idBase = `${drugA.id}|${drugB.id}|${parsed.severity}|${parsed.evidenceExcerpt}`;
  return {
    id: `ddi-${crypto.createHash("sha1").update(idBase).digest("hex").slice(0, 16)}`,
    drugAId: drugA.id, drugAName: drugA.name, drugBId: drugB.id, drugBName: drugB.name,
    severity: parsed.severity, mechanism: parsed.mechanism, clinicalEffect: parsed.clinicalEffect,
    recommendation: parsed.recommendation, monitoring: parsed.monitoring,
    evidenceSource: "Source drug report parsed from Medscape export; verify against licensed source and RxNorm before production use.",
    evidenceExcerpt: parsed.evidenceExcerpt, sourceReportPath,
    reviewedBy: null, reviewedAt: null, reviewStatus: "parsed_pending_review",
    parserConfidence: drugB.identityStatus === "pending_rxnorm_review" ? "medium" : "high",
    sourceReportVersion: sourceReportPath, knowledgeBaseVersion: version, sequence: parsed.sequence
  };
}
export function parseReport(raw, filePath, context) {
  const { drugs, version } = context;
  const neutral = reportParser.parseReport(raw, filePath);
  const drugA = getOrCreateDrug(drugs, neutral.primaryDrug.name, neutral.primaryDrug.aliases);
  if (!drugA) return { drug: null, interactions: [], report: neutral.report };
  drugA.isSourceReportDrug = true;
  addDoseSuggestions(drugA, neutral.primaryDrug.doseSuggestions);
  const interactions = neutral.interactions.flatMap((item) => {
    const drugB = getOrCreateDrug(drugs, item.drugBName);
    return drugB && drugB.id !== drugA.id ? [createInteraction({
      drugA, drugB, parsed: item,
      sourceReportPath: filePath, version
    })] : [];
  });
  return { drug: drugA, interactions, report: neutral.report };
}
export function validateDrugIdentities(drugRecords) {
  const labels = new Map();
  for (const drug of Array.isArray(drugRecords) ? drugRecords : []) {
    if (!drug?.id) continue;
    const uniqueForDrug = new Set(
      [drug.name, ...(Array.isArray(drug.aliases) ? drug.aliases : [])]
        .map(normalizeDrugName)
        .filter(Boolean)
    );
    for (const label of uniqueForDrug) {
      if (!labels.has(label)) labels.set(label, new Map());
      labels.get(label).set(drug.id, { id: drug.id, name: drug.name });
    }
  }

  return [...labels.entries()]
    .filter(([, candidates]) => candidates.size > 1)
    .map(([label, candidates]) => ({
      label,
      candidates: [...candidates.values()].sort((a, b) =>
        String(a.id || "").localeCompare(String(b.id || ""))
      )
    }))
    .sort((a, b) => a.label.localeCompare(b.label));
}

export function buildKnowledgeBase(sourceDir = SOURCE_DIR, revisionConfig = {}) {
  const sourceExists = fs.existsSync(sourceDir);
  if (!sourceExists) {
    throw new Error(`Source directory not found: ${sourceDir}`);
  }

  const sourceStat = fs.statSync(sourceDir);
  if (!sourceStat.isDirectory()) {
    throw new Error(`Source path is not a directory: ${sourceDir}`);
  }

  const source = readTextFiles(sourceDir);
  const schemaVersion = revisionConfig.schemaVersion || KB_SCHEMA_VERSION;
  const parserVersion = revisionConfig.parserVersion || PARSER_VERSION;
  const normalization = revisionConfig.normalization || NORMALIZATION_CONFIG;
  const version = createRevisionId(sourceDir, source.files, { schemaVersion, parserVersion, normalization });
  const freshness = new Date().toISOString();
  const drugs = new Map();
  const interactionMap = new Map();
  const reports = [];

  for (const filePath of source.files) {
    const raw = fs.readFileSync(filePath, "utf8");
    const bytes = fs.readFileSync(filePath);
    const contentDigest = crypto.createHash("sha256").update(bytes).digest("hex");
    const relativePath = path.relative(sourceDir, filePath).split(path.sep).join("/");
    const sourceReportVersion = `${relativePath}@sha:${contentDigest.slice(0, 16)}`;
    const parsed = parseReport(raw, filePath, { drugs, version });
    for (const interaction of parsed.interactions) {
      interaction.sourceReportVersion = sourceReportVersion;
    }
    reports.push({
      path: filePath,
      relativePath,
      sourceReportVersion,
      drugId: parsed.drug?.id || null,
      drugName: parsed.drug?.name || path.basename(filePath, path.extname(filePath)),
      parsedInteractionCount: parsed.interactions.length
    });

    for (const interaction of parsed.interactions) {
      if (!interactionMap.has(interaction.id)) interactionMap.set(interaction.id, interaction);
    }
  }

  const interactions = [...interactionMap.values()].sort((a, b) => {
    const byA = a.drugAName.localeCompare(b.drugAName);
    if (byA) return byA;
    return a.drugBName.localeCompare(b.drugBName);
  });

  const drugRecords = [...drugs.values()].sort((a, b) => a.name.localeCompare(b.name));

  // DDI-05 identity/evidence governance step 1 — the parser seam already
  // rejects dose/age/clinical-phrase "drug" headings. An alias can still
  // legitimately collide across drug identities (e.g. "Children's" tagged
  // against cetirizine AND branded variants). Such cross-ID aliases are
  // ambiguous identities; they cannot yield a definitive safe result.
  // Prune the colliding alias from later drugs only (first-defined keeps it),
  // and record the pruned identity so admin review can resolve it. Drug
  // canonical names are never pruned — they identify the record.
  const canonicalById = new Map();
  for (const drug of drugRecords) {
    const canonical = normalizeDrugName(drug.name);
    if (canonical) canonicalById.set(drug.id, canonical);
  }
  const canonicals = new Set(canonicalById.values());
  const labelOwners = new Map();
  const prunedAliases = [];
  for (const drug of drugRecords) {
    const dedupedAliases = [];
    for (const alias of Array.isArray(drug.aliases) ? drug.aliases : []) {
      const norm = normalizeDrugName(alias);
      if (!norm) continue;
      if (canonicals.has(norm) && canonicalById.get(drug.id) !== norm) {
        prunedAliases.push({ label: norm, drugId: drug.id, reason: "collides_with_canonical" });
        continue;
      }
      const owner = labelOwners.get(norm);
      if (owner && owner !== drug.id) {
        prunedAliases.push({ label: norm, drugId: drug.id, conflictWith: owner });
        continue;
      }
      if (!owner) labelOwners.set(norm, drug.id);
      dedupedAliases.push(alias);
    }
    drug.aliases = dedupedAliases;
    const canonical = canonicalById.get(drug.id);
    if (canonical && !labelOwners.has(canonical)) labelOwners.set(canonical, drug.id);
  }

  // DDI-05: identity/evidence governance. Hand the candidate KB to the shared
  // validator's quarantine partition. Ambiguous identities and conflicting /
  // unversioned-duplicate unordered medication pairs are quarantined (with a
  // reason and conflict reference) rather than flattened into the active KB.
  // The bundled KB ships only the survivors; the quarantine partition stays
  // available for admin review without aborting ingestion. The original
  // source corpus is preserved as non-runtime evidence — the relative paths
  // and per-report content digests are carried on each record and report.
  const candidateKb = {
    schemaVersion,
    version,
    status: "draft_parsed_pending_admin_review",
    clinicalUse: { allowedForProduction: false },
    normalization,
    drugs: drugRecords,
    interactions,
  };
  const partition = validateKnowledgeBase(candidateKb, { returnPartition: true });
  const activeInteractions = partition.interactions;
  const quarantine = {
    identities: partition.quarantinedIdentities,
    prunedAliases,
    interactions: partition.quarantinedInteractions,
  };

  return {
    schemaVersion,
    parserVersion,
    version,
    status: "draft_parsed_pending_admin_review",
    generatedAt: freshness,
    activatedAt: null,
    source: {
      type: "medscape-export",
      version,
      freshness,
      path: sourceDir,
      textReportCount: source.files.length,
      skippedFileCount: source.skipped.length,
      skippedFiles: source.skipped
    },
    normalization,
    clinicalUse: {
      allowedForProduction: false,
      reason: "Parsed records require clinician/pharmacist review and activation before production clinical use."
    },
    drugs: drugRecords,
    interactions: activeInteractions,
    reports,
    quarantine,
    auditSchema: {
      captures: [
        "knowledgeBaseVersion",
        "alerts shown",
        "psychiatrist final action",
        "overrides and reasons",
        "source report version"
      ]
    }
  };
}

function writeOutputs(kb) {
  const dataDir = path.join(PROJECT_ROOT, "data");
  fs.mkdirSync(dataDir, { recursive: true });
  const jsonPath = path.join(dataDir, "active-kb.json");
  fs.writeFileSync(jsonPath, JSON.stringify(kb, null, 2));
  // DDI-05: the duplicate browser JS KB artifact is intentionally NOT written.
  // The UI reads the canonical server /knowledge-bases interface instead.
  return { jsonPath };
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const kb = buildKnowledgeBase(SOURCE_DIR);
  const outputs = writeOutputs(kb);
  console.log(`Generated ${kb.interactions.length} interaction records from ${kb.source.textReportCount} text/markdown reports.`);
  console.log(`Drugs: ${kb.drugs.length}`);
  console.log(`Skipped non-text files: ${kb.source.skippedFileCount}`);
  console.log(`Version: ${kb.version}`);
  console.log(`JSON: ${outputs.jsonPath}`);
  console.log(`Browser data: ${outputs.jsPath}`);
}
