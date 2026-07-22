# ADR TP-04 - Disposable lifecycle prototype

Status: proposed for psychiatrist walkthrough; not a clinical approval  
Date: 2026-07-13

## Context and decision

TP-01 remains blocked for clinical release. Keep this executable conversation aid under `prototype/`, use synthetic data, and expose one deep module interface: `reduce(state, action) -> new_state`. The pure reducer has no I/O and does not mutate its input. Run its terminal adapter with `python prototype/run_lifecycle.py`; it prints full state after every accepted or rejected action.

Delete `prototype/` after the walkthrough unless a later issue explicitly preserves it as research evidence. Production code must not import it.

## Provisional findings to agree with a psychiatrist

- Incomplete inputs block generation; a complete replacement snapshot enters evaluation.
- Only generated, editing, and ready-for-review drafts are mutable. Editing returns review to editing.
- Finalization is legal only from ready-for-review.
- A high-severity DDI blocks finalization. For this prototype only, override requires an existing high-severity finding plus a nonblank reason and actor; blank, duplicate, unknown, and non-high overrides are rejected.
- Final content is immutable. A non-empty follow-up delta can lead to supersession and a requested successor descriptor.
- These hypotheses are not approved emergency, contraindication, allergy, suicide-risk, or clinical override rules. TP-01 remains authoritative and fail-closed.

## Six-scenario walkthrough record

The runner covers incomplete inputs; straight-through finalization; all four edit types; blocked high DDI; rejected then accepted override; and follow-up supersession with illegal post-supersession edit.

Do not fabricate acceptance. Complete after the actual session:

- Psychiatrist: pending
- Session date: pending
- Transition rules agreed: pending
- Override rules agreed: pending
- Findings/minutes reference: pending

## Consequences

The reducer concentrates policy behind a small test surface. It deliberately omits persistence, clocks, REST, authentication, clinical knowledge, and production adapters. Future implementation must start from approved governance, not promote this prototype mechanically.
