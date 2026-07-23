import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
DEPLOYMENT = ROOT / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

from supervisor import build_process_specs  # noqa: E402


class UnifiedImageTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((DEPLOYMENT / "manifest.json").read_text(encoding="utf-8"))

    def test_manifest_is_authoritative_for_unified_runtime(self):
        self.assertEqual(
            {
                module["moduleId"]: module["internalPort"]
                for module in self.manifest["modules"]
            },
            {
                "authentication": 8101,
                "dashboard": 8102,
                "add-new-patient": 8103,
                "diagnosis": 8104,
                "severity": 8105,
                "medical-history": 8106,
                "ddi-checker": 8107,
                "bn-manager": 8108,
                "treatment-plan": 8109,
            },
        )
        self.assertEqual(self.manifest["gateway"], {"port": 8080, "exposed": True})
        self.assertEqual(self.manifest["image"]["dockerfile"], "deployment/Dockerfile")
        self.assertEqual(self.manifest["supervisor"]["pid1"], "tini")

    def test_manifest_gives_each_module_private_writable_database(self):
        modules = self.manifest["modules"]
        data_paths = {module["volume"]["mountPath"] for module in modules}
        database_paths = {module["databasePath"] for module in modules}
        self.assertEqual(len(data_paths), len(modules))
        self.assertEqual(len(database_paths), len(modules))
        for module in modules:
            self.assertTrue(module["volume"]["writable"])
            self.assertTrue(module["databasePath"].startswith(module["volume"]["mountPath"] + "/"))

    def test_supervisor_declares_all_module_processes_and_gateway(self):
        specs = build_process_specs(self.manifest)
        self.assertEqual(
            set(specs),
            {
                "authentication",
                "dashboard",
                "add-new-patient",
                "diagnosis",
                "severity",
                "medical-history",
                "ddi-checker",
                "bn-manager",
                "treatment-plan",
                "nginx",
            },
        )
        for module in self.manifest["modules"]:
            spec = specs[module["moduleId"]]
            self.assertEqual(spec.cwd, module["workingDirectory"])
            self.assertEqual(spec.env["PORT"], str(module["internalPort"]))
            self.assertEqual(spec.env["DATABASE_PATH"], module["databasePath"])
        self.assertEqual(specs["nginx"].command[:3], ("nginx", "-g", "daemon off;"))

    def test_image_exposes_only_gateway_and_excludes_runtime_inputs(self):
        dockerfile = (DEPLOYMENT / "Dockerfile").read_text(encoding="utf-8")
        dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        compose = (DEPLOYMENT / "compose.unified.yaml").read_text(encoding="utf-8")
        self.assertIn("EXPOSE 8080", dockerfile)
        self.assertIn("tini -- python /opt/deployment/supervisor.py", dockerfile)
        self.assertNotIn("EXPOSE 810", dockerfile)
        for ignored in ("graphify-out", "tests", "node_modules", "*.sqlite*", "fixtures"):
            self.assertIn(ignored, dockerignore)
        self.assertIn('"8080:8080"', compose)
        for port in range(8101, 8110):
            self.assertNotIn(f'"{port}:', compose)

    def test_nginx_routes_unique_base_paths_on_gateway_only(self):
        nginx = (DEPLOYMENT / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("listen 8080", nginx)
        self.assertNotIn("listen 80;", nginx)
        self.assertNotIn("listen 443;", nginx)
        for module in self.manifest["modules"]:
            self.assertIn(f"location {module['basePath']}", nginx)
            self.assertIn(f"location {module['proxyPrefix']}", nginx)

    def test_ddi_adapter_reads_database_from_deployment_data_directory(self):
        source = (ROOT / "Modules/DDI-Checker-1.2.0/src/server.mjs").read_text(encoding="utf-8")
        self.assertIn("DDI_DATA_DIR", source)
        self.assertIn("DDI_BUNDLED_KB_PATH", source)

    def test_treatment_plan_adapter_honors_manifest_port(self):
        source = (ROOT / "Modules/Treatment-Plan/treatment_plan/deployment.py").read_text(encoding="utf-8")
        self.assertIn("TP_PORT", source)


if __name__ == "__main__":
    unittest.main()
