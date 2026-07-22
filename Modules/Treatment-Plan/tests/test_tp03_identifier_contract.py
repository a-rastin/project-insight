import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("identifier_contract", ROOT / "scripts" / "check_identifier_contract.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class SharedIdentifierContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / "contracts" / "identifier-transport-contract.v1.json").read_text(encoding="utf-8"))

    def test_committed_contract_conforms(self):
        self.assertEqual([], MODULE.evaluate(self.contract))

    def test_alias_may_not_be_a_foreign_key(self):
        changed = copy.deepcopy(self.contract)
        changed["patientAlias"]["foreignKeyAllowed"] = True
        self.assertIn("patientCode foreignKeyAllowed must be False", MODULE.evaluate(changed))

    def test_alias_collision_must_fail_closed(self):
        changed = copy.deepcopy(self.contract)
        changed["patientAlias"]["resolution"]["collision"]["status"] = 200
        self.assertIn("alias collision must return HTTP 409", MODULE.evaluate(changed))

    def test_encounter_cannot_be_inferred_from_time(self):
        changed = copy.deepcopy(self.contract)
        changed["encounter"]["selectionByTimestampForbidden"] = False
        self.assertIn("encounter rule selectionByTimestampForbidden must be true", MODULE.evaluate(changed))

    def test_correlation_id_must_propagate(self):
        changed = copy.deepcopy(self.contract)
        changed["headers"]["X-Correlation-ID"]["forwardUnchanged"] = False
        self.assertIn("X-Correlation-ID must be forwarded unchanged", MODULE.evaluate(changed))

    def test_mutation_requires_etag_precondition(self):
        changed = copy.deepcopy(self.contract)
        del changed["headers"]["If-Match"]
        self.assertTrue(any("If-Match" in failure for failure in MODULE.evaluate(changed)))

    def test_only_utc_instants_are_accepted(self):
        pattern = self.contract["time"]["instantPattern"]
        self.assertIsNotNone(re.fullmatch(pattern, "2026-07-13T11:22:33Z"))
        self.assertIsNone(re.fullmatch(pattern, "2026-07-13T04:22:33-07:00"))

    def test_idempotency_key_reuse_with_changed_payload_conflicts(self):
        conflict = self.contract["behavior"]["idempotencyConflict"]
        self.assertEqual((409, "idempotency_key_reused"), (conflict["status"], conflict["code"]))


if __name__ == "__main__":
    unittest.main()
