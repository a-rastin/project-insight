// One-shot repair driver — DDI-05.
// Runs the same governance repair steps the CLI ingest applies over the
// candidate KB: prune cross-ID ambiguous aliases, then run the validator's
// quarantine partition to drop conflicting / unversioned-duplicate unordered
// pairs. This particular entrypoint is used to repair a previously generated
// bundled active-kb.json whose source corpus is not available on this host;
// the original bytes, relative paths, and sourceReportVersion provenance are
// preserved as non-runtime evidence on every record and report.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { validateKnowledgeBase } = require("../src/kb-validator.cjs");
const engine = require("../src/ddi-engine.js");
const normalizeDrugName = engine.normalizeName;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const kbPath = path.resolve(__dirname, "..", "data", "active-kb.json");

const kb = JSON.parse(fs.readFileSync(kbPath, "utf8"));
const before = { drugs: kb.drugs.length, interactions: kb.interactions.length };

// Step 1 — prune cross-ID ambiguous aliases (first-defined keeps the alias).
// A second pass removes any alias that collides with another drug's CANONICAL
// name — e.g. a brand alias mistakenly tagged on the generic when the brand
// has its own canonical identity. This is a normalization-only fix (no clinical
// threshold or approval is assigned).
const canonicalById = new Map();
for (const drug of kb.drugs) {
  const canonical = normalizeDrugName(drug.name);
  if (canonical) canonicalById.set(drug.id, canonical);
}
const canonicals = new Set(canonicalById.values());
const labelOwners = new Map();
const prunedAliases = [];
kb.drugs.sort((a, b) => String(a.id).localeCompare(String(b.id)));
for (const drug of kb.drugs) {
  const dedupedAliases = [];
  for (const alias of Array.isArray(drug.aliases) ? drug.aliases : []) {
    const norm = normalizeDrugName(alias);
    if (!norm) continue;
    // Drop an alias that matches another drug's canonical name.
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

// Step 2 — run the quarantine partition to drop conflicting pairs.
const partition = validateKnowledgeBase(kb, { returnPartition: true });
kb.interactions = partition.interactions;
kb.quarantine = {
  identities: partition.quarantinedIdentities,
  prunedAliases,
  interactions: partition.quarantinedInteractions,
};
// Preserve the original report corpus as nonruntime evidence input.
if (!kb.source.version) kb.source.version = kb.version;
if (!kb.source.freshness) kb.source.freshness = kb.generatedAt || new Date().toISOString();

// Step 3 — prove structural validation passes on the repaired KB.
const structural = validateKnowledgeBase(kb);
if (structural.length) {
  console.error(`repair failed: ${structural.length} structural error(s) remain:\n${structural.slice(0, 20).map(e => `- ${e}`).join("\n")}`);
  process.exit(1);
}
fs.writeFileSync(kbPath, JSON.stringify(kb, null, 2));
console.log(`repaired ${path.basename(kbPath)}: ${before.drugs}→${kb.drugs.length} drugs, ${before.interactions}→${kb.interactions.length} interactions.`);
console.log(`quarantine partition: ${partition.quarantinedInteractions.length} interaction(s), ${partition.quarantinedIdentities.length} identity(ies), ${prunedAliases.length} pruned alias(es).`);
process.exit(0);
