import unittest
from dataclasses import replace

from scripts.check_tp21_clinical_safety_case import evaluate_payloads
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


def protocol() -> ValidationProtocol:
    return ValidationProtocol("controlled://protocol/TP-21/v1", 0, 0, 1, 2, 1, 0, 0.1)


def cases() -> list[ClinicalCase]:
    result = []
    for index, kind in enumerate(CaseKind, start=1):
        result.append(
            ClinicalCase(
                f"CASE-TP-{index:03d}", kind, "psychiatrist", f"controlled://case/{index}",
                expected_actions=frozenset({f"action-{index}"}),
                prohibited_actions=frozenset({f"unsafe-{index}"}),
                subgroup="approved-subgroup" if kind is CaseKind.SUBGROUP else None,
                expected_override=True if kind is CaseKind.OVERRIDE_WORKFLOW else None,
                calibration_outcomes=((f"outcome-{index}", True),),
            )
        )
    return result


def observations(source: list[ClinicalCase]) -> list[CaseObservation]:
    return [
        CaseObservation(
            item.case_id, item.expected_actions, frozenset(), ("review",), True, 0, 20,
            override_used=(True if item.kind is CaseKind.OVERRIDE_WORKFLOW else None),
            override_authorized=(True if item.kind is CaseKind.OVERRIDE_WORKFLOW else None),
            probabilities=((item.calibration_outcomes[0][0], 0.9),),
        )
        for item in source
    ]


def hazards(status: str = "mitigated") -> list[Hazard]:
    return [Hazard("HZ-TEST-001", "unsafe output", "critical", status, (Mitigation("MIT-TEST-001", "gate output", ("tests/test_tp21_clinical_validation.py",)),))]


def evidence_tests() -> dict[str, bool]:
    return {"tests/test_tp21_clinical_validation.py": True}


