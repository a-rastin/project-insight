# INSIGHT canonical identifiers, encounters, and transport interface v1

This is the shared interface for identifier-bearing REST calls between INSIGHT modules. The machine-readable companion is `identifier-transport-contract.v1.json`. Its `schemaVersion` is the contract version and is independent of clinical payload schema versions.

## Canonical identifiers and aliases

`patientId` and `encounterId` are lowercase, hyphenated RFC 4122 UUIDs. Owners generate UUIDv4 values; consumers accept every valid non-nil RFC 4122 variant described by the contract pattern. IDs are opaque, immutable, and never inferred from names, aliases, timestamps, or module-local database keys.

Add New Patient owns `patientCode`, a case-normalized six-character lookup/display alias. Input is trimmed and uppercased before validation. The owner enforces global uniqueness, immutability, and non-reuse. A consumer resolves an alias through the owner's versioned REST interface, then uses the returned `patientId` for relationships and persistence.

Resolution returns exactly one canonical ID. Malformed and unknown aliases return the specified 400 and 404 problems. Any legacy collision returns 409 and fails closed; a resolver never picks the first match. Creation collisions also return 409 and require another alias.

## Encounter semantics

An encounter is one patient-specific episode in which clinical inputs are gathered and one treatment-plan workflow may be performed. Add New Patient owns it and its immutable patient binding. A follow-up is a new encounter, even when it supersedes a prior plan.

Every assessment and recommendation input identifies the same `patientId` and `encounterId`. Treatment Plan rejects mismatches and does not combine facts across encounters. An encounter is never selected by nearest timestamp. A “latest” lookup is permitted only through an endpoint that explicitly defines ordering, eligibility, and tie behavior; persisted relationships retain the resolved `encounterId`.

## Request lineage and replay

The first receiver creates `X-Request-ID` when absent and returns it. The workflow initiator creates `X-Correlation-ID` when absent; every downstream module forwards it unchanged. A caused internal call sets `X-Causation-ID` to the directly causing request's `X-Request-ID`. All three values use the canonical UUID representation.

Replay-safe commands require `Idempotency-Key`. Its scope and payload fingerprint are defined in the machine-readable contract. The same scoped key and fingerprint returns the original result without repeating effects. Reusing the key with a different fingerprint returns 409. Records remain replayable for at least 24 hours; a module may publish a longer retention period.

## Time, schemas, and optimistic concurrency

Persisted and exchanged instants are RFC 3339 UTC strings ending in `Z`. A clinical local time also carries an IANA timezone name; a numeric offset alone is insufficient because it cannot preserve daylight-saving rules. Conversion failures or nonexistent/ambiguous local times are surfaced for explicit resolution, not guessed.

Body-bearing internal requests and responses declare `X-Schema-Version` as a semantic version. Unsupported versions return 422 before clinical fields are used. Versioned resources return a strong opaque `ETag`. Commands that mutate a resource require `If-Match`; absence returns 428 and mismatch returns 412. Clients treat ETags as opaque and never derive them from timestamps.

All failures use `application/problem+json`, include the stable code named in the contract, and return request and correlation headers. Problem details do not expose patient data, aliases, credentials, or raw payloads.

## Conformance

Every module copies or packages the JSON artifact unchanged and runs `tests/test_tp03_identifier_contract.py` (or an equivalent consumer test importing `scripts/check_identifier_contract.py`) against that artifact. A changed rule requires a new contract version; silently weakening a local copy is non-conformant.
