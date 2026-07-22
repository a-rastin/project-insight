import unittest

from treatment_plan.safety_policy import (
    Disposition,
    POLICY_VERSION,
    ProbabilisticRecommendation,
    SafetyFacts,
    SafetyOutcome,
    SafetyPolicy,
)


class TP11SafetyPolicyTests(unittest.TestCase):
    def test_versioned_policy_applies_all_candidate_safety_dimensions(self):
        candidates = (
            ProbabilisticRecommendation("allergy-drug", .99, substances=("latex",)),
            ProbabilisticRecommendation("contra-drug", .80, contraindication_codes=("condition-x",)),
            ProbabilisticRecommendation("monitor-drug", .70, monitoring_requirement="enhanced"),
            ProbabilisticRecommendation("prior-drug", .60),
            ProbabilisticRecommendation("adherence-drug", .50),
            ProbabilisticRecommendation("known-good", .10, supports_adherence=True),
        )
        facts = SafetyFacts(
            allergies=("LATEX",),
            contraindications=("condition-x",),
            monitoring_capacity="routine",
            prior_response={"prior-drug": "adverse", "known-good": "good"},
            adherence="poor",
        )
        decision = SafetyPolicy().apply(candidates, facts)
        dispositions = {
            item.recommendation.recommendation_id: item.disposition
            for item in decision.recommendations
        }
        self.assertEqual(decision.policy_version, POLICY_VERSION)
        self.assertEqual(dispositions["allergy-drug"], Disposition.EXCLUDED)
        self.assertEqual(dispositions["contra-drug"], Disposition.EXCLUDED)
        self.assertEqual(dispositions["monitor-drug"], Disposition.EXCLUDED)
        self.assertEqual(dispositions["prior-drug"], Disposition.EXCLUDED)
        self.assertEqual(dispositions["adherence-drug"], Disposition.CONDITIONAL)
        self.assertEqual(dispositions["known-good"], Disposition.PREFERRED)
        self.assertEqual(decision.outcome, SafetyOutcome.REVIEW_REQUIRED)
        self.assertTrue(all(trace.summary and trace.evidence for trace in decision.traces))

    def test_urgent_condition_dominates_probability_and_empty_candidate_list(self):
        decision = SafetyPolicy().apply(
            (ProbabilisticRecommendation("outpatient", .001),),
            SafetyFacts(suicide_risk="IMMINENT"),
        )
        self.assertEqual(decision.outcome, SafetyOutcome.EMERGENCY_ESCALATION)
        self.assertTrue(decision.escalation.required)
        self.assertFalse(decision.escalation.action_performed)
        self.assertEqual(decision.urgent_traces[0].rule_id, "imminent-suicide-risk")

        empty = SafetyPolicy().apply((), SafetyFacts(emergency_signals=("active attempt",)))
        self.assertEqual(empty.outcome, SafetyOutcome.EMERGENCY_ESCALATION)
        self.assertEqual(empty.traces[0].rule_id, "emergency-signal")

    def test_exclusion_is_not_overridden_by_prior_benefit_or_probability(self):
        candidate = ProbabilisticRecommendation("candidate-a", 1.0, substances=("agent-a",))
        decision = SafetyPolicy().apply(
            (candidate,),
            SafetyFacts(allergies=("agent-a",), prior_response={"candidate-a": "good"}),
        )
        assessed = decision.recommendations[0]
        self.assertEqual(assessed.disposition, Disposition.EXCLUDED)
        self.assertEqual(
            assessed.trace_rule_ids,
            ("candidate-allergy", "prior-beneficial-response"),
        )
        self.assertEqual(assessed.recommendation.probability, 1.0)

    def test_invalid_probability_and_duplicate_ids_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "probability"):
            SafetyPolicy().apply(
                (ProbabilisticRecommendation("x", float("nan")),), SafetyFacts()
            )
        with self.assertRaisesRegex(ValueError, "unique"):
            SafetyPolicy().apply(
                (
                    ProbabilisticRecommendation("x", .2),
                    ProbabilisticRecommendation("x", .8),
                ),
                SafetyFacts(),
            )


if __name__ == "__main__":
    unittest.main()
