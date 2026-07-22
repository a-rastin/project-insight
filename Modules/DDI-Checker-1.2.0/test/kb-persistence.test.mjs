import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const persistence = require("../src/kb-persistence.js");

const record = (id, effect, reviewStatus = "pending") => ({
  id, drugAId: "a", drugBId: "b", severity: "major", clinicalEffect: effect, reviewStatus
});
const kb = (version, interactions) => ({
  schemaVersion: "1.0.0", version, status: "draft", clinicalUse: {},
  drugs: [{ id: "a", name: "A" }, { id: "b", name: "B" }], interactions, reports: []
});

test("rebase imports new bundled records and records the new base version", () => {
  const oldBase = kb("v1", [record("ddi-1", "old")]);
  const result = persistence.rebase(kb("v2", [record("ddi-1", "old"), record("ddi-2", "new")]), persistence.createRevision(oldBase, oldBase));
  assert.deepEqual(result.kb.interactions.map((item) => item.id), ["ddi-1", "ddi-2"]);
  assert.equal(result.revision.baseVersion, "v2");
});

test("rebase uses changed bundled content when there is no local edit", () => {
  const oldBase = kb("v1", [record("ddi-1", "old")]);
  const result = persistence.rebase(kb("v2", [record("ddi-1", "corrected")]), persistence.createRevision(oldBase, oldBase));
  assert.equal(result.kb.interactions[0].clinicalEffect, "corrected");
  assert.deepEqual(result.conflicts, []);
});

test("rebase removes deleted bundled records", () => {
  const oldBase = kb("v1", [record("ddi-1", "old")]);
  const result = persistence.rebase(kb("v2", []), persistence.createRevision(oldBase, oldBase));
  assert.deepEqual(result.kb.interactions, []);
});

test("rebase preserves a matching local review and surfaces a changed-record conflict", () => {
  const oldBase = kb("v1", [record("ddi-1", "old")]);
  const edited = structuredClone(oldBase);
  edited.interactions[0].reviewStatus = "approved";
  edited.interactions[0].reviewedBy = "pharmacist";
  const result = persistence.rebase(kb("v2", [record("ddi-1", "corrected")]), persistence.createRevision(oldBase, edited));
  assert.equal(result.kb.interactions[0].clinicalEffect, "corrected");
  assert.equal(result.kb.interactions[0].reviewStatus, "approved");
  assert.equal(result.conflicts[0].type, "bundled_record_changed");
});

test("rebase does not resurrect a removed locally edited record and surfaces the conflict", () => {
  const oldBase = kb("v1", [record("ddi-1", "old")]);
  const edited = structuredClone(oldBase);
  edited.interactions[0].reviewStatus = "approved";
  const result = persistence.rebase(kb("v2", []), persistence.createRevision(oldBase, edited));
  assert.deepEqual(result.kb.interactions, []);
  assert.equal(result.conflicts[0].type, "bundled_record_removed");
});
test("legacy full snapshots do not resurrect removed bundled records", () => {
  const legacySnapshot = kb("v1", [record("ddi-removed", "obsolete"), record("ddi-local-1", "local")]);
  const result = persistence.rebase(kb("v2", []), legacySnapshot);
  assert.deepEqual(result.kb.interactions.map((item) => item.id), ["ddi-local-1"]);
  assert.equal(result.revision.storageVersion, 2);
  assert.equal(result.revision.baseVersion, "v2");
});