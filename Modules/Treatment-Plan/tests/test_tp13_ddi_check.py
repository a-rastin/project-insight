import unittest

from treatment_plan.ddi_check import DdiMedicationChecker, Medication
from tests.test_tp12_primary_plan import bundle, facts
from treatment_plan.primary_plan import PrimaryPlanSynthesizer
from treatment_plan.safety_policy import (
    ProbabilisticRecommendation,
    SafetyFacts,
    SafetyPolicy,
)


def primary_plan():
    safety = SafetyPolicy().apply(
        (
            ProbabilisticRecommendation("candidate-a", .8),
            ProbabilisticRecommendation("candidate-b", .2),
        ),
        SafetyFacts(),
    )
    return PrimaryPlanSynthesizer().synthesize(
        bundle(), safety, facts(), timezone="America/Los_Angeles"
    )


class RecordingDdiPort:
    def __init__(self, response_factory):
        self.response_factory = response_factory
        self.requests = []

    async def check(self, request):
        self.requests.append(request)
        return self.response_factory(request)


class TP13DdiCheckTests(unittest.IsolatedAsyncioTestCase):
    async def test_checks_current_and_exact_proposed_set_and_preserves_evidence(self):
        def response(request):
            return {
                "schemaVersion": "1.0.0",
                "checkId": "ddi-check-13",
                "medicationSetHash": request["medicationSetHash"],
                "knowledgeBaseId": "synthetic-kb",
                "knowledgeBaseVersion": "2026.07.14",
                "normalizedMedications": [
                    {
                        "inputIndex": 0,
                        "conceptId": "rxnorm:111",
                        "codeSystem": "RxNorm",
                        "display": "Synthetic current drug",
                    },
                    {
                        "inputIndex": 1,
                        "conceptId": "rxnorm:222",
                        "codeSystem": "RxNorm",
                        "display": "Synthetic proposed drug",
                    },
                ],
                "unresolvedMedications": [],
                "pairsChecked": [{"leftInputIndex": 0, "rightInputIndex": 1}],
                "alerts": [{
                    "alertId": "alert-1",
                    "medicationInputIndexes": [0, 1],
                    "severity": "high",
                    "mechanism": "Synthetic mechanism",
                    "evidence": [{"sourceId": "evidence-1", "summary": "Synthetic evidence"}],
                    "recommendedAction": "Review the combination.",
                }],
            }

        port = RecordingDdiPort(response)
        plan = primary_plan()
        result = await DdiMedicationChecker(port).check(
            plan,
            (Medication(
                original_text="Current drug 10 mg",
                medication_code="111",
                code_system="RxNorm",
                dose="10 mg",
                route="oral",
                frequency="daily",
            ),),
        )

        sent = port.requests[0]
        self.assertEqual([item["source"] for item in sent["medications"]], ["current", "proposed"])
        self.assertEqual(sent["medications"][1]["medicationCode"], plan.pharmacotherapy.value["medicationCode"])
        self.assertEqual(result.medication_set_hash, sent["medicationSetHash"])
        self.assertEqual(result.plan_semantic_hash, plan.semantic_hash)
        self.assertEqual(result.knowledge_base_version, "2026.07.14")
        self.assertEqual(result.normalized_medications[1].concept_id, "rxnorm:222")
        self.assertEqual(result.interactions[0].severity, "high")
        self.assertEqual(result.interactions[0].evidence[0]["sourceId"], "evidence-1")
        self.assertEqual(result.interactions[0].recommended_action, "Review the combination.")
        self.assertFalse(result.allows_no_interactions_claim)


if __name__ == "__main__":
    unittest.main()
