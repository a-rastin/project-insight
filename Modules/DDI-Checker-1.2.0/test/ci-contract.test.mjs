import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

test("CI exposes unit tests and KB validation as separate checks", () => {
  const packageJson = JSON.parse(fs.readFileSync(new URL("../package.json", import.meta.url)));
  assert.equal(packageJson.scripts["test:unit"], "node --test test/*.test.mjs");
  assert.equal(packageJson.scripts["test:kb"], "node scripts/validate-kb.mjs");
  assert.equal(
    packageJson.scripts["test:ci"],
    "npm run test:unit && npm run test:kb"
  );
});

