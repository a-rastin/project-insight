# XML Bayesian Network Migration

The BN Manager 2.0 rebuild replaces the former Parkinsonism/Akathisia and legacy `.net` workflows with four canonical `.xml` networks and the supplied `XSD.xml`.

## Decisions

- Exactly four registry entries are exposed.
- `.xml` is the only accepted model extension at the API boundary.
- Registry and schema files are module-owned and path-safe.
- All four targets are chance nodes and use posterior evaluation.
- One-row conditional tables are broadcast across parent combinations.
- The conversion route, `.net` parser, and standalone workbench are removed.
- Contract version is `2.0.0`.

## Verification

The automated suite compiles every network against the supplied schema, validates semantic table dimensions and row sums, checks targets, exercises model registry APIs, rejects legacy formats, and evaluates the Clozapine target through authenticated API routes.
