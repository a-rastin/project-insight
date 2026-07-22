import { randomUUID } from "node:crypto";

function responseJson(value, status = 200, request) {
  const headers = new Headers({ "content-type": "application/json" });
  headers.set("X-Request-ID", request?.headers?.get("X-Request-ID") || randomUUID());
  headers.set("X-Correlation-ID", request?.headers?.get("X-Correlation-ID") || randomUUID());
  const causation = request?.headers?.get("X-Causation-ID");
  if (causation) headers.set("X-Causation-ID", causation);
  return new Response(JSON.stringify(value), { status, headers });
}

function problem(request, status, code, detail) {
  return responseJson({
    type: `https://insight.example/problems/${code.toLowerCase()}`,
    title: code.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase()),
    status,
    detail,
    instance: request?.url || "/",
    code,
    requestId: request?.headers?.get("X-Request-ID") || randomUUID(),
    correlationId: request?.headers?.get("X-Correlation-ID") || randomUUID(),
  }, status, request);
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
