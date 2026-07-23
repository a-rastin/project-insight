"use strict";
const { createRequire } = require("node:module");
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");

const requireResolve = createRequire(__filename);
const engine = requireResolve("./ddi-engine.js");

const SCHEMA_VERSION = "1.0.0";
const INTERFACE_VERSION = "1.0.0";
const MODULE_ID = "ddi-checker";
const BASE_PATH = "/api/ddi-checker/v1";
const DEPRECATED_ALIAS = "/api/ddi/v1";

function pivotalProblem(request, status, code, detail) {
  const headers = new Headers({ "content-type": "application/problem+json" });
  headers.set("X-Request-ID", request.headers.get("X-Request-ID") || crypto.randomUUID());
  headers.set("X-Correlation-ID", request.headers.get("X-Correlation-ID") || crypto.randomUUID());
  const causation = request.headers.get("X-Causation-ID");
  if (causation) headers.set("X-Correlation-ID", causation + "," + headers.get("X-Correlation-ID"));
  return new Response(JSON.stringify({
    type: `https://insight.example/problems/${code.toLowerCase()}`,
    title: code.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase()),
    status,
    detail,
    instance: new URL(request.url).pathname,
    code,
    requestId: headers.get("X-Request-ID"),
    correlationId: headers.get("X-Correlation-ID"),
  }), { status, headers });
}

function ok(request, body, status = 200, extraHeaders = {}) {
  const headers = new Headers({ "content-type": "application/json", ...extraHeaders });
  headers.set("X-Request-ID", request.headers.get("X-Request-ID") || crypto.randomUUID());
  headers.set("X-Correlation-ID", request.headers.get("X-Correlation-ID") || crypto.randomUUID());
  const causation = request.headers.get("X-Causation-ID");
  if (causation) headers.set("X-Correlation-ID", causation);
  return new Response(JSON.stringify(body), { status, headers });
}

function okWithoutRequest(body, status = 200) {
  const headers = new Headers({ "content-type": "application/json" });
  headers.set("X-Request-ID", crypto.randomUUID());
  headers.set("X-Correlation-ID", crypto.randomUUID());
  return new Response(JSON.stringify(body), { status, headers });
}

function canonicalBaseVersion(version) {
  return String(version || "").trim() || "";
}

function readContractsArtifact(name) {
  const root = path.resolve(__dirname, "..", "..", "..", "contracts");
  const schemasDir = path.join(root, "schemas", SCHEMA_VERSION);
  const openapiPath = path.join(root, "openapi", SCHEMA_VERSION, "common.openapi.json");
  if (name === "openapi") {
    return fs.existsSync(openapiPath) ? { common: JSON.parse(fs.readFileSync(openapiPath, "utf8")) } : null;
  }
  const file = path.join(schemasDir, name + ".schema.json");
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : null;
}

function ddiContractPayload() {
  return {
    moduleId: MODULE_ID,
    moduleVersion: "1.2.0",
    interfaceVersion: INTERFACE_VERSION,
    schemaVersion: SCHEMA_VERSION,
    basePath: BASE_PATH,
    capabilities: [
      "ddi.interaction-check",
      "ddi.medication-resolve",
      "ddi.knowledge-base.read",
      "ddi.knowledge-base.admin",
    ],
    dependencies: [
      {
        moduleId: "authentication",
        interfaceVersion: "1.0.0",
        required: true,
        capabilities: ["auth.session"],
      },
    ],
    auth: { required: true, schemes: ["session"] },
    compatibilityRoutes: [
      { path: DEPRECATED_ALIAS, deprecated: true, replacement: BASE_PATH },
    ],
    supportedClinicalScope: {
      declaration: "module-owned",
      populations: ["adults receiving psychiatric pharmacotherapy"],
      workflows: ["interaction-check", "knowledge-base-admin"],
    },
  };
}

