import copy
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from check_deployment import DeploymentContractError, check_deployment, load_manifest
from verify_unified_deployment import MODULE_SMOKE


ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "deployment" / "manifest.json"


class DeploymentContractTests(unittest.TestCase):
    def test_manifest_declares_unique_runtime_and_proxy_identity(self):
        manifest = load_manifest(MANIFEST)
        check_deployment(ROOT, manifest)

        modules = manifest["modules"]
        self.assertEqual(len(modules), 10)
        self.assertEqual(
            len({module["internalPort"] for module in modules}), len(modules)
        )
        self.assertEqual(
            len({module["proxyPrefix"] for module in modules}), len(modules)
        )

    def test_suicide_risk_has_stable_isolated_deployment_identity(self):
        module = next(module for module in load_manifest(MANIFEST)["modules"] if module["moduleId"] == "suicide-risk")
        self.assertEqual(8111, module["internalPort"])
        self.assertEqual("/api/suicide-risk/v1", module["basePath"])
        self.assertEqual("/modules/suicide-risk", module["proxyPrefix"])
        self.assertEqual("/var/lib/insight/suicide-risk", module["volume"]["mountPath"])

    def test_severity_browser_targets_are_deployed(self):
        source = (ROOT / "Modules" / "Severity-1.1.0" / "public" / "index.html").read_text(encoding="utf-8")
        target_ids = set(re.findall(r"/modules/([a-z0-9-]+)", source))
        target_ids.update(re.findall(r"/api/([a-z0-9-]+)/v\d+", source))
        self.assertEqual({"suicide-risk"}, target_ids)

        modules = {module["moduleId"]: module for module in load_manifest(MANIFEST)["modules"]}
        nginx = (ROOT / "deployment" / "nginx.conf").read_text(encoding="utf-8")
        dockerfile = (ROOT / "deployment" / "Dockerfile").read_text(encoding="utf-8")
        compose = (ROOT / "deployment" / "compose.unified.yaml").read_text(encoding="utf-8")
        for module_id in target_ids:
            module = modules[module_id]
            self.assertIn(f"location {module['basePath']}", nginx)
            self.assertIn(f"location /modules/{module_id}/", nginx)
            self.assertRegex(dockerfile, rf"COPY Modules/\S+ /opt/modules/{module_id}\b")
            self.assertIn(f"{module['volume']['name']}:{module['volume']['mountPath']}", compose)
            self.assertIn(module_id, MODULE_SMOKE)

    def test_medical_history_receives_ddi_service_url(self):
        modules = {module["moduleId"]: module for module in load_manifest(MANIFEST)["modules"]}
        self.assertEqual(
            f"http://127.0.0.1:{modules['ddi-checker']['internalPort']}",
            modules["medical-history"]["environment"].get("DDI_CHECKER_SERVICE_URL"),
        )

    def test_nginx_canonicalizes_suicide_risk_route_and_preserves_query(self):
        nginx = (ROOT / "deployment" / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn(
            "location = /modules/suicide-risk {\n"
            "            return 308 /modules/suicide-risk/$is_args$args;\n"
            "        }",
            nginx,
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
