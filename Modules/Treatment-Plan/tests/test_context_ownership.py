import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("context_check", ROOT / "scripts" / "check_context_ownership.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ContextOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "governance" / "context-ownership.v1.json").read_text(encoding="utf-8"))

    def test_registry_is_valid(self):
        self.assertEqual([], MODULE.evaluate(self.registry))

    def test_duplicate_owner_record_is_rejected(self):
        changed = copy.deepcopy(self.registry)
        changed["entities"].append({"entity": "Patient", "owner": "Treatment Plan", "id": "patientId", "idKind": "uuid"})
        self.assertTrue(any("multiple ownership" in failure for failure in MODULE.evaluate(changed)))

    def test_cross_module_database_access_is_rejected(self):
        changed = copy.deepcopy(self.registry)
        changed["relationshipPolicy"]["crossDatabaseAccessAllowed"] = True
        self.assertTrue(any("crossDatabaseAccessAllowed" in failure for failure in MODULE.evaluate(changed)))


if __name__ == "__main__":
    unittest.main()
