import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("release_gate", ROOT / "scripts" / "check_tp01_release_gate.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.matrix = json.loads((ROOT / "governance" / "scope-matrix.v1.json").read_text(encoding="utf-8"))

    def test_draft_is_blocked(self):
        self.assertTrue(MODULE.evaluate(self.matrix))

    def test_complete_approved_matrix_passes(self):
        m = copy.deepcopy(self.matrix)
        m["status"] = "approved"
        for gate in m["decisionGates"]:
            gate.update(status="approved", decision="approved decision")
        for role in MODULE.REQUIRED_ROLES:
            m["owners"][role] = f"Named {role} owner"
            m["approvals"].append({"role": role, "name": m["owners"][role], "signedAt": "2026-07-13T12:00:00Z", "signatureRef": f"approval:{role}", "scopeHash": "sha256:" + "a" * 64})
        m["intendedUse"].update(decision="research-only evaluation", researchOnly=True, jurisdictions=["US"])
        m["clinicalScope"].update(supportedDiagnoses=["approved pathway"], supportedPopulation="approved population", emergencyBehavior="approved escalation behavior")
        m["knowledgeAuthority"]["approvedSources"] = [{"name": "approved source", "version": "approved version"}]
        m["notSupported"] = [{"case": "all cases outside approved scope", "behavior": "reject_generation"}]
        m["regulatoryAssessment"].update(status="completed", classification="assessed", jurisdictionAnalysis="evidence-based analysis", assessor="Named assessor", assessedAt="2026-07-13T12:00:00Z", evidenceRef="regulatory:assessment")
        m["clinicalValidation"].update(status="completed", reportRef="validation:report", approvedByClinicalSafetyOfficer=True, approvedAt="2026-07-13T12:00:00Z")
        self.assertEqual([], MODULE.evaluate(m))


if __name__ == "__main__":
    unittest.main()