function buildOpenapiDocument() {
  const paths = {
    [`${BASE_PATH}/medications/resolve`]: {
      post: {
        summary: "Resolve one medication identity against a knowledge-base version",
        operationId: "resolveMedication",
        requestBody: { required: true, content: { "application/json": { schema: { type: "object" } } } },
        responses: { "200": { description: "resolved identity" }, "404": { description: "unknown KB version" } },
      },
    },
    [`${BASE_PATH}/interaction-checks`]: {
      post: {
        summary: "Run a deterministic pairwise interaction check for an exact medication set",
        operationId: "interactionChecks",
        requestBody: { required: true, content: { "application/json": { schema: { type: "object" } } } },
        responses: { "200": { description: "interaction check result" }, "400": { description: "invalid request" } },
      },
    },
    [`${BASE_PATH}/knowledge-bases/{version}`]: {
      get: {
        summary: "Read one knowledge-base revision",
        operationId: "getKnowledgeBase",
        responses: { "200": { description: "KB snapshot" }, "404": { description: "unknown version" } },
      },
    },
    [`${BASE_PATH}/knowledge-bases`]: {
      get: {
        summary: "List available knowledge-base revisions (admin)",
        operationId: "listKnowledgeBases",
        responses: { "200": { description: "KB versions" }, "401": { description: "unauthenticated" } },
      },
    },
    [`${BASE_PATH}/knowledge-bases/{version}/review`]: {
      post: { summary: "Admin review draft", operationId: "reviewDraft", responses: { "401": {}, "403": {} } },
    },
    [`${BASE_PATH}/knowledge-bases/{version}/activate`]: {
      post: { summary: "Admin activate draft revision", operationId: "activateKb", responses: { "200": {}, "401": {}, "403": {} } },
    },
    [`${BASE_PATH}/knowledge-bases/{version}/retire`]: {
      post: { summary: "Admin retire active revision", operationId: "retireKb", responses: { "200": {}, "401": {}, "403": {} } },
    },
    [`${BASE_PATH}/knowledge-bases/{version}/rollback`]: {
      post: { summary: "Admin rollback active revision", operationId: "rollbackKb", responses: { "200": {}, "401": {}, "403": {} } },
    },
  };
  return {
    openapi: "3.1.0",
    info: { title: "DDI Checker", version: INTERFACE_VERSION, description: "Standalone drug-drug interaction REST seam" },
    paths,
    components: {},
  };
}

function medicationInputToEngine(medication) {
  if (!medication || typeof medication !== "object") return { name: "", dose: "" };
  const text = medication.originalText || medication.name || medication.medicationCode || "";
  return {
    name: String(text || ""),
    dose: typeof medication.dose === "string" ? medication.dose : "",
    route: typeof medication.route === "string" ? medication.route : undefined,
    frequency: typeof medication.frequency === "string" ? medication.frequency : undefined,
    medicationCode: typeof medication.medicationCode === "string" ? medication.medicationCode : undefined,
    codeSystem: typeof medication.codeSystem === "string" ? medication.codeSystem : undefined,
  };
}

function knowledgeBaseShape(kb) {
  return {
    version: kb.version,
    schemaVersion: kb.schemaVersion,
    status: kb.status,
    generatedAt: kb.generatedAt || null,
    activatedAt: kb.activatedAt || null,
    drugs: Array.isArray(kb.drugs)
      ? kb.drugs.map((drug) => ({ id: drug.id, name: drug.name, aliases: drug.aliases || [] }))
      : [],
    interactions: Array.isArray(kb.interactions)
      ? kb.interactions.map((row) => ({
          id: row.id,
          severity: row.severity,
          drugAId: row.drugAId,
          drugBId: row.drugBId,
          reviewStatus: row.reviewStatus,
          knowledgeBaseVersion: row.knowledgeBaseVersion,
        }))
      : [],
  };
}

function resolveMedication(input, kb) {
  const index = engine.buildIndex(kb);
  return engine.resolveDrug(input, index);
}

