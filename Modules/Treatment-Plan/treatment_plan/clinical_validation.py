"""Clinical validation metrics and fail-closed safety-case release decision (TP-21)."""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Iterable, Mapping, Sequence


_ID = re.compile(r"^[A-Z][A-Z0-9-]{2,63}$")
_CLINICIAN_ROLES = frozenset({"psychiatrist", "clinicalSafetyOfficer"})
_REQUIRED_APPROVALS = frozenset({"independentPsychiatrist", "clinicalSafetyOfficer"})
_UNSPECIFIED_SUBGROUP = "unspecified"


class CaseKind(StrEnum):
    REFERENCE = "reference"
    EDGE = "edge"
    COUNTERFACTUAL = "counterfactual"
    SUBGROUP = "subgroup"
    FAILURE_INJECTION = "failureInjection"
    OVERRIDE_WORKFLOW = "overrideWorkflow"


@dataclass(frozen=True)
class ValidationProtocol:
    evidence_ref: str
    max_unsafe_omission_rate: float
    max_unsafe_commission_rate: float
    min_concordance: float
    max_alerts_per_case: float
    min_task_completion_rate: float
    max_use_error_rate: float
    max_brier_score: float | None = None

    def __post_init__(self) -> None:
        errors: list[str] = []
        if not self.evidence_ref.strip():
            errors.append("validation protocol requires a controlled evidence reference")
        for name in (
            "max_unsafe_omission_rate", "max_unsafe_commission_rate", "min_concordance",
            "min_task_completion_rate", "max_use_error_rate",
        ):
            value = getattr(self, name)
            if not 0 <= value <= 1:
                errors.append(f"{name} must be between zero and one")
        if self.max_alerts_per_case < 0:
            errors.append("max_alerts_per_case cannot be negative")
        if self.max_brier_score is not None and not 0 <= self.max_brier_score <= 1:
            errors.append("max_brier_score must be between zero and one")
        if errors:
            raise ValueError("; ".join(errors))


@dataclass(frozen=True)
class ClinicalCase:
    case_id: str
    kind: CaseKind
    author_role: str
    author_evidence_ref: str
    expected_actions: frozenset[str] = frozenset()
    prohibited_actions: frozenset[str] = frozenset()
    expected_unresolved: frozenset[str] = frozenset()
    subgroup: str | None = None
    expected_override: bool | None = None
    calibration_outcomes: tuple[tuple[str, bool], ...] = ()

    def __post_init__(self) -> None:
        if not _ID.fullmatch(self.case_id):
            raise ValueError("case_id must be a stable uppercase identifier")
        if self.author_role not in _CLINICIAN_ROLES or not self.author_evidence_ref.strip():
            raise ValueError("each case requires attributable clinician authorship evidence")
        if self.kind is CaseKind.SUBGROUP and not (self.subgroup and self.subgroup.strip()):
            raise ValueError("subgroup cases must name the evaluated subgroup")
        if self.expected_actions & self.prohibited_actions:
            raise ValueError("an action cannot be both expected and prohibited")


@dataclass(frozen=True)
class CaseObservation:
    case_id: str
    actions: frozenset[str]
    unresolved: frozenset[str]
    alerts: tuple[str, ...]
    task_completed: bool
    use_errors: int
    completion_seconds: float | None
    override_used: bool | None = None
    override_authorized: bool | None = None
    probabilities: tuple[tuple[str, float], ...] = ()

    def __post_init__(self) -> None:
        if self.use_errors < 0:
            raise ValueError("use_errors cannot be negative")
        if self.completion_seconds is not None and self.completion_seconds < 0:
            raise ValueError("completion_seconds cannot be negative")
        if any(not 0 <= probability <= 1 for _, probability in self.probabilities):
            raise ValueError("probabilities must be between zero and one")


@dataclass(frozen=True)
class Mitigation:
    mitigation_id: str
    description: str
    test_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _ID.fullmatch(self.mitigation_id) or not self.description.strip():
            raise ValueError("mitigations require stable identifiers and descriptions")
        if not self.test_refs or any(not ref.strip() for ref in self.test_refs):
            raise ValueError("every mitigation must trace to at least one test")


