# Treatment Plan schema versioning and compatibility

Every payload declares an exact `schemaVersion` in `MAJOR.MINOR.PATCH` form. Published artifacts are immutable and live under `contracts/schemas/<version>/`. The registry identifies supported versions; transport uses `X-Schema-Version` as defined by TP-03.

- **Patch** releases may clarify descriptions or tighten no accepted instance. They must accept every instance accepted by the preceding patch.
- **Minor** releases may add optional fields or enum values. Existing required fields, types, meanings, and accepted values cannot be removed or narrowed. Consumers must ignore only fields explicitly permitted by their negotiated schema; strict schemas otherwise reject unknown fields.
- **Major** releases may make breaking changes. A caller must explicitly negotiate support; unsupported majors fail with `UNSUPPORTED_SCHEMA_VERSION` before clinical fields are processed.

Compatibility is directional: a candidate patch/minor schema must accept the committed corpus for every earlier version in the same major. `scripts/check_tp05_contracts.py` enforces that rule and rejects modification of a released version by checking its manifest digest. Clinical objects use `additionalProperties: false` at safety-relevant levels so misspelled or unreviewed fields fail closed. A new optional extension therefore requires a new minor version rather than an in-place edit.
