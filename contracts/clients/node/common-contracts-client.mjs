// Generated from contracts/openapi/1.0.0/common.openapi.json; do not edit.
export class CommonContractsClient {
  constructor(adapter) { this.adapter = adapter; }
  getContract() { return this.adapter.getContract(); }
  getOpenapi() { return this.adapter.getOpenapi(); }
  getSchema(version, name) { return this.adapter.getSchema(version, name); }
}
