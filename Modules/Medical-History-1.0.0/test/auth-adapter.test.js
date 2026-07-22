const assert = require("node:assert/strict");
const { createMemoryAuthAdapter, parseCanonicalSession } = require("../auth-adapter.js");

const future = "2099-01-01T00:00:00Z";
const canonical = {
  schemaVersion: "1.0.0",
  authenticated: true,
  user: { id: "u-1", username: "doc", roles: ["psychiatrist"], displayName: "Doc" },
  session: { id: "s-1", expiresAt: future },
  gates: { disclaimerAccepted: true, passwordChangeRequired: false },
};

assert.equal(parseCanonicalSession(canonical)?.userId, "u-1");
assert.equal(parseCanonicalSession({ ok: true, message: "hi", display_role: "Admin" }), null);
assert.equal(parseCanonicalSession({ ...canonical, schemaVersion: "0.9" }), null);
assert.equal(parseCanonicalSession({ ...canonical, gates: { disclaimerAccepted: false, passwordChangeRequired: false } }), null);
assert.equal(parseCanonicalSession({ ...canonical, user: { ...canonical.user, roles: ["Psychiatrist"] } }), null);

(async () => {
  const memory = createMemoryAuthAdapter(new Map([["tok", parseCanonicalSession(canonical)]]));
  assert.equal((await memory.verify("insight_session=tok")).sessionId, "s-1");
  assert.equal(await memory.verify("insight_session=missing"), null);
  console.log("medical-history auth-adapter ok");
})();
