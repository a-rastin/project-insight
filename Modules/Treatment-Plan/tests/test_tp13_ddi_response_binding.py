import unittest

from tests.test_tp13_ddi_check import RecordingDdiPort, primary_plan
from tests.test_tp13_ddi_hash_binding import no_interaction_response
from treatment_plan.ddi_check import DdiMedicationChecker


class TP13ResponseBindingTests(unittest.IsolatedAsyncioTestCase):
    async def test_mismatched_checker_hash_fails_closed(self):
        def stale_response(request):
            response = no_interaction_response(request)
            response["medicationSetHash"] = "sha256:" + "0" * 64
            return response

        result = await DdiMedicationChecker(RecordingDdiPort(stale_response)).check(
            primary_plan(), ()
        )

        self.assertFalse(result.checker_succeeded)
        self.assertEqual(result.failure.code, "invalid-response")
        self.assertFalse(result.allows_no_interactions_claim)
        self.assertNotIn("No interactions", result.interaction_statement)


if __name__ == "__main__":
    unittest.main()
