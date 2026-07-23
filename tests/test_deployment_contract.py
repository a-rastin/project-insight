import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from check_deployment import DeploymentContractError, check_deployment, load_manifest


ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "deployment" / "manifest.json"


class DeploymentContractTests(unittest.TestCase):
    def test_manifest_declares_unique_runtime_and_proxy_identity(self):
        manifest = load_manifest(MANIFEST)
        check_deployment(ROOT, manifest)

        modules = manifest["modules"]
        self.assertEqual(len(modules), 9)
        self.assertEqual(
            len({module["internalPort"] for module in modules}), len(modules)
        )
        self.assertEqual(
            len({module["proxyPrefix"] for module in modules}), len(modules)
        )

    def test_manifest_requires_startup_migration_and_recovery_contracts(self):
        manifest = load_manifest(MANIFEST)
        for module in manifest["modules"]:
            self.assertEqual("startup", module["migration"]["mode"])
            self.assertTrue(module["migration"]["readinessGate"])
            self.assertTrue(module["volume"]["writable"])
            self.assertTrue(module["backup"]["configured"])
            self.assertTrue(module["restore"]["configured"])
            self.assertTrue(module["retention"]["configured"])
            self.assertTrue(module["retention"]["policyReference"])
            self.assertEqual("SIGTERM", module["shutdown"]["signal"])
            self.assertGreater(module["shutdown"]["timeoutSeconds"], 0)

    def test_duplicate_ports_and_proxy_prefixes_are_rejected(self):
        manifest = load_manifest(MANIFEST)
        broken = copy.deepcopy(manifest)
        broken["modules"][1]["internalPort"] = broken["modules"][0]["internalPort"]
        with self.assertRaises(DeploymentContractError):
            check_deployment(ROOT, broken)

        broken = copy.deepcopy(manifest)
        broken["modules"][1]["proxyPrefix"] = broken["modules"][0]["proxyPrefix"]
        with self.assertRaises(DeploymentContractError):
            check_deployment(ROOT, broken)

    def test_browser_sources_cannot_contain_hard_coded_localhost_urls(self):
        manifest = load_manifest(MANIFEST)
        broken = copy.deepcopy(manifest)
        broken["browserSourceOverrides"] = {
            "Modules/example/public/app.js": "fetch('http://localhost:8000/api')"
        }
        with self.assertRaises(DeploymentContractError):
            check_deployment(ROOT, broken)

    def test_manifest_is_json_and_has_machine_checkable_schema_reference(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual("deployment-manifest-1.0.0", manifest["manifestId"])
        self.assertEqual("deployment/manifest.schema.json", manifest["schema"])
        self.assertTrue((ROOT / manifest["schema"]).is_file())


if __name__ == "__main__":
    unittest.main()
