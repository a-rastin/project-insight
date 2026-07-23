import { createHash, randomUUID } from "node:crypto";

const _ALLOWED_LOG_KEYS = Object.freeze([
  "event",
  "correlation_id",
  "actor_id",
  "entity_id",
  "module",
  "outcome",
  "code",
  "status",
  "method",
  "path",
  "latency_ms",
  "version",
  "policy_version",
  "host",
]);

const _ALLOWED_ANALYTICS_LABELS = Object.freeze([
  "category",
  "dependency",
  "kind",
  "model",
  "module",
  "outcome",
  "policy_version",
  "version",
]);

const _REDACTED_PLACEHOLDER = "[redacted]";

function _opaqueId(value) {
  if (value === null || value === undefined) return null;
  const trimmed = String(value).trim();
  if (!trimmed) return null;
  return "sha256:" + createHash("sha256").update(trimmed, "utf8").digest("hex");
}

function _queryToPath(instance) {
  if (!instance) return "/";
  try {
    const url = new URL(instance, "https://insight.example");
    return url.pathname;
  } catch {
    return String(instance).split("?")[0] || "/";
  }
}

function _stripInstanceQuery(instance) {
  return _queryToPath(instance);
}

function redactProblemDetail(problem) {
  if (!problem || typeof problem !== "object") return problem;
  const redacted = { ...problem };
  redacted.detail = _REDACTED_PLACEHOLDER;
  if (typeof redacted.instance === "string" && redacted.instance.includes("?")) {
    redacted.instance = _stripInstanceQuery(redacted.instance);
  }
  // Drop any non-canonical fields that may carry PHI surfaced by upstream handlers.
  for (const key of ["patientId", "patientName", "mrn", "medications", "diagnosis", "reason"]) {
    if (key in redacted) delete redacted[key];
  }
  if (typeof redacted.title === "string") {
    redacted.title = redacted.title.replace(/\b(?:Alice|Bob|Charlie)\b/gi, _REDACTED_PLACEHOLDER);
  }
  return redacted;
}

function redactLogFields(fields) {
  if (!fields || typeof fields !== "object") return {};
  const redacted = {};
  for (const [key, value] of Object.entries(fields)) {
    if (!_ALLOWED_LOG_KEYS.includes(key)) continue;
    if (key === "actor_id" || key === "entity_id") {
      const hashed = _opaqueId(value);
      redacted[key] = hashed ?? _REDACTED_PLACEHOLDER;
      continue;
    }
    redacted[key] = value;
  }
  return redacted;
}

function _redactMedication(med) {
  if (!med || typeof med !== "object") return _REDACTED_PLACEHOLDER;
  const rebuilt = {};
  for (const allowed of ["name", "dose", "rxNorm", "route"]) {
    if (allowed in med) rebuilt[allowed] = _REDACTED_PLACEHOLDER;
  }
  return rebuilt;
}

function redactExportPayload(payload) {
  if (!payload || typeof payload !== "object") return payload;
  const redacted = { ...payload };
  if ("sessionCode" in redacted) redacted.sessionCode = _REDACTED_PLACEHOLDER;
  if (Array.isArray(redacted.medications)) {
    redacted.medications = redacted.medications.map(_redactMedication);
  }
  if (Array.isArray(redacted.audit)) {
    redacted.audit = redacted.audit.map((entry) => {
      if (!entry || typeof entry !== "object") return _REDACTED_PLACEHOLDER;
      const out = { ...entry };
      for (const forbidden of ["clinician", "patientId", "reason", "medications", "interactingDrugs", "evidenceSource", "evidenceExcerpt"]) {
        if (forbidden in out) delete out[forbidden];
      }
      out.actor_id = _opaqueId(out.actor_id ?? entry?.clinician) ?? _REDACTED_PLACEHOLDER;
      out.entity_id = _opaqueId(out.entity_id ?? entry?.patientId) ?? _REDACTED_PLACEHOLDER;
      return out;
    });
  }
  if ("result" in redacted && typeof redacted.result === "object") {
    redacted.result = { phiRedacted: true };
  }
  return redacted;
}

function redactAnalyticsPoint(point) {
  if (!point || typeof point !== "object") return point;
  const redacted = {
    name: point.name,
    value: point.value,
    labels: {},
  };
  if (point.labels && typeof point.labels === "object") {
    for (const [key, value] of Object.entries(point.labels)) {
      if (_ALLOWED_ANALYTICS_LABELS.includes(key)) redacted.labels[key] = value;
    }
  }
  if (point.correlationId) redacted.correlationId = point.correlationId;
  return redacted;
}

function redactCacheValue(cache) {
  if (!cache || typeof cache !== "object") return cache;
  const redacted = {};
  for (const key of ["etag", "updatedAt", "cachedAt", "expiresAt", "key", "schemaVersion"]) {
    if (key in cache) redacted[key] = cache[key];
  }
  redacted.body = { phiRedacted: true };
  return redacted;
}

