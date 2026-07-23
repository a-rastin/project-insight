"""DSM-5-TR schizophrenia diagnostic criteria and evaluation engine.

Source: DSM-5-TR (APA, 2022). Charitable paraphrase for research prototype.
The authoritative reference is the printed manual; do not treat this module
as a diagnostic substitute — clinician confirmation is required (see api.py).

This module is **decision support**, never a decision. ``CriteriaEvaluation``
carries only computed checklist evidence and its rule version. A separate
``DiagnosisAssertion`` carries clinician-authored provenance. The clinician-authority
invariant (the model never auto-decides; bypass is always valid on an unmet
checklist) is a tested contract: ``test_unittest.TestClinicianAuthority``
locks it at the REST + pure-rule layer and the boot self-check loads that suite
via ``api._http_selfcheck`` (HANDOFF §6.1).

Criterion A: >=2 of 9 characteristic symptoms, present for a significant
portion of time during a 1-month period (or less if successfully treated).
At least 1 must be from the core triad (1-3). Criterion B requires functional
impairment; C and D rule out schizoaffective/substance/autism overlap.
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Group labels shown to clinician; ids are stable for the API contract.
CRITERIA: list[dict] = [
    # Criterion A — characteristic symptoms (>=2, at least 1 from items 1-3)
    {"id": "A1",  "group": "Criterion A - Characteristic symptoms",
     "text": "Delusions (fixed false beliefs resistant to evidence).", "core": True},
    {"id": "A2",  "group": "Criterion A - Characteristic symptoms",
     "text": "Hallucinations (perceptual experiences without external stimulus).", "core": True},
    {"id": "A3",  "group": "Criterion A - Characteristic symptoms",
     "text": "Disorganized thinking / speech (frequent derailment or incoherence).", "core": True},
    {"id": "A4",  "group": "Criterion A - Characteristic symptoms",
     "text": "Grossly disorganized or catatonic behaviour.", "core": False},
    {"id": "A5",  "group": "Criterion A - Characteristic symptoms",
     "text": "Negative symptoms: diminished emotional expression, avolition, alogia, anhedonia, asociality.", "core": False},
    {"id": "A6",  "group": "Criterion A - Characteristic symptoms",
     "text": "Symptoms present for a significant portion of 1 month (or less if successfully treated).", "core": False, "duration": True},
    # Criterion B — functional impairment
    {"id": "B1",  "group": "Criterion B - Functioning",
     "text": "Disturbance manifests in reduced level of functioning in work, interpersonal relations, or self-care.",
     "core": False, "guard": "B"},
    # Criterion C — schizoaffective exclusion
    {"id": "C1",  "group": "Criterion C - Schizoaffective exclusion",
     "text": "No major mood episodes occur concurrently with active-phase symptoms (mood episodes, if present, are present for a minority of the total duration).",
     "core": False, "guard": "C"},
    # Criterion D — substance / medical exclusion
    {"id": "D1",  "group": "Criterion D - Substance / medical exclusion",
     "text": "Disturbure is not attributable to substance effects or another medical condition.",
     "core": False, "guard": "D"},
]

GUARD_LABEL = {"B": "Criterion B unmet", "C": "Schizoaffective not excluded", "D": "Substance/medical not excluded"}
RULE_VERSION = "DSM-5-TR-APA-2022"

# The criteria are clinically approved for this module, but the normalized
# diagnosis coding system has not been approved. Keep the code absent until
# that decision exists; readiness must remain blocked in the meantime.
SUPPORTED_CRITERIA_SETS = (
    {
        "diagnosis": "schizophrenia",
        "criteriaSet": "DSM-5-TR",
        "criteriaVersion": "APA-2022",
        "normalizedCoding": {
            "system": None,
            "code": None,
            "display": "Schizophrenia",
            "resolutionStatus": "unresolved",
        },
    },
)


class UnsupportedDiagnosis(ValueError):
    """Raised when a caller requests a diagnosis outside this module's scope."""

    def __init__(self, diagnosis: str):
        self.diagnosis = diagnosis
        super().__init__(f"Unsupported diagnosis: {diagnosis}")