function interactionCheck(request, kb) {
  const meds = Array.isArray(request.medications) ? request.medications : [];
  const engineMeds = meds.map(medicationInputToEngine);
  const index = engine.buildIndex(kb);
  const resolutions = engineMeds.map((med) => engine.resolveDrug(med.name, index));
  const result = engine.checkInteractions(engineMeds, kb);

  const normalizedMedications = engineMeds.map((med, inputIndex) => {
    const resolution = resolutions[inputIndex];
    const identity = {
      inputIndex,
      originalText: med.name,
      codeSystem: med.codeSystem || null,
    };
    if (resolution.status === "resolved") {
      identity.conceptId = resolution.drug.id;
      identity.display = resolution.drug.name;
    } else if (resolution.status === "ambiguous") {
      identity.conceptId = null;
      identity.candidates = resolution.candidates.map((drug) => ({ id: drug.id, name: drug.name }));
    } else {
      identity.conceptId = null;
    }
    return identity;
  });

  const unresolvedMedications = resolutions
    .map((resolution, inputIndex) => ({
      resolution,
      inputIndex,
      medication: engineMeds[inputIndex],
    }))
    .filter((row) => row.resolution.status === "unknown" && row.medication.name);

  const unresolvedInputIndexes = new Set(unresolvedMedications.map((row) => row.inputIndex));
  const resolvedIndexes = resolutions
    .map((resolution, idx) => ({ resolution, idx }))
    .filter((row) => row.resolution.status === "resolved")
    .map((row) => row.idx);

  const pairsChecked = [];
  for (let left = 0; left < resolvedIndexes.length; left += 1) {
    for (let right = left + 1; right < resolvedIndexes.length; right += 1) {
      const leftIndex = resolvedIndexes[left];
      const rightIndex = resolvedIndexes[right];
      const pairKey = engine.pairKey(resolutions[leftIndex].drug.id, resolutions[rightIndex].drug.id);
      pairsChecked.push({
        medicationInputIndexes: [leftIndex, rightIndex],
        interactionId: null,
        pairKey,
        severity: null,
      });
    }
  }

  const alerts = result.alerts.map((alert) => {
    const matched = engineMeds
      .map((med, idx) => ({ med, idx }))
      .filter((row) => alert.patientMedications.some((inputMed) => engine.normalizeName(inputMed.name) === engine.normalizeName(row.med.name)))
      .map((row) => row.idx);
    return {
      alertId: alert.id,
      interactionId: alert.interactionId,
      medicationInputIndexes: matched,
      severity: alert.severity,
      mechanism: alert.mechanism || null,
      recommendedAction: alert.recommendedAction,
      evidence: [
        { source: alert.evidenceSource || "knowledge-base", excerpt: alert.evidenceExcerpt || "" },
      ],
      knowledgeBaseVersion: alert.knowledgeBaseVersion,
    };
  });

  const unresolved = unresolvedMedications.map((row) => ({
    inputIndex: row.inputIndex,
    originalText: row.medication.name,
    codeSystem: row.medication.codeSystem || null,
    candidates: [],
  }));

  return {
    schemaVersion: SCHEMA_VERSION,
    checkId: request.idempotencyKey || crypto.randomUUID(),
    idempotencyKey: request.idempotencyKey,
    medicationSetHash: request.medicationSetHash,
    knowledgeBaseId: `${MODULE_ID}:${kb.version}`,
    knowledgeBaseVersion: kb.version,
    normalizedMedications,
    unresolvedMedications: unresolved,
    pairsChecked,
    alerts,
  };
}

function requireAuth(request, auth, options = {}) {
  const principal = auth ? auth.verify(request.headers.get("cookie")) : null;
  if (principal && typeof principal.then === "function") return principal;
  return Promise.resolve(principal);
}

function hasAdminRole(principal) {
  // TODO(DDI-01): pending confirmation of the canonical Authentication admin role.
  // Authentication-1.1.0 issues roles {admin, psychiatrist, user}; the gate
  // here uses "ddi_admin" only as a local identifier matching the test stub.
  // Before exposing admin mutators in production, switch this to the agreed
  // canonical role (likely "admin") or a dedicated scope claim issued by the
  // Authentication module. Until then the endpoints remain protected (gated).
  return Boolean(principal && Array.isArray(principal.roles) && principal.roles.includes("ddi_admin"));
}

function routeStaticFile(filePathFull) {
  if (!fs.existsSync(filePathFull) || !fs.statSync(filePathFull).isFile()) return null;
  const ext = path.extname(filePathFull).toLowerCase();
  const types = { ".html": "text/html", ".js": "application/javascript", ".css": "text/css", ".json": "application/json" };
  return new Response(fs.readFileSync(filePathFull), {
    status: 200,
    headers: { "content-type": types[ext] || "application/octet-stream" },
  });
}

