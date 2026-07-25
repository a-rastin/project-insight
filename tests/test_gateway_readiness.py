import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "deployment"))

from gateway_readiness import aggregate_readiness  # noqa: E402


class GatewayReadinessTests(unittest.TestCase):
    def test_all_required_modules_ready_marks_gateway_ready(self):
        with patch("gateway_readiness.probe", return_value={"ok": True}):
            status, payload = aggregate_readiness()
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        self.assertEqual("unified-gateway", payload["service"])
        self.assertEqual(9, len(payload["modules"]))

    def test_required_module_failure_marks_gateway_unready(self):
        def probe(module_id, _url):
            return {"ok": module_id != "diagnosis", "reason": "clinical_scope_unresolved"}

        with patch("gateway_readiness.probe", side_effect=probe):
            status, payload = aggregate_readiness()
        self.assertEqual(503, status)
        self.assertFalse(payload["ok"])
        self.assertEqual("clinical_scope_unresolved", payload["modules"]["diagnosis"]["reason"])


if __name__ == "__main__":
    unittest.main()