class AssertionState(str, Enum):
    """Explicit states for a clinician-authored diagnosis assertion."""

    ASSERTION = "assertion"
    OVERRIDE = "override"


@dataclass
class CriteriaEvaluation:
    met: bool                              # Criterion A satisfied (>=2, >=1 from core)
    checked_ids: list[str] = field(default_factory=list)
    a_count: int = 0
    core_count: int = 0
    failures: list[str] = field(default_factory=list)   # guard labels not satisfied
    reason: str = ""                       # one-line clinician-facing summary
    rule_version: str = RULE_VERSION

    @property
    def evidence(self) -> dict:
        """Return computed evidence without any assertion fields."""
        return {
            "met": self.met,
            "a_count": self.a_count,
            "core_count": self.core_count,
            "failures": list(self.failures),
            "reason": self.reason,
            "checked": list(self.checked_ids),
        }

    def to_dict(self) -> dict:
        result = self.evidence
        result["rule_version"] = self.rule_version
        return result


@dataclass(frozen=True)
class DiagnosisAssertion:
    """A clinician-authored assertion, independent of computed evidence."""

    code: str
    decision_state: AssertionState
    author: str
    timestamp: datetime
    override_reason: str | None = None

    def __post_init__(self):
        if not self.code.strip():
            raise ValueError("assertion code is required")
        if not self.author.strip():
            raise ValueError("assertion author is required")
        if not isinstance(self.timestamp, datetime):
            raise TypeError("assertion timestamp must be a datetime")
        object.__setattr__(self, "decision_state", AssertionState(self.decision_state))

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "decision_state": self.decision_state.value,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "override_reason": self.override_reason,
        }


# Existing callers retain the old name while the public record is explicit.
Evaluation = CriteriaEvaluation


def supported_clinical_scope() -> dict:
    """Return the immutable contract for the module's supported scope."""
    return {
        "declaration": "module-owned",
        "populations": [],
        "workflows": ["diagnosis"],
        "criteriaSets": deepcopy(list(SUPPORTED_CRITERIA_SETS)),
    }


def get_criteria(diagnosis: str = "schizophrenia") -> list[dict]:
    """Return the criteria tree for the one supported diagnosis."""
    normalized = diagnosis.strip().lower()
    if normalized != "schizophrenia":
        raise UnsupportedDiagnosis(diagnosis)
    return [c.copy() for c in CRITERIA]


def meta_contract() -> dict:
    """Rule contract the browser page consumes for its optimistic display.

    The web page's instant-feedback tiles (symptom count, core count,
    duration, A-met, guards-met) need to render BEFORE the PUT round-trip
    comes back. Rather than mirror the rule logic in JS — which drifts the
    moment someone edits ``evaluate()`` — the page derives every displayed
    number from this contract dict, served by ``GET /diagnosis/_meta``.

    The shapes below are the SAME primitives ``evaluate()`` itself reads,
    so a server rule change here is the single source of truth. The
    contract is locked against the engine by ``test_unittest.py``
    (``test_meta_rules_match_engine_every_subset``): for every subset of
    criteria ids, an optimistic renderer driven ONLY by this contract
    produces the same ``a_count`` / ``core_count`` / ``A-met`` / *all
    guards checked* flags the engine returns. If you add a rule dimension,
    expose its primitive here and add it to that test.
    """
    return {
        # ids whose checked state counts toward the Criterion A symptom
        # count (A-group, NOT duration). Drives the "symptoms" tile.
        "symptom_ids": [c["id"] for c in CRITERIA
                        if c["group"].startswith("Criterion A")
                        and not c.get("duration")],
        # ids of the core triad (A1-A3). Drives the "core" tile.
        "core_ids": [c["id"] for c in CRITERIA if c.get("core")],
        # the single duration id (A6). Required but does not inflate the
        # symptom count.
        "duration_id": next(c["id"] for c in CRITERIA if c.get("duration")),
        # ids of the guard (exclusion) items B1/C1/D1. Each must be checked
        # for the guard to be satisfied.
        "guard_ids": [c["id"] for c in CRITERIA if c.get("guard")],
        # DSM-5-TR thresholds. Locked constants; exposed so the UI never
        # hardcodes them.
        "symptom_threshold": 2,
        "core_threshold": 1,
    }


