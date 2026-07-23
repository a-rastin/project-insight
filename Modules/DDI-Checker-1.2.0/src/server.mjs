// DDI-01 standalone entrypoint. Wires the .cjs REST seam to a real
// read-only knowledgeStore backed by the bundled data/active-kb.json, plus
// src/auth-adapter.js (HTTP session check when AUTH_SESSION_URL is set, or a
// memory adapter seeded from DDI_AUTH_SESSIONS for local dev). Serves the
// existing static UI (which still calls window.DDIEngine for this packet).
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const require = createRequire(import.meta.url);

// Local module imports only — architecture check forbids cross-module imports
// except contracts.* (none needed by this entrypoint).
const { createDdiServer } = require("./ddi-rest-adapter.cjs");
const { createHttpAuthAdapter, createMemoryAuthAdapter } = require("./auth-adapter.js");

const moduleRoot = join(__dirname, "..");
const kbPath = join(moduleRoot, "data", "active-kb.json");
const kb = JSON.parse(readFileSync(kbPath, "utf8"));

// Read-only knowledgeStore backed by the bundled active-kb.json. Admin
// mutators stay unimplemented for DDI-01; the adapter already returns
// ADMIN_NOT_IMPLEMENTED (501) when knowledgeStore.admin is absent.
function createBundledKnowledgeStore(activeKb) {
  const byVersion = new Map([[activeKb.version, activeKb]]);
  return {
    async load(version) {
      if (!version) return activeKb;
      return byVersion.has(version) ? byVersion.get(version) : null;
    },
    async list() {
      return [{ version: activeKb.version, status: activeKb.status }];
    },
  };
}

function createAuth() {
  if (process.env.AUTH_SESSION_URL) {
    return createHttpAuthAdapter({ sessionUrl: process.env.AUTH_SESSION_URL });
  }
  // Local dev seed: DDI_AUTH_SESSIONS="token=admin roles=ddi_admin;doc= roles=psychiatrist"
  // Each entry is "<token>=<rolesKey>" with rolesKey resolved against an inline
  // "roles=" suffix holding a comma-separated role list. Omit for no sessions.
  const sessions = new Map();
  const seed = process.env.DDI_AUTH_SESSIONS || "";
  for (const chunk of seed.split(";").map((piece) => piece.trim()).filter(Boolean)) {
    const equals = chunk.indexOf("=");
    if (equals === -1) continue;
    const token = chunk.slice(0, equals).trim();
    const tail = chunk.slice(equals + 1).trim();
    const rolesMatch = tail.match(/roles=([^\s]+)/);
    const roles = rolesMatch ? rolesMatch[1].split(",").map((r) => r.trim()).filter(Boolean) : [];
    if (!token) continue;
    sessions.set(token, {
      userId: `seed:${token}`,
      sessionId: `seed-session-${token}`,
      roles,
      expiresAt: "2099-01-01T00:00:00Z",
    });
  }
  return createMemoryAuthAdapter(sessions);
}

const server = createDdiServer({
  knowledgeStore: createBundledKnowledgeStore(kb),
  activeVersion: kb.version,
  auth: createAuth(),
  serveStatic: true,
  moduleRoot,
});

const port = Number(process.env.PORT || 8087);

if (globalThis.Bun) {
  Bun.serve({ port, fetch: server.fetch });
  console.log(`ddi-checker listening on http://0.0.0.0:${port}  basePath=/api/ddi-checker/v1`);
} else if (typeof Deno !== "undefined") {
  Deno.serve({ port }, (request) => server.fetch(request));
  console.log(`ddi-checker listening on http://0.0.0.0:${port}  basePath=/api/ddi-checker/v1`);
} else {
  // Node 18 ships a global fetch but no std HTTP server. The REST seam is
  // framework-agnostic (a fetch handler), so deploy under Bun/Deno/Workers.
  // For local Node smoke-testing use `npx wun` or route through a fetch host;
  // the ddi-rest-adapter.cjs contract is exercised by node --test directly.
  console.error(
    "server.mjs ships a fetch handler for Bun/Deno/Workers runtimes. " +
      "Node has no bundled HTTP server; run with `bun src/server.mjs` or " +
      "PORT=8087 deno run --allow-net --allow-env --allow-read src/server.mjs.",
  );
  process.exit(2);
}
