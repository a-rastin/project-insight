import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createRequire } from "node:module";

// DDI-04: the canonical validation logic lives in src/kb-validator.cjs
// so the server-side CommonJS store can share the exact same clinical
// gate as the ESM CLI. This module re-exports it and adds the CLI runner.
const require = createRequire(import.meta.url);
const { validateKnowledgeBase } = require("../src/kb-validator.cjs");
export { validateKnowledgeBase };

const here = path.dirname(fileURLToPath(import.meta.url));

export function runCli(argv = process.argv.slice(2)) {
  const clinicalActive = argv.includes("--clinical-active");
  const kbPath = argv.find(a => a !== "--clinical-active") || path.resolve(here, "..", "data", "active-kb.json");
  let kb;
  try { kb = JSON.parse(fs.readFileSync(kbPath, "utf8")); }
  catch (error) { console.error(`Unable to read KB ${kbPath}: ${error.message}`); return 1; }
  const errors = validateKnowledgeBase(kb, { clinicalActive });
  if (errors.length) {
    console.error(`KB validation failed (${errors.length} error${errors.length === 1 ? "" : "s"}):\n${errors.map(e => `- ${e}`).join("\n")}`);
    return 1;
  }
  console.log(`KB ${kb.version} validated${clinicalActive ? " for clinical activation" : ""}: ${kb.drugs.length} drugs, ${kb.interactions.length} interactions.`);
  return 0;
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) process.exitCode = runCli();