def _classify(criterion_id: str) -> dict | None:
    for c in CRITERIA:
        if c["id"] == criterion_id:
            return c
    return None


def evaluate(checked_ids: list[str]) -> CriteriaEvaluation:
    """Pure function: given the clinician's checked criteria, return a
    CriteriaEvaluation. No side effects, no I/O — the test surface.

    Rules:
      - Criterion A: count items in group 'Criterion A...' that are checked.
        The duration item (A6) is required but does NOT count toward the
        symptom count of >=2 (it gates duration, per DSM-5-TR).
      - At least one of A1-A5 (symptoms proper), and duration A6, must be met.
      - Of A1-A3 (core triad), at least 1 must be checked.
      - Guards B, C, D: each has one item; if its group appears at all in the
        checklist, the item must be checked (True) to exclude. We model them as
        'must be checked to be excluded/satisfied', matching the UI checkbox.
    """
    checked = set(checked_ids)

    symptom_ids = [c["id"] for c in CRITERIA if c["group"].startswith("Criterion A") and not c.get("duration")]
    core_ids = [c["id"] for c in CRITERIA if c.get("core")]
    duration_id = next(c["id"] for c in CRITERIA if c.get("duration"))
    guard_ids = {c["guard"]: c["id"] for c in CRITERIA if c.get("guard")}

    symptoms_met = [i for i in symptom_ids if i in checked]
    core_met = [i for i in core_ids if i in checked]
    duration_met = duration_id in checked

    a_count = len(symptoms_met)
    core_count = len(core_met)

    failures: list[str] = []
    if a_count < 2:
        failures.append(f"Criterion A: only {a_count} of required >=2 characteristic symptoms")
    if a_count >= 1 and core_count < 1:
        failures.append("Criterion A: at least 1 symptom must be from the core triad (A1-A3)")
    if a_count >= 1 and not duration_met:
        failures.append("Criterion A: duration not established (1-month)")

    for guard, item_id in guard_ids.items():
        if item_id not in checked:
            failures.append(GUARD_LABEL[guard])

    met = not failures

    reason = "DSM-5-TR schizophrenia criteria met." if met else "Criteria not met: " + "; ".join(failures)

    return CriteriaEvaluation(
        met=met,
        checked_ids=sorted(checked),
        a_count=a_count,
        core_count=core_count,
        failures=failures,
        reason=reason,
    )


# --- self-check: delegates to the unittest suite ---------------------------
# ``_demo()`` was the original inline-assert smoke check. The asserts now
# live in ``test_unittest.py::TestCriteriaRules`` (stdlib ``unittest``, no
# new dependency). This shim keeps the boot-time fail-fast contract
# (HANDOFF §9.5) — ``python -m diagnosis.criteria`` still runs them and
# exits non-zero on any failure — without duplicating the assertions.
def _demo():
    """Run the rule-suite unittest cases. Exit non-zero on failure.

    Run: ``python -m diagnosis.criteria``
    """
    import os as _os
    import sys as _sys
    import unittest as _unittest
    import pathlib as _pl

    _here = _pl.Path(__file__).resolve().parents[1]
    if str(_here.parent) not in _sys.path:
        _sys.path.insert(0, str(_here.parent))
    # Avoid picking up the suite's DIAGNOSIS_AUTH_BYPASS=1 import-time pivot
    # — the criteria engine is pure and the rules are env-independent.
    _os.environ.pop("DIAGNOSIS_AUTH_BYPASS", None)
    loader = _unittest.TestLoader()
    suite = loader.loadTestsFromName(
        "test_unittest.TestCriteriaRules")
    runner = _unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("OK: criteria engine self-check passed")


if __name__ == "__main__":
    _demo()