class TP21ClinicalValidationTests(unittest.TestCase):
    def test_measures_required_clinical_and_human_factors_metrics(self):
        authored = cases()
        report = ClinicalSafetyCase().evaluate(protocol(), authored, observations(authored), hazards(), evidence_tests())
        self.assertEqual(0, report.metrics["unsafeOmissionCount"])
        self.assertEqual(0, report.metrics["unsafeCommissionCount"])
        self.assertEqual(1, report.metrics["concordance"])
        self.assertAlmostEqual(0.01, report.metrics["brierScore"])
        self.assertEqual(1, report.metrics["alertsPerCase"])
        self.assertEqual(1, report.metrics["taskCompletionRate"])
        self.assertEqual(20, report.metrics["medianCompletionSeconds"])
        self.assertEqual(20, report.metrics["completionTimeDistribution"]["medianSeconds"])
        self.assertEqual(1, report.metrics["alertBurden"]["alertsPerCase"])
        self.assertEqual(1, report.metrics["taskCompletion"]["completionRate"])
        self.assertEqual(0, report.metrics["useErrors"]["total"])
        self.assertEqual((), report.failures)

    def test_unsafe_results_open_hazards_and_incomplete_coverage_block(self):
        authored = cases()[:-1]
        observed = observations(authored)
        first = observed[0]
        observed[0] = CaseObservation(first.case_id, frozenset({"unsafe-1"}), frozenset({"allergy"}), tuple(f"alert-{index}" for index in range(20)), False, 1, 40)
        report = ClinicalSafetyCase().evaluate(protocol(), authored, observed, hazards("open"), evidence_tests())
        joined = " ".join(report.failures)
        for expected in ("missing case kinds", "open hazards", "unsafe omission", "unsafe commission", "alert burden", "human-factors"):
            self.assertIn(expected, joined)
        self.assertEqual(1, report.metrics["unresolvedDataCount"])

    def test_release_requires_distinct_external_human_approvals_bound_to_report(self):
        authored = cases()
        safety_case = ClinicalSafetyCase()
        report = safety_case.evaluate(protocol(), authored, observations(authored), hazards(), evidence_tests())
        blocked = safety_case.release_decision(report, [])
        self.assertFalse(blocked.approved)
        approvals = [
            Approval("independentPsychiatrist", "reviewer-1", True, "2026-07-16T00:00:00Z", "controlled://review/1", report.sha256),
            Approval("clinicalSafetyOfficer", "reviewer-2", False, "2026-07-16T00:00:00Z", "controlled://signoff/1", report.sha256),
        ]
        self.assertTrue(safety_case.release_decision(report, approvals).approved)
        approvals[0] = Approval("independentPsychiatrist", "reviewer-1", True, "2026-07-16T00:00:00Z", "controlled://review/1", "wrong")
        self.assertFalse(safety_case.release_decision(report, approvals).approved)

    def test_compares_unresolved_data_and_reports_case_kind_and_subgroup_results(self):
        authored = cases()
        authored[0] = replace(authored[0], expected_unresolved=frozenset({"allergy"}))
        report = ClinicalSafetyCase().evaluate(protocol(), authored, observations(authored), hazards(), evidence_tests())

        self.assertEqual(1, report.metrics["unresolvedDataMismatchCount"])
        self.assertIn("unresolved data mismatch", " ".join(report.failures))
        self.assertEqual(1, report.results_by_case_kind[CaseKind.REFERENCE.value]["caseCount"])
        self.assertEqual(len(CaseKind) - 1, report.results_by_subgroup["unspecified"]["caseCount"])

    def test_calibration_is_not_applicable_without_probabilistic_outcomes(self):
        authored = cases()
        observed = [replace(item, probabilities=()) for item in observations(authored)]
        report = ClinicalSafetyCase().evaluate(protocol(), authored, observed, hazards(), evidence_tests())

        self.assertEqual("not applicable", report.metrics["brierScore"])
        self.assertNotIn("calibration threshold", " ".join(report.failures))

    def test_override_requires_authorization_and_expected_behavior(self):
        authored = cases()
        observed = observations(authored)
        override_index = next(index for index, item in enumerate(authored) if item.kind is CaseKind.OVERRIDE_WORKFLOW)
        override_observation = observed[override_index]
        observed[override_index] = replace(override_observation, override_authorized=False)
        report = ClinicalSafetyCase().evaluate(protocol(), authored, observed, hazards(), evidence_tests())

        self.assertIn("override authorization", " ".join(report.failures))

    def test_requires_unique_hazard_and_mitigation_ids_and_passed_test_evidence(self):
        duplicate_hazard = Hazard("HZ-TEST-001", "second unsafe output", "major", "mitigated", (Mitigation("MIT-TEST-001", "second gate", ("missing-test",)),))
        report = ClinicalSafetyCase().evaluate(
            protocol(), cases(), observations(cases()), hazards() + [duplicate_hazard], {"tests/test_tp21_clinical_validation.py": False}
        )

        joined = " ".join(report.failures)
        self.assertIn("duplicate hazard identifier", joined)
        self.assertIn("duplicate mitigation identifier", joined)
        self.assertIn("mitigation test did not pass", joined)
        self.assertIn("mitigation test evidence missing", joined)

    def test_adapter_aggregates_malformed_protocol_and_evidence_errors(self):
        with self.assertRaises(EvidenceValidationError) as context:
            evaluate_payloads(
                {"protocol": {"evidenceRef": ""}},
                {"observations": []},
                {"hazards": []},
                {"approvals": []},
            )

        message = str(context.exception)
        self.assertIn("protocol.maxUnsafeOmissionRate", message)
        self.assertIn("protocol.maxUnsafeCommissionRate", message)
        self.assertIn("protocol.minConcordance", message)
        self.assertIn("protocol.maxAlertsPerCase", message)
        self.assertIn("protocol.minTaskCompletionRate", message)
        self.assertIn("protocol.maxUseErrorRate", message)
        self.assertIn("controlled evidence", message)

    def test_protocol_reports_all_invalid_thresholds(self):
        with self.assertRaises(ValueError) as context:
            ValidationProtocol("", -1, 2, -1, -1, 2, -1, 2)

        message = str(context.exception)
        self.assertIn("controlled evidence reference", message)
        self.assertIn("max_unsafe_omission_rate", message)
        self.assertIn("max_unsafe_commission_rate", message)
        self.assertIn("min_concordance", message)
        self.assertIn("max_alerts_per_case", message)
        self.assertIn("max_brier_score", message)


if __name__ == "__main__":
    unittest.main()
