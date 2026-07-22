# TP-01 — Intended use, clinical scope, and release gates

## Current disposition

**BLOCKED FOR CLINICAL RELEASE.** This package records the decisions and evidence required for release; it does not represent stakeholder approval. Architecture and research prototyping may continue only if they cannot be mistaken for clinical use.

## Required decision meeting

The meeting record must identify one accountable person for each role: psychiatrist, Clinical Safety Officer, product owner, privacy owner, and regulatory owner. The group must resolve DG-01 through DG-08 in `scope-matrix.v1.json`. Meeting minutes and evidence are referenced; protected material is not copied into this repository.

The Clinical Safety Officer must be a named individual with authority to stop release. A team name, vacancy, or generic mailbox does not satisfy the gate.

## Scope matrix completion rules

The approved matrix must state:

1. Intended use, deployment jurisdiction, regulatory posture, and whether v1 is research-only.
2. Approved guideline editions, formularies, dose references, contraindication sources, monitoring protocols, and licensing conditions.
3. Included population and explicit exclusions for pediatrics, pregnancy, older adults, renal/hepatic impairment, and emergency psychiatry.
4. Included plan sections and whether non-pharmacological care, monitoring, psychoeducation, and referrals are supported.
5. Whether the module recommends an interval, range, or scheduled time and which module owns availability and timezone.
6. Hard blockers and controlled override behavior for missing data, contraindications, allergies, suicide risk, and high-severity DDI findings.
7. Exact v1 diagnosis pathways and coding criteria.
8. Approved diagnosis and medication terminology systems and their licenses.

## Not-supported cases

Every excluded diagnosis, population, workflow, and data-quality condition must be listed in `notSupported`. Each entry defines observable behavior. Unsupported input must never fall through to a plausible-looking plan. Until the list is approved, the system must be treated as supporting no clinical cases.

## Emergency behavior

The approved matrix must define emergency triggers, user-visible instructions, generation/finalization behavior, escalation ownership, and documentation requirements. Treatment Plan must not imply that it contacts emergency services unless a separately validated integration actually does so.

## Regulatory assessment

The regulatory owner must record the assessed jurisdiction, intended-use classification, rationale/evidence reference, assessor, and assessment date. Changes to intended use, population, diagnosis breadth, knowledge sources, or deployment jurisdiction invalidate the assessment and require re-review.

## Clinical validation and release rule

Clinical release is prohibited unless all of the following are true:

- the matrix status is `approved`;
- all eight decision gates are approved with non-empty decisions;
- all five accountable owners are named;
- all five roles signed the exact canonical matrix content;
- a regulatory assessment is complete;
- at least one supported diagnosis and population are explicit;
- emergency behavior and approved knowledge sources are explicit;
- explicit not-supported cases exist;
- clinical validation is complete and the Clinical Safety Officer approved its report.

Run `python scripts/check_tp01_release_gate.py`. A non-zero exit code blocks release packaging or deployment. CI and deployment automation must call this check when those facilities are introduced.

## Change control

Any approved matrix change creates a new document version and new signatures. Never edit a signed matrix in place. Signature records must bind to a canonical SHA-256 hash and point to the authoritative signing evidence.
