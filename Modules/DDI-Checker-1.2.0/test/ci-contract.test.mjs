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

test("analyzer exclusion contract excludes vendored build trees", () => {
  const ignoreFile = fs.readFileSync(
    new URL("../.understand-anything/.understandignore", import.meta.url),
    "utf8"
  );
  function hasActive(pattern) {
    const lines = ignoreFile.split(/\r?\n/).map((l) => l.trim());
    return lines.some((l) => {
      const trimmed = l.replace(/^\s+|\s+$/g, "");
      if (trimmed === "" || trimmed.startsWith("#")) return false;
      return trimmed === pattern;
    });
  }
  const required = ["node_modules/", "build/", "obj/"];
  for (const pattern of required) {
    assert.ok(
      hasActive(pattern),
      `.understandignore must actively exclude "${pattern}" (vended build artifacts must not surface findings such as misra-c2012-17.1 against third-party C)`
    );
  }
});

