import unittest

from tests.test_tp13_ddi_check import primary_plan
from treatment_plan.ddi_check import DdiMedicationChecker, Medication


class FailingDdiPort:
    async def check(self, request):
        raise TimeoutError("synthetic timeout")


class TP13CheckerFailureTests(unittest.IsolatedAsyncioTestCase):
    async def test_checker_failure_is_bound_to_plan_and_never_claims_no_interactions(self):
        plan = primary_plan()
        result = await DdiMedicationChecker(FailingDdiPort()).check(
            plan, (Medication("Current drug", "111", "RxNorm"),)
        )

        self.assertFalse(result.checker_succeeded)
        self.assertEqual(result.failure.code, "checker-failed")
        self.assertEqual(result.plan_semantic_hash, plan.semantic_hash)
        self.assertTrue(result.medication_set_hash.startswith("sha256:"))
        self.assertFalse(result.allows_no_interactions_claim)
        self.assertNotIn("No interactions", result.interaction_statement)


if __name__ == "__main__":
    unittest.main()
