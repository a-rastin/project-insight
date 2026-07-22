import assert from "node:assert/strict";
import test from "node:test";

import {
  HttpContractAdapter,
  InMemoryContractAdapter,
  createCommonContractHandlers,
} from "../contracts/adapters/node/index.mjs";

const contract = {
  moduleId: "dashboard",
  moduleVersion: "1.2.0",
  interfaceVersion: "1.0.0",
  schemaVersion: "1.0.0",
  basePath: "/api/dashboard/v1",
  capabilities: ["workspace.read"],
  dependencies: [],
  auth: { required: true, schemes: ["session"] },
  compatibilityRoutes: [],
  supportedClinicalScope: { declaration: "module-owned", populations: [], workflows: [] },
};

const problemSchema = { $id: "problem-details", type: "object" };
const openapi = { openapi: "3.1.0", info: { version: "1.0.0" }, paths: {} };

test("Node production and in-memory adapters share registry interface", async () => {
  const memory = new InMemoryContractAdapter({ contract, openapi, schemas: { "1.0.0/problem-details": problemSchema } });
  const production = new HttpContractAdapter(async (url) => {
    const path = new URL(url).pathname;
    const body = path.endsWith("/openapi.json")
      ? openapi
      : path.includes("/schemas/")
        ? problemSchema
        : contract;
    return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
  }, "https://module.invalid");

  assert.deepEqual(await memory.getSchema("1.0.0", "problem-details"), problemSchema);
  assert.deepEqual(await production.getSchema("1.0.0", "problem-details"), problemSchema);
  assert.deepEqual(await memory.getOpenapi(), openapi);
  assert.deepEqual(await production.getOpenapi(), openapi);
});

test("Node common handlers expose safe interface routes", async () => {
  const handlers = createCommonContractHandlers({
    registry: new InMemoryContractAdapter({ contract, openapi, schemas: { "1.0.0/problem-details": problemSchema } }),
    contract,
    readiness: async () => ({ migrations: "ok", configuration: "ok", contractCompatibility: "ok", dependencies: "ok" }),
  });
  assert.equal((await handlers.health()).status, 200);
  const ready = await handlers.ready();
  assert.equal(ready.status, 200);
  assert.equal((await ready.json()).status, "ready");
  assert.deepEqual(await (await handlers.contract()).json(), contract);
  assert.equal((await handlers.schema({ version: "1.0.0", name: "problem-details" })).status, 200);
});
