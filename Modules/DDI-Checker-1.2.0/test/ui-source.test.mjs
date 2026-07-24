import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..");

test("admin workflow and report upload controls are reachable", () => {
  const html = fs.readFileSync(path.join(projectRoot, "index.html"), "utf8");
  assert.match(html, /data-view="admin"/);
  assert.match(html, /class="admin-shortcut"/);
  assert.match(html, /id="uploadReportForm"/);
  assert.match(html, /type="file"/);
});

test("dashboard shows session code and result export controls", () => {
  const html = fs.readFileSync(path.join(projectRoot, "index.html"), "utf8");
  const app = fs.readFileSync(path.join(projectRoot, "src", "app.js"), "utf8");
  assert.match(html, /id="sessionCode"/);
  assert.match(html, /id="resultSummary"/);
  assert.match(html, /id="exportResultsButton"/);
  assert.match(app, /sessionStorage\.getItem/);
  assert.match(app, /ddi-results-\$\{sessionCode\}\.json/);
});

test("Evidence/source alert markup does not render sourceReportPath", () => {
  const app = fs.readFileSync(path.join(projectRoot, "src", "app.js"), "utf8");
  const evidenceTemplate = app.match(/<strong>Evidence\/source:<\/strong>[\s\S]*?<\/div>/)?.[0] || "";
  assert.ok(evidenceTemplate);
  assert.doesNotMatch(evidenceTemplate, /sourceReportPath/);
  assert.match(evidenceTemplate, /evidenceSource/);
  assert.match(evidenceTemplate, /evidenceExcerpt/);
});


test("activation is blocked and clearly reported when no interactions are approved", () => {
  const app = fs.readFileSync(path.join(projectRoot, "src", "app.js"), "utf8");
  assert.match(app, /if \(!approved\)/);
  assert.doesNotMatch(app, /activation_blocked_no_approved_records/);
  assert.match(app, /no approved interactions available/);
});

test("ambiguous medication identities are shown with candidate names and IDs", () => {
  const app = fs.readFileSync(path.join(projectRoot, "src", "app.js"), "utf8");
  assert.match(app, /result\.ambiguous/);
  assert.match(app, /Choose one identity/);
  assert.match(app, /drug\.id/);
});
test("override rationale uses a cancelable required form and never window.prompt", () => {
  const html = fs.readFileSync(path.join(projectRoot, "index.html"), "utf8");
  const app = fs.readFileSync(path.join(projectRoot, "src", "app.js"), "utf8");
  assert.match(html, /<dialog id="overrideDialog"/);
  assert.match(html, /id="overrideReason"[^>]*maxlength="500"[^>]*required/);
  assert.match(app, /overrideDialog\.addEventListener\("cancel"/);
  assert.match(app, /pendingOverrideAlertId = null/);
  assert.doesNotMatch(app, /window\.prompt/);
});

test("storage failures are persistent and KB mutations roll back", () => {
  const html = fs.readFileSync(path.join(projectRoot, "index.html"), "utf8");
  const app = fs.readFileSync(path.join(projectRoot, "src", "app.js"), "utf8");
  assert.match(html, /id="storageFailure"[^>]*role="alert"/);
  assert.match(app, /if \(!persistKb\(\)\) \{\s*kb = snapshot/);
  assert.match(app, /if \(!writeJson\(STORAGE_KEYS\.meds, medications\)\.ok\) \{ medications = previous; return; \}/);
  assert.match(app, /quota_exceeded/);
});

test("report upload reads files in parallel and never awaits inside the import loop", () => {
  const app = fs.readFileSync(path.join(projectRoot, "src", "app.js"), "utf8");
  const uploadBody = app.match(/async function uploadReports\(event\)\s*\{([\s\S]*?)\n  \}\n/)?.[1] || "";
  assert.ok(uploadBody, "uploadReports body must be present");

  assert.match(uploadBody, /Promise\.all\(/, "file contents must be read concurrently with Promise.all");
  assert.match(uploadBody, /\.text\(\)/, "each file is read via file.text()");

  const parallelReadEnd = uploadBody.indexOf("await Promise.all(");
  assert.ok(parallelReadEnd !== -1, "the single await must guard the parallel Promise.all read");
  const afterRead = uploadBody.slice(parallelReadEnd);
  const closing = afterRead.indexOf(");", "await Promise.all(".length);
  assert.ok(closing !== -1, "Promise.all must be closed");
  const afterPromise = uploadBody.slice(parallelReadEnd + closing + 2);
  assert.doesNotMatch(afterPromise, /\bawait\b/, "no await inside the serial parse/merge loop");

  const loopMatch = uploadBody.match(/for\s*\((?:const file of files|let i = 0;[^)]*)\)\s*\{([\s\S]*?)\n    \}/);
  assert.ok(loopMatch, "uploadReports must keep a per-file serial loop for parse/merge");
  assert.doesNotMatch(loopMatch[1], /\bawait\b/, "the per-file loop must not await inside the body");
});

test("DDI-05: the UI loads the KB from the canonical server interface, not the duplicate active-kb.js artifact", () => {
  const html = fs.readFileSync(path.join(projectRoot, "index.html"), "utf8");
  const app = fs.readFileSync(path.join(projectRoot, "src", "app.js"), "utf8");
  assert.doesNotMatch(html, /src="data\/active-kb\.js"/, "index.html must not load the duplicate active-kb.js artifact");
  assert.doesNotMatch(app, /window\.DDI_ACTIVE_KB/, "app.js must not read the bundled window.DDI_ACTIVE_KB artifact");
  assert.match(app, /\/api\/ddi-checker\/v1\/knowledge-bases/, "app.js must read the canonical server /knowledge-bases interface");
});

