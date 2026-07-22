import unittest

from tests.test_tp13_ddi_check import RecordingDdiPort, primary_plan
from treatment_plan.ddi_check import DdiMedicationChecker, Medication


class TP13UnresolvedIdentityTests(unittest.IsolatedAsyncioTestCase):
    async def test_unresolved_identity_makes_zero_alert_result_indeterminate(self):
        def response(request):
            return {
                "schemaVersion": "1.0.0",
                "checkId": "ddi-unresolved-13",
                "medicationSetHash": request["medicationSetHash"],
                "knowledgeBaseId": "synthetic-kb",
                "knowledgeBaseVersion": "2026.07.14",
                "normalizedMedications": [{
                    "inputIndex": 0,
                    "conceptId": "rxnorm:111",
                    "codeSystem": "RxNorm",
                }],
                "unresolvedMedications": [{
                    "inputIndex": 1,
                    "reason": "ambiguous",
                    "candidates": [
                        {"conceptId": "rxnorm:222", "display": "Candidate one"},
                        {"conceptId": "rxnorm:223", "display": "Candidate two"},
                    ],
                }],
                "pairsChecked": [],
                "alerts": [],
            }

        result = await DdiMedicationChecker(RecordingDdiPort(response)).check(
            primary_plan(),
            (Medication("Current drug", "111", "RxNorm"),),
        )

        self.assertTrue(result.checker_succeeded)
        self.assertEqual(result.unresolved_medications[0].source, "proposed")
        self.assertEqual(result.unresolved_medications[0].reason, "ambiguous")
        self.assertEqual(result.unresolved_medications[0].candidates[1]["conceptId"], "rxnorm:223")
        self.assertFalse(result.allows_no_interactions_claim)
        self.assertNotIn("No interactions", result.interaction_statement)


if __name__ == "__main__":
    unittest.main()
