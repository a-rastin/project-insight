# INSIGHT common interface contracts

Version `1.0.0` publishes transport/interface artifacts shared by modules:
JSON Schemas, an OpenAPI fragment, compatibility examples, and generated
Python/Node clients. Executable code is limited to reusable adapters and
generated clients; domain behavior stays in each module.

Every module may mount the common routes at its own `basePath`:

- `GET /health` — process liveness.
- `GET /ready` — injected migration, configuration, compatibility, and dependency checks.
- `GET /contract` — module metadata and capabilities.
- `GET /openapi.json` — module OpenAPI document.
- `GET /schemas/{version}/{name}` — versioned schema.

Adapters generate request and correlation IDs when absent and echo them on
responses. Production adapters load artifacts from disk or HTTP; in-memory
adapters expose the same registry interface for tests.