function safeResponseHeaders(options = {}) {
  const headers = new Headers();
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "no-referrer");
  if (options.environment === "production") {
    headers.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
  }
  if (options.setCookie && typeof options.setCookie === "string") {
    let cookie = options.setCookie;
    if (options.environment === "production" && !/;\s*Secure/i.test(cookie)) cookie += "; Secure";
    if (!/SameSite=/i.test(cookie)) cookie += "; SameSite=Lax";
    if (options.environment === "production" && !/;\s*HttpOnly/i.test(cookie)) cookie += "; HttpOnly";
    headers.set("Set-Cookie", cookie);
  }
  if (options.clinical) {
    headers.set("Cache-Control", "no-store");
    headers.set("Pragma", "no-cache");
  }
  return headers;
}

function clinicalResponsePolicyDefault({ environment, encryptionAtRestKeyRef }) {
  const isProduction = environment === "production";
  return {
    requireTls: isProduction,
    embedEncryptionKeys: false,
    encryptionAtRestKeyRef: encryptionAtRestKeyRef ?? null,
    environment: environment ?? "development",
    cacheControl: "no-store",
    cookieFlags: isProduction
      ? { secure: true, httpOnly: true, sameSite: "Lax" }
      : { secure: false, httpOnly: true, sameSite: "Lax" },
  };
}

function responseJson(value, status = 200, request, options = {}) {
  const clinical = options.clinical === true;
  const headers = safeResponseHeaders({ clinical, environment: options.environment });
  headers.set("content-type", "application/json");
  headers.set("X-Request-ID", request?.headers?.get("X-Request-ID") || randomUUID());
  headers.set("X-Correlation-ID", request?.headers?.get("X-Correlation-ID") || randomUUID());
  const causation = request?.headers?.get("X-Causation-ID");
  if (causation) headers.set("X-Causation-ID", causation);
  if (options.setCookie) headers.set("Set-Cookie", options.setCookie);
  return new Response(JSON.stringify(value), { status, headers });
}

function problem(request, status, code, detail) {
  const body = redactProblemDetail({
    type: `https://insight.example/problems/${code.toLowerCase()}`,
    title: code.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase()),
    status,
    detail,
    instance: request?.url || "/",
    code,
    requestId: request?.headers?.get("X-Request-ID") || randomUUID(),
    correlationId: request?.headers?.get("X-Correlation-ID") || randomUUID(),
  });
  return responseJson(body, status, request, { clinical: true });
}

export class HttpContractAdapter {
  constructor(fetchImpl = globalThis.fetch, baseUrl = "") {
    this.fetchImpl = fetchImpl;
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async #get(path) {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`);
    if (!response.ok) throw new Error(`contract request failed: ${response.status}`);
    return response.json();
  }

  getSchema(version, name) { return this.#get(`/schemas/${version}/${name}`); }
  getOpenapi() { return this.#get("/openapi.json"); }
  getContract() { return this.#get("/contract"); }
}

export class InMemoryContractAdapter {
  constructor({ schemas = {}, openapi, contract }) {
    this.schemas = schemas;
    this.openapi = openapi;
    this.contract = contract;
  }

  async getSchema(version, name) {
    const value = this.schemas[`${version}/${name}`];
    if (!value) throw new Error(`schema not found: ${version}/${name}`);
    return value;
  }

  async getOpenapi() { return this.openapi; }
  async getContract() { return this.contract; }
}

export function createCommonContractHandlers({ registry, contract, readiness }) {
  return {
    async health(request) { return responseJson({ status: "ok" }, 200, request); },
    async ready(request) {
      const result = await (readiness ? readiness() : {});
      const checks = Object.fromEntries(["migrations", "configuration", "contractCompatibility", "dependencies"].map((key) => [key, result[key] ?? "unknown"]));
      const isReady = Object.values(checks).every((value) => value === "ok" || value === true);
      return responseJson({ status: isReady ? "ready" : "not_ready", checks }, isReady ? 200 : 503, request);
    },
    async contract(request) { return responseJson(contract, 200, request); },
    async openapi(request) { return responseJson(await registry.getOpenapi(), 200, request); },
    async schema({ version, name, request } = {}) {
      try {
        return responseJson(await registry.getSchema(version, name), 200, request);
      } catch {
        return problem(request, 404, "SCHEMA_NOT_FOUND", "Requested schema is not published.");
      }
    },
  };
}

export {
  redactProblemDetail,
  redactLogFields,
  redactExportPayload,
  redactAnalyticsPoint,
  redactCacheValue,
  safeResponseHeaders,
  clinicalResponsePolicyDefault,
};
