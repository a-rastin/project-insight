import unittest

from tests.test_tp13_ddi_check import RecordingDdiPort, primary_plan
from treatment_plan.ddi_check import DdiMedicationChecker, Medication


class TP13PairCoverageTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_normalized_pair_coverage_fails_closed(self):
        def incomplete_response(request):
            return {
                "schemaVersion": "1.0.0",
                "checkId": "ddi-incomplete-pairs-13",
                "medicationSetHash": request["medicationSetHash"],
                "knowledgeBaseId": "synthetic-kb",
                "knowledgeBaseVersion": "2026.07.14",
                "normalizedMedications": [
                    {"inputIndex": 0, "conceptId": "rxnorm:111", "codeSystem": "RxNorm"},
                    {"inputIndex": 1, "conceptId": "rxnorm:222", "codeSystem": "RxNorm"},
                ],
                "unresolvedMedications": [],
                "pairsChecked": [],
                "alerts": [],
            }

        result = await DdiMedicationChecker(RecordingDdiPort(incomplete_response)).check(
            primary_plan(), (Medication("Current drug", "111", "RxNorm"),)
        )

        self.assertFalse(result.checker_succeeded)
        self.assertEqual(result.failure.code, "invalid-response")
        self.assertFalse(result.allows_no_interactions_claim)


if __name__ == "__main__":
    unittest.main()