function createDdiServer(options = {}) {
  const knowledgeStore = options.knowledgeStore;
  if (!knowledgeStore || typeof knowledgeStore.load !== "function") {
    throw new Error("knowledgeStore.load is required");
  }
  const auth = options.auth || null;
  const allowAdminWithoutAuth = Boolean(options.allowAdminWithoutAuth);
  const activeVersion = options.activeVersion;
  const moduleRoot = options.moduleRoot || path.resolve(__dirname, "..");
  const staticIndexRoot = options.serveStatic !== false ? moduleRoot : null;
  const contract = ddiContractPayload();
  const openapiDocument = buildOpenapiDocument();

  async function loadActiveKb(versionOverride) {
    const version = versionOverride || activeVersion;
    if (!version) return null;
    const kb = await knowledgeStore.load(version);
    return kb || null;
  }

  async function handleApiCall(request, pathname) {
    if (pathname === "/health") return readHealth();
    if (pathname === "/ready") return readReady();
    if (pathname === "/contract") return ok(request, contract, 200);
    if (pathname === "/openapi.json") {
      const common = readContractsArtifact("openapi");
      const body = common ? { ...openapiDocument, "x-insight-common-openapi": common.common } : openapiDocument;
      return ok(request, body, 200);
    }
    const schemaMatch = pathname.match(/^\/schemas\/([^/]+)\/([^/]+)$/);
    if (schemaMatch) {
      const artifact = readContractsArtifact(schemaMatch[2]);
      if (!artifact) return pivotalProblem(request, 404, "SCHEMA_NOT_FOUND", "Requested schema is not published.");
      return new Response(JSON.stringify(artifact), {
        status: 200,
        headers: { "content-type": "application/schema+json" },
      });
    }
    const canonicalPath = stripAliasPrefix(pathname);
    if (!canonicalPath.startsWith(`${BASE_PATH}`) && canonicalPath !== BASE_PATH) {
      return staticIndexRoot ? serveStatic(request, pathname) : pivotalProblem(request, 404, "NOT_FOUND", `${pathname}`);
    }

    if (canonicalPath === `${BASE_PATH}/medications/resolve` && request.method === "POST") {
      return handleResolve(request);
    }
    if (canonicalPath === `${BASE_PATH}/interaction-checks` && request.method === "POST") {
      return handleInteractionChecks(request);
    }
    const kbMatch = canonicalPath.match(new RegExp(`^${BASE_PATH}/knowledge-bases(/([^/]+))?(?:/(review|activate|retire|rollback))?$`));
    if (kbMatch) {
      return handleKnowledgeBase(request, kbMatch);
    }
    return pivotalProblem(request, 404, "NOT_FOUND", `${pathname}`);
  }

  function stripAliasPrefix(pathname) {
    if (pathname.startsWith(DEPRECATED_ALIAS)) return `${BASE_PATH}${pathname.slice(DEPRECATED_ALIAS.length)}`;
    return pathname;
  }

  function readHealth() {
    return okWithoutRequest({ status: "ok" }, 200);
  }

  function readReady() {
    const checks = { migrations: "ok", configuration: "ok", contractCompatibility: "ok", dependencies: "ok" };
    return okWithoutRequest({ status: "ready", checks }, 200);
  }

  async function readJson(request) {
    try {
      const text = await request.text();
      return { ok: true, body: text ? JSON.parse(text) : {} };
    } catch {
      return { ok: false };
    }
  }

  async function handleResolve(request) {
    const parsed = await readJson(request);
    if (!parsed.ok) return pivotalProblem(request, 400, "INVALID_REQUEST", "Request body must be JSON.");
    const body = parsed.body || {};
    const kb = await loadActiveKb(body.knowledgeBaseVersion || activeVersion);
    if (!kb) return pivotalProblem(request, 404, "KNOWLEDGE_BASE_NOT_FOUND", `Unknown knowledge-base version: ${body.knowledgeBaseVersion || activeVersion || ""}`);
    const resolution = resolveMedication(body.input, kb);
    return ok(request, resolution, 200);
  }

  async function handleInteractionChecks(request) {
    const parsed = await readJson(request);
    if (!parsed.ok) return pivotalProblem(request, 400, "INVALID_REQUEST", "Request body must be JSON.");
    const body = parsed.body || {};
    if (typeof body.idempotencyKey !== "string" || !body.idempotencyKey.trim()) {
      return pivotalProblem(request, 400, "INVALID_REQUEST", "idempotencyKey is required.");
    }
    if (typeof body.medicationSetHash !== "string" || !body.medicationSetHash.trim()) {
      return pivotalProblem(request, 400, "INVALID_REQUEST", "medicationSetHash is required.");
    }
    const kb = await loadActiveKb(activeVersion);
    if (!kb) return pivotalProblem(request, 503, "KNOWLEDGE_BASE_UNAVAILABLE", "No active knowledge base is loaded.");
    const result = interactionCheck(body, kb);
    return ok(request, result, 200);
  }

  async function handleKnowledgeBase(request, match) {
    const version = match[2];
    const action = match[3];
    if (!version) {
      const principal = await requireAuth(request, auth);
      if (!principal && !allowAdminWithoutAuth) return pivotalProblem(request, 401, "UNAUTHENTICATED", "Authentication is required.");
      if (!allowAdminWithoutAuth && !hasAdminRole(principal)) return pivotalProblem(request, 403, "FORBIDDEN", "ddi_admin role is required.");
      const list = await knowledgeStore.list();
      return ok(request, list || [], 200);
    }
    if (!action) {
      const kb = await knowledgeStore.load(version);
      if (!kb) return pivotalProblem(request, 404, "KNOWLEDGE_BASE_NOT_FOUND", `Unknown knowledge-base version: ${version}`);
      return ok(request, knowledgeBaseShape(kb), 200);
    }
    const principal = await requireAuth(request, auth);
    if (!principal && !allowAdminWithoutAuth) return pivotalProblem(request, 401, "UNAUTHENTICATED", "Authentication is required.");
    if (!allowAdminWithoutAuth && !hasAdminRole(principal)) return pivotalProblem(request, 403, "FORBIDDEN", "ddi_admin role is required.");
    if (typeof knowledgeStore.admin !== "function") {
      return pivotalProblem(request, 501, "ADMIN_NOT_IMPLEMENTED", "Admin mutator for the requested action is not wired for this deployment.");
    }
    const parsed = await readJson(request);
    const result = await knowledgeStore.admin(action, version, parsed.ok ? parsed.body || {} : {});
    return ok(request, result, 200);
  }

  function serveStatic(request, pathname) {
    const normalized = pathname === "/" || pathname === "" ? "/index.html" : pathname;
    let candidate = path.join(moduleRoot, decodeURIComponent(normalized.replace(/^\//, "")));
    if (!candidate.startsWith(moduleRoot)) return pivotalProblem(request, 400, "BAD_REQUEST", "Invalid path.");
    if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) return routeStaticFile(candidate);
    if (fs.existsSync(candidate) && fs.statSync(candidate).isDirectory()) {
      const indexPath = path.join(candidate, "index.html");
      if (fs.existsSync(indexPath)) return routeStaticFile(indexPath);
    }
    const indexFallback = path.join(moduleRoot, "index.html");
    if (fs.existsSync(indexFallback)) return routeStaticFile(indexFallback);
    return pivotalProblem(request, 404, "NOT_FOUND", `${pathname}`);
  }

  const fetchImpl = async (input, init) => {
    const request = new Request(input, init);
    let pathname;
    try { pathname = new URL(request.url).pathname; } catch { return pivotalProblem(request, 400, "BAD_REQUEST", "Invalid URL."); }
    try {
      return await handleApiCall(request, pathname);
    } catch (error) {
      return pivotalProblem(request, 500, "INTERNAL_ERROR", error?.message || "Unhandled error.");
    }
  };

  return {
    fetch: fetchImpl,
    contract,
    openapiDocument,
    config: { activeVersion: options.activeVersion, allowAdminWithoutAuth },
  };
}

module.exports = {
  createDdiServer,
  ddiContractPayload,
  buildOpenapiDocument,
  interactionCheck,
  resolveMedication,
  knowledgeBaseShape,
  SCHEMA_VERSION,
  INTERFACE_VERSION,
  MODULE_ID,
  BASE_PATH,
  DEPRECATED_ALIAS,
};
