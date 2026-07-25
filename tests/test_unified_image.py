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

    def test_diagnosis_manifest_uses_unified_authentication_endpoint(self):
        diagnosis = next(module for module in self.manifest["modules"] if module["moduleId"] == "diagnosis")
        self.assertEqual("http://127.0.0.1:8101", diagnosis["environment"]["AUTH_BASE_URL"])

    def test_dashboard_manifest_uses_unified_authentication_endpoint(self):
        dashboard = next(module for module in self.manifest["modules"] if module["moduleId"] == "dashboard")
        self.assertEqual(
            "http://127.0.0.1:8101/api/auth/session",
            dashboard["environment"]["AUTH_SESSION_URL"],
        )
        self.assertEqual("0", dashboard["environment"]["DASHBOARD_MOCK_AUTH"])

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
                "gateway-readiness",
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
        self.assertIn('"127.0.0.1:8080:8080"', compose)
        for port in range(8101, 8110):
            self.assertNotIn(f'"{port}:', compose)
        self.assertIn("/run/secrets:ro", compose)
        self.assertIn("INSIGHT_UNIFIED_IMAGE", compose)
        self.assertIn("http://127.0.0.1:8080/readyz", dockerfile)

    def test_nginx_routes_unique_base_paths_on_gateway_only(self):
        nginx = (DEPLOYMENT / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("listen 8080", nginx)
        self.assertNotIn("listen 80;", nginx)
        self.assertNotIn("listen 443;", nginx)
        for module in self.manifest["modules"]:
            self.assertIn(f"location {module['basePath']}", nginx)
            self.assertIn(f"location {module['proxyPrefix']}", nginx)
        self.assertIn("location = /readyz { proxy_pass http://127.0.0.1:8110; }", nginx)
        self.assertIn("location = /healthz { proxy_pass http://127.0.0.1:8110; }", nginx)

    def test_nginx_proxies_user_management_to_authentication(self):
        nginx = (DEPLOYMENT / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn(
            "location /modules/user-management {\n            proxy_pass http://127.0.0.1:8101;\n        }",
            nginx,
        )

    def test_nginx_serves_authentication_root_and_dashboard_static_shell(self):
        nginx = (DEPLOYMENT / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("include /etc/nginx/mime.types;", nginx)
        self.assertIn("default_type application/octet-stream;", nginx)
        # Authentication is the application landing page at "/".
        self.assertIn("location / {", nginx)
        self.assertIn("proxy_pass http://127.0.0.1:8101;", nginx)
        self.assertIn("proxy_set_header Host $host;", nginx)
        self.assertIn("proxy_set_header X-Forwarded-Proto $scheme;", nginx)
        self.assertIn("proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;", nginx)
        # Role links normalize to one shell, avoiding extensionless HTML aliases.
        self.assertIn("location = /dashboard {", nginx)
        self.assertIn("return 302 /dashboard/;", nginx)
        self.assertIn("absolute_redirect off;", nginx)
        self.assertIn("location = /dashboard/ {", nginx)
        self.assertIn("location = /dashboard/admin {", nginx)
        self.assertIn("location = /dashboard/user {", nginx)
        self.assertIn("location /dashboard/ {", nginx)
        self.assertIn("alias /opt/modules/dashboard/;", nginx)
        self.assertEqual(nginx.count("default_type text/html;"), 1)
        self.assertIn('add_header Cache-Control "no-store";', nginx)
        self.assertIn('add_header X-Content-Type-Options "nosniff";', nginx)
        for role in ("admin", "user"):
            route = f"location = /dashboard/{role} {{\n            return 302 /dashboard/;\n        }}"
            self.assertIn(route, nginx)

    def test_dashboard_shell_uses_gateway_absolute_assets(self):
        shell = (ROOT / "Modules" / "Dashboard-1.2.0" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/dashboard/styles.css"', shell)
        self.assertIn('src="/dashboard/dashboard.js"', shell)

    def test_vps_topology_keeps_host_nginx_on_tls_and_systemd_on_digest_only(self):
        unit = (DEPLOYMENT / "insight-unified-container.service").read_text(encoding="utf-8")
        nginx = (DEPLOYMENT / "nginx-vps.conf").read_text(encoding="utf-8")
        nginx_lower = nginx.lower()
        self.assertIn("/usr/bin/docker run", unit)
        self.assertIn("${INSIGHT_UNIFIED_IMAGE}", unit)
        self.assertIn("127.0.0.1:8080:8080", unit)
        self.assertIn("/run/secrets:ro", unit)
        self.assertNotIn("uvicorn", unit)
        self.assertNotIn("supervisor.py", unit)
        for module_port in range(8101, 8110):
            self.assertNotIn(f":{module_port}", unit)
            self.assertNotIn(f"127.0.0.1:{module_port}", nginx)
        self.assertIn("listen 443 ssl", nginx_lower)
        self.assertIn("strict-transport-security", nginx_lower)
        self.assertIn("content-security-policy", nginx_lower)
        self.assertIn("x-content-type-options", nginx_lower)
        self.assertIn("x-frame-options", nginx_lower)
        self.assertIn("referrer-policy", nginx_lower)
        self.assertIn("proxy_pass http://127.0.0.1:8080", nginx_lower)
        self.assertIn("proxy_set_header x-forwarded-proto", nginx_lower)
        self.assertIn("proxy_set_header x-forwarded-for", nginx_lower)
        self.assertIn("proxy_set_header host", nginx_lower)
        self.assertNotIn("proxy_pass http://127.0.0.1:810", nginx_lower)

    def test_supervisor_remains_sole_manager_of_internal_module_processes(self):
        dockerfile = (DEPLOYMENT / "Dockerfile").read_text(encoding="utf-8")
        unit = (DEPLOYMENT / "insight-unified-container.service").read_text(encoding="utf-8")
        self.assertIn("tini -- python /opt/deployment/supervisor.py", dockerfile)
        specs = build_process_specs(self.manifest)
        self.assertIn("nginx", specs)
        self.assertNotIn("python -m", unit)
        self.assertNotIn("node server", unit)
        self.assertNotIn("deno run", unit)
        for module in self.manifest["modules"]:
            self.assertIn(module["moduleId"], specs)
            command = " ".join(module["command"])
            self.assertNotIn(command, unit)

    def test_ddi_adapter_reads_database_from_deployment_data_directory(self):
        source = (ROOT / "Modules/DDI-Checker-1.2.0/src/server.mjs").read_text(encoding="utf-8")
        self.assertIn("DDI_DATA_DIR", source)
        self.assertIn("DDI_BUNDLED_KB_PATH", source)

    def test_treatment_plan_adapter_honors_manifest_port(self):
        source = (ROOT / "Modules/Treatment-Plan/treatment_plan/deployment.py").read_text(encoding="utf-8")
        self.assertIn("TP_PORT", source)


if __name__ == "__main__":
    unittest.main()
