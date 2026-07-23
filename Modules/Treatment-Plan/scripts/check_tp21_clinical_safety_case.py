"""Fail-closed TP-21 clinical validation and safety-case gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).parents[1]))

from treatment_plan.clinical_validation import (
    Approval,
    CaseKind,
    CaseObservation,
    ClinicalCase,
    ClinicalSafetyCase,
    EvidenceValidationError,
    Hazard,
    Mitigation,
    ValidationProtocol,
)


ROOT = Path(__file__).parents[1]
DEFAULT_DIR = ROOT / "governance" / "clinical-validation"


def evaluate_payloads(cases_payload: dict[str, Any], observations_payload: dict[str, Any], hazard_payload: dict[str, Any], approvals_payload: dict[str, Any]):
    errors: list[str] = []
    raw_protocol = cases_payload.get("protocol") or {}
    if not isinstance(raw_protocol, Mapping):
        errors.append("protocol: expected an object")
        raw_protocol = {}
    protocol_values: dict[str, Any] = {"evidence_ref": str(raw_protocol.get("evidenceRef") or "")}
    protocol_fields = (
        ("maxUnsafeOmissionRate", "max_unsafe_omission_rate"),
        ("maxUnsafeCommissionRate", "max_unsafe_commission_rate"),
        ("minConcordance", "min_concordance"),
        ("maxAlertsPerCase", "max_alerts_per_case"),
        ("minTaskCompletionRate", "min_task_completion_rate"),
        ("maxUseErrorRate", "max_use_error_rate"),
    )
    for payload_key, field_name in protocol_fields:
        try:
            protocol_values[field_name] = float(raw_protocol[payload_key])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"protocol.{payload_key}: {exc}")
    if raw_protocol.get("maxBrierScore") is not None:
        try:
            protocol_values["max_brier_score"] = float(raw_protocol["maxBrierScore"])
        except (TypeError, ValueError) as exc:
            errors.append(f"protocol.maxBrierScore: {exc}")
    else:
        protocol_values["max_brier_score"] = None
    protocol = None
    if len(protocol_values) == len(protocol_fields) + 2:
        try:
            protocol = ValidationProtocol(**protocol_values)
        except ValueError as exc:
            errors.append(f"protocol: {exc}")

    cases: list[ClinicalCase] = []
    for index, item in enumerate(_items(cases_payload, "cases", errors)):
        try:
            cases.append(
                ClinicalCase(
                    case_id=item["caseId"], kind=CaseKind(item["kind"]), author_role=item["authorRole"],
                    author_evidence_ref=item["authorEvidenceRef"],
                    expected_actions=frozenset(item.get("expectedActions", [])),
                    prohibited_actions=frozenset(item.get("prohibitedActions", [])),
                    expected_unresolved=frozenset(item.get("expectedUnresolved", [])),
                    subgroup=item.get("subgroup"), expected_override=item.get("expectedOverride"),
                    calibration_outcomes=tuple((entry["label"], bool(entry["outcome"])) for entry in item.get("calibrationOutcomes", [])),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"cases[{index}]: {exc}")

    observations: list[CaseObservation] = []
    for index, item in enumerate(_items(observations_payload, "observations", errors)):
        try:
            observations.append(
                CaseObservation(
                    case_id=item["caseId"], actions=frozenset(item.get("actions", [])),
                    unresolved=frozenset(item.get("unresolved", [])), alerts=tuple(item.get("alerts", [])),
                    task_completed=bool(item.get("taskCompleted", False)), use_errors=int(item.get("useErrors", 0)),
                    completion_seconds=item.get("completionSeconds"), override_used=item.get("overrideUsed"),
                    override_authorized=item.get("overrideAuthorized"),
                    probabilities=tuple((entry["label"], float(entry["probability"])) for entry in item.get("probabilities", [])),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"observations[{index}]: {exc}")

    hazards: list[Hazard] = []
    for index, item in enumerate(_items(hazard_payload, "hazards", errors)):
        mitigations: list[Mitigation] = []
        raw_mitigations = item.get("mitigations", [])
        if not isinstance(raw_mitigations, list):
            errors.append(f"hazards[{index}].mitigations: expected a list")
            raw_mitigations = []
        for mitigation_index, entry in enumerate(raw_mitigations):
            try:
                mitigations.append(Mitigation(entry["mitigationId"], entry["description"], tuple(entry.get("testRefs", []))))
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"hazards[{index}].mitigations[{mitigation_index}]: {exc}")
        try:
            hazards.append(
                Hazard(
                    hazard_id=item["hazardId"], unsafe_condition=item["unsafeCondition"],
                    severity=item["severity"], status=item["status"], mitigations=tuple(mitigations),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"hazards[{index}]: {exc}")

    approvals: list[Approval] = []
    for index, item in enumerate(_items(approvals_payload, "approvals", errors)):
        try:
            approvals.append(
                Approval(
                    role=item["role"], reviewer_id=item["reviewerId"], independent=bool(item.get("independent", False)),
                    signed_at=item["signedAt"], evidence_ref=item["evidenceRef"], report_sha256=item["reportSha256"],
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"approvals[{index}]: {exc}")

    evidence_tests = _evidence_tests(hazard_payload, errors)
    if errors:
        raise EvidenceValidationError(errors)
    safety_case = ClinicalSafetyCase()
    report = safety_case.evaluate(protocol, cases, observations, hazards, evidence_tests)
    return report, safety_case.release_decision(report, approvals)


def _items(payload: Mapping[str, Any], key: str, errors: list[str]) -> list[Mapping[str, Any]]:
    raw_items = payload.get(key, [])
    if not isinstance(raw_items, list):
        errors.append(f"{key}: expected a list")
        return []
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(raw_items):
        if not isinstance(item, Mapping):
            errors.append(f"{key}[{index}]: expected an object")
            continue
        result.append(item)
    return result


def _evidence_tests(payload: Mapping[str, Any], errors: list[str]) -> dict[str, bool]:
    evidence_run = payload.get("evidenceRun") or {}
    if not isinstance(evidence_run, Mapping):
        errors.append("evidenceRun: expected an object")
        return {}
    raw_tests = evidence_run.get("tests", {})
    if isinstance(raw_tests, Mapping):
        return {str(test_ref): passed for test_ref, passed in raw_tests.items()}
    if isinstance(raw_tests, list):
        result: dict[str, bool] = {}
        for index, item in enumerate(raw_tests):
            try:
                result[str(item["testRef"])] = item["passed"]
            except (KeyError, TypeError) as exc:
                errors.append(f"evidenceRun.tests[{index}]: {exc}")
        return result
    errors.append("evidenceRun.tests: expected an object or list")
    return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        payloads = [
            json.loads((args.evidence_dir / name).read_text(encoding="utf-8"))
            for name in ("cases.v1.json", "observations.v1.json", "hazard-log.v1.json", "approvals.v1.json")
        ]
        report, decision = evaluate_payloads(*payloads)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print("TP-21 CLINICAL SAFETY GATE: BLOCKED")
        print(f"- invalid or incomplete controlled evidence: {exc}")
        return 1
    if args.as_json:
        print(json.dumps({**report.canonical_payload(), "reportSha256": report.sha256, "approved": decision.approved, "releaseFailures": list(decision.failures)}, indent=2))
    else:
        print("TP-21 CLINICAL SAFETY GATE: " + ("PASSED" if decision.approved else "BLOCKED"))
        print(f"- report sha256: {report.sha256}")
        for failure in decision.failures:
            print(f"- {failure}")
    return 0 if decision.approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
