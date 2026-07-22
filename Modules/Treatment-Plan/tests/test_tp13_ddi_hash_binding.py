import unittest
from dataclasses import replace

from tests.test_tp13_ddi_check import RecordingDdiPort, primary_plan
from treatment_plan.ddi_check import DdiMedicationChecker


def no_interaction_response(request):
    medication = request["medications"][0]
    return {
        "schemaVersion": "1.0.0",
        "checkId": "ddi-no-alerts-13",
        "medicationSetHash": request["medicationSetHash"],
        "knowledgeBaseId": "synthetic-kb",
        "knowledgeBaseVersion": "2026.07.14",
        "normalizedMedications": [{
            "inputIndex": 0,
            "conceptId": "rxnorm:proposed",
            "codeSystem": medication["codeSystem"],
        }],
        "unresolvedMedications": [],
        "pairsChecked": [],
        "alerts": [],
    }


class TP13MedicationSetBindingTests(unittest.IsolatedAsyncioTestCase):
    async def test_proposed_plan_edit_changes_bound_medication_set_hash(self):
        first_plan = primary_plan()
        changed_value = dict(first_plan.pharmacotherapy.value)
        changed_value["dose"] = "different synthetic dose"
        second_plan = replace(
            first_plan,
            pharmacotherapy=replace(first_plan.pharmacotherapy, value=changed_value),
        )
        port = RecordingDdiPort(no_interaction_response)
        checker = DdiMedicationChecker(port)

        first = await checker.check(first_plan, ())
        second = await checker.check(second_plan, ())

        self.assertTrue(first.allows_no_interactions_claim)
        self.assertTrue(second.allows_no_interactions_claim)
        self.assertNotEqual(first.plan_semantic_hash, second.plan_semantic_hash)
        self.assertNotEqual(first.medication_set_hash, second.medication_set_hash)
        self.assertNotEqual(port.requests[0]["idempotencyKey"], port.requests[1]["idempotencyKey"])


if __name__ == "__main__":
    unittest.main()