@dataclass(frozen=True)
class Hazard:
    hazard_id: str
    unsafe_condition: str
    severity: str
    status: str
    mitigations: tuple[Mitigation, ...]

    def __post_init__(self) -> None:
        if not _ID.fullmatch(self.hazard_id) or not self.unsafe_condition.strip():
            raise ValueError("hazards require stable identifiers and an unsafe condition")
        if self.severity not in {"minor", "major", "critical", "catastrophic"}:
            raise ValueError("hazard severity is invalid")
        if self.status not in {"open", "mitigated", "accepted"}:
            raise ValueError("hazard status is invalid")
        if not self.mitigations:
            raise ValueError("hazards require traced mitigations")


@dataclass(frozen=True)
class Approval:
    role: str
    reviewer_id: str
    independent: bool
    signed_at: str
    evidence_ref: str
    report_sha256: str


class EvidenceValidationError(ValueError):
    """Controlled evidence parsing errors collected across the complete payload."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(dict.fromkeys(error for error in errors if error))
        super().__init__("invalid or incomplete controlled evidence: " + "; ".join(self.errors))


@dataclass(frozen=True)
class ValidationReport:
    protocol_ref: str
    case_count: int
    metrics: Mapping[str, Any]
    failures: tuple[str, ...]
    covered_case_kinds: tuple[str, ...]
    hazard_ids: tuple[str, ...]
    results_by_case_kind: Mapping[str, Mapping[str, Any]]
    results_by_subgroup: Mapping[str, Mapping[str, Any]]

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "protocolRef": self.protocol_ref,
            "caseCount": self.case_count,
            "metrics": dict(self.metrics),
            "failures": list(self.failures),
            "coveredCaseKinds": list(self.covered_case_kinds),
            "hazardIds": list(self.hazard_ids),
            "resultsByCaseKind": {key: dict(value) for key, value in self.results_by_case_kind.items()},
            "resultsBySubgroup": {key: dict(value) for key, value in self.results_by_subgroup.items()},
        }

    @property
    def sha256(self) -> str:
        canonical = json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReleaseDecision:
    approved: bool
    failures: tuple[str, ...]


class ClinicalSafetyCase:
    """Evaluate a complete case set and bind human approvals to the resulting report."""

    def evaluate(
        self,
        protocol: ValidationProtocol,
        cases: Sequence[ClinicalCase],
        observations: Sequence[CaseObservation],
        hazards: Sequence[Hazard],
        evidence_tests: Mapping[str, bool] | None = None,
    ) -> ValidationReport:
        failures: list[str] = []
        case_by_id = _index_unique(cases, lambda item: item.case_id, "case", failures)
        observation_by_id = _index_unique(observations, lambda item: item.case_id, "observation", failures)
        hazard_by_id = _index_unique(hazards, lambda item: item.hazard_id, "hazard", failures)
        mitigation_by_id: dict[str, Mitigation] = {}
        for hazard in hazards:
            for mitigation in hazard.mitigations:
                if mitigation.mitigation_id in mitigation_by_id:
                    failures.append(f"duplicate mitigation identifier: {mitigation.mitigation_id}")
                else:
                    mitigation_by_id[mitigation.mitigation_id] = mitigation
        required_kinds = set(CaseKind)
        covered_kinds = {case.kind for case in cases}
        missing_kinds = sorted(kind.value for kind in required_kinds - covered_kinds)
        if missing_kinds:
            failures.append("missing case kinds: " + ", ".join(missing_kinds))
        missing_results = sorted(set(case_by_id) - set(observation_by_id))
        unexpected_results = sorted(set(observation_by_id) - set(case_by_id))
        if missing_results:
            failures.append("missing case observations: " + ", ".join(missing_results))
        if unexpected_results:
            failures.append("observations without authored cases: " + ", ".join(unexpected_results))
        if not hazards:
            failures.append("hazard log is empty")
        open_hazards = sorted(hazard.hazard_id for hazard in hazard_by_id.values() if hazard.status == "open")
        if open_hazards:
            failures.append("open hazards: " + ", ".join(open_hazards))

        for hazard in hazards:
            for mitigation in hazard.mitigations:
                for test_ref in mitigation.test_refs:
                    if evidence_tests is None or test_ref not in evidence_tests:
                        failures.append(f"mitigation test evidence missing: {test_ref} ({mitigation.mitigation_id})")
                    elif evidence_tests[test_ref] is not True:
                        failures.append(f"mitigation test did not pass: {test_ref} ({mitigation.mitigation_id})")

        pairs = [
            (case_by_id[case_id], observation_by_id[case_id])
            for case_id in sorted(set(case_by_id) & set(observation_by_id))
        ]
        metrics = _metrics_for(pairs, failures)
        by_case_kind = _group_metrics(pairs, lambda case: case.kind.value)
        by_subgroup = _group_metrics(pairs, lambda case: case.subgroup or _UNSPECIFIED_SUBGROUP)
        brier_score = metrics["brierScore"]
        comparisons = (
            (metrics["unsafeOmissionRate"] > protocol.max_unsafe_omission_rate, "unsafe omission threshold exceeded"),
            (metrics["unsafeCommissionRate"] > protocol.max_unsafe_commission_rate, "unsafe commission threshold exceeded"),
            (metrics["concordance"] < protocol.min_concordance, "clinical concordance threshold not met"),
            (metrics["alertsPerCase"] > protocol.max_alerts_per_case, "alert burden threshold exceeded"),
            (metrics["taskCompletionRate"] < protocol.min_task_completion_rate, "human-factors completion threshold not met"),
            (metrics["useErrorRate"] > protocol.max_use_error_rate, "human-factors use-error threshold exceeded"),
            (metrics["overrideWorkflowFailures"] > 0, "override workflow failures observed"),
            (
                protocol.max_brier_score is not None
                and brier_score != "not applicable"
                and brier_score > protocol.max_brier_score,
                "calibration threshold not met",
            ),
        )
        failures.extend(message for failed, message in comparisons if failed)
        return ValidationReport(
            protocol.evidence_ref,
            len(cases),
            metrics,
            tuple(failures),
            tuple(sorted(kind.value for kind in covered_kinds)),
            tuple(sorted(hazard_by_id)),
            by_case_kind,
            by_subgroup,
        )

    def release_decision(self, report: ValidationReport, approvals: Sequence[Approval]) -> ReleaseDecision:
        failures = list(report.failures)
        by_role: dict[str, Approval] = {}
        for approval in approvals:
            if approval.role in by_role:
                failures.append(f"duplicate approval role: {approval.role}")
            by_role[approval.role] = approval
        missing = sorted(_REQUIRED_APPROVALS - set(by_role))
        if missing:
            failures.append("missing human approvals: " + ", ".join(missing))
        for role in sorted(_REQUIRED_APPROVALS & set(by_role)):
            approval = by_role[role]
            if not all((approval.reviewer_id.strip(), approval.signed_at.strip(), approval.evidence_ref.strip())):
                failures.append(f"{role} approval is incomplete")
            if approval.report_sha256 != report.sha256:
                failures.append(f"{role} approval is not bound to this report")
        psychiatrist = by_role.get("independentPsychiatrist")
        safety_officer = by_role.get("clinicalSafetyOfficer")
        if psychiatrist and not psychiatrist.independent:
            failures.append("psychiatrist review is not independent")
        if psychiatrist and safety_officer and psychiatrist.reviewer_id == safety_officer.reviewer_id:
            failures.append("psychiatrist reviewer and Clinical Safety Officer must be distinct")
        return ReleaseDecision(not failures, tuple(dict.fromkeys(failures)))


def _index_unique(items: Iterable[Any], key: Any, label: str, failures: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in items:
        identifier = key(item)
        if identifier in result:
            failures.append(f"duplicate {label} identifier: {identifier}")
            continue
        result[identifier] = item
    return result


def _group_metrics(
    pairs: Sequence[tuple[ClinicalCase, CaseObservation]],
    group_key: Any,
) -> dict[str, Mapping[str, Any]]:
    groups: dict[str, list[tuple[ClinicalCase, CaseObservation]]] = {}
    for case, observation in pairs:
        groups.setdefault(group_key(case), []).append((case, observation))
    return {key: _metrics_for(group) for key, group in sorted(groups.items())}


def _metrics_for(
    pairs: Sequence[tuple[ClinicalCase, CaseObservation]],
    failures: list[str] | None = None,
) -> dict[str, Any]:
    omissions = commissions = required_total = prohibited_total = 0
    concordances: list[float] = []
    expected_unresolved = observed_unresolved = unresolved_mismatches = 0
    alert_count = completed = use_errors = 0
    completion_times: list[float] = []
    brier_terms: list[float] = []
    override_failures = 0

    for case, observed in pairs:
        omissions += len(case.expected_actions - observed.actions)
        commissions += len(case.prohibited_actions & observed.actions)
        required_total += len(case.expected_actions)
        prohibited_total += len(case.prohibited_actions)
        union = case.expected_actions | observed.actions
        concordances.append(len(case.expected_actions & observed.actions) / len(union) if union else 1.0)
        expected_unresolved += len(case.expected_unresolved)
        observed_unresolved += len(observed.unresolved)
        if case.expected_unresolved != observed.unresolved:
            unresolved_mismatches += 1
            if failures is not None:
                failures.append(
                    f"unresolved data mismatch for {case.case_id}: expected {sorted(case.expected_unresolved)}, observed {sorted(observed.unresolved)}"
                )
        alert_count += len(observed.alerts)
        completed += int(observed.task_completed)
        use_errors += observed.use_errors
        if observed.completion_seconds is not None:
            completion_times.append(observed.completion_seconds)
        if observed.override_used is True and observed.override_authorized is not True:
            override_failures += 1
            if failures is not None:
                failures.append(f"override authorization invalid for {case.case_id}")
        if observed.override_used is not True and observed.override_authorized is True:
            override_failures += 1
            if failures is not None:
                failures.append(f"override authorization present without override use for {case.case_id}")
        if case.expected_override is not None and observed.override_used != case.expected_override:
            override_failures += 1
            if failures is not None:
                failures.append(f"expected override behavior not observed for {case.case_id}")
        expected_probability = dict(case.calibration_outcomes)
        for label, probability in observed.probabilities:
            if label in expected_probability:
                brier_terms.append((probability - int(expected_probability[label])) ** 2)

    evaluated = len(pairs)
    omission_rate = omissions / required_total if required_total else 0.0
    commission_rate = commissions / prohibited_total if prohibited_total else 0.0
    concordance = statistics.fmean(concordances) if concordances else 0.0
    alerts_per_case = alert_count / evaluated if evaluated else math.inf
    completion_rate = completed / evaluated if evaluated else 0.0
    use_error_rate = use_errors / evaluated if evaluated else math.inf
    brier_score: float | str = statistics.fmean(brier_terms) if brier_terms else "not applicable"
    completion_distribution = _completion_distribution(completion_times)
    return {
        "caseCount": evaluated,
        "unsafeOmissionCount": omissions,
        "unsafeOmissionRate": omission_rate,
        "unsafeCommissionCount": commissions,
        "unsafeCommissionRate": commission_rate,
        "concordance": concordance,
        "brierScore": brier_score,
        "applicableCalibrationOutcomeCount": len(brier_terms),
        "expectedUnresolvedDataCount": expected_unresolved,
        "unresolvedDataCount": observed_unresolved,
        "unresolvedDataMismatchCount": unresolved_mismatches,
        "alertsPerCase": alerts_per_case,
        "taskCompletionRate": completion_rate,
        "useErrorRate": use_error_rate,
        "medianCompletionSeconds": completion_distribution["medianSeconds"],
        "completionTimeDistribution": completion_distribution,
        "alertBurden": {"totalAlerts": alert_count, "alertsPerCase": alerts_per_case},
        "taskCompletion": {"completedCases": completed, "completionRate": completion_rate},
        "useErrors": {"total": use_errors, "rate": use_error_rate},
        "overrideWorkflowFailures": override_failures,
    }


def _completion_distribution(completion_times: Sequence[float]) -> dict[str, float | int | None]:
    if not completion_times:
        return {"count": 0, "minSeconds": None, "medianSeconds": None, "p95Seconds": None, "maxSeconds": None}
    ordered = sorted(completion_times)
    p95_index = min(len(ordered) - 1, max(0, math.ceil(len(ordered) * 0.95) - 1))
    return {
        "count": len(ordered),
        "minSeconds": ordered[0],
        "medianSeconds": statistics.median(ordered),
        "p95Seconds": ordered[p95_index],
        "maxSeconds": ordered[-1],
    }
