import assert from "node:assert/strict";
import fs from "node:fs";

const html = fs.readFileSync(new URL("./public/index.html", import.meta.url), "utf8");

assert.match(html, /startSuicideRiskTransition\(patientCode, true\)/);
assert.match(html, /\/api\/suicide-risk\/v1\/activate/);
assert.match(html, /\/modules\/suicide-risk\?code=\$\{encodeURIComponent\(code\)\}/);
assert.match(html, /The PANSS evaluation was saved, but the Suicide Risk module could not be opened/);
assert.doesNotMatch(html, /startMedicalHistoryTransition\(patientCode, true\)/);
assert.doesNotMatch(html, /\/api\/internal\/medical-history\/activate/);

console.log("severity workflow transition ok");
