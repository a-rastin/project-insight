import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_unified_deployment import (  # noqa: E402
    MODULE_SMOKE,
    _probe_ok,
    hardened_unified_run_command,
    immutable_image_reference,
    image_digest,
    load_manifest,
    scan_evidence_path,
    smoke_matrix,
    verify_paths,
    verify_all_modules_smoke_matrix,
    verify_unified_gateway,
    verify_topology_contracts,
    write_scan_evidence,
)


class TP22UnifiedVerificationTests(unittest.TestCase):
    def test_smoke_matrix_covers_every_manifest_module(self):
        manifest = load_manifest()
        rows = verify_all_modules_smoke_matrix()
        self.assertEqual(len(rows), len(manifest["modules"]))
        self.assertEqual({row["moduleId"] for row in rows}, {module["moduleId"] for module in manifest["modules"]})
        for row in rows:
            self.assertTrue(row["standalone_health"])
            self.assertTrue(row["unified_health"])
            self.assertTrue(row["basePath"].startswith("/"))
            self.assertTrue(row["proxyPrefix"].startswith("/modules/"))

    def test_module_smoke_routes_match_real_module_surfaces(self):
        # Spot-check against known process-root routes (do not invent thresholds).
        self.assertIn("/healthz", MODULE_SMOKE["authentication"]["standalone_health"])
        self.assertIn("/api/auth/health", MODULE_SMOKE["authentication"]["standalone_health"])
        self.assertIn("/readyz", MODULE_SMOKE["dashboard"]["standalone_ready"])
        self.assertIn("/api/health", MODULE_SMOKE["add-new-patient"]["standalone_health"])
        self.assertIn("/api/internal/medical-history/health", MODULE_SMOKE["medical-history"]["standalone_health"])
        self.assertIn("/api/health", MODULE_SMOKE["bn-manager"]["standalone_health"])
        self.assertIn("/health", MODULE_SMOKE["treatment-plan"]["standalone_health"])
        self.assertIn("/health", MODULE_SMOKE["severity"]["standalone_health"])
        self.assertIn("/health", MODULE_SMOKE["ddi-checker"]["standalone_health"])
        self.assertIn("/health", MODULE_SMOKE["diagnosis"]["standalone_health"])

    def test_diagnosis_unified_probes_are_canonical_and_module_specific(self):
        probes = MODULE_SMOKE["diagnosis"]
        self.assertEqual(("/api/diagnosis/v1/health",), probes["unified_health"])
        self.assertEqual(("/api/diagnosis/v1/ready",), probes["unified_ready"])
        self.assertFalse(_probe_ok(200, b'{"ok": true, "service": "auth"}', expected_module="diagnosis"))
        self.assertTrue(_probe_ok(200, b'{"ok": true, "module": "diagnosis"}', expected_module="diagnosis"))

    def test_verifier_reports_diagnosis_503_body(self):
        body = b'{"ok":false,"module":"diagnosis","checks":{"clinicalScope":{"ok":false,"coding":{"resolutionStatus":"unresolved"}}}}'
        with patch("verify_unified_deployment.request", return_value=(503, {}, body)):
            with self.assertRaises(RuntimeError) as context:
                verify_paths(
                    "http://gateway.test",
                    ["/api/diagnosis/v1/ready"],
                    label="unified diagnosis ready",
                    expected_module="diagnosis",
                )
        message = str(context.exception)
        self.assertIn("checks.clinicalScope.ok=false", message)
        self.assertIn("resolutionStatus=unresolved", message)

    def test_unified_verifier_uses_gateway_aggregate_not_health_aliases(self):
        calls = []
        with patch("verify_unified_deployment.verify_paths", side_effect=lambda _base, paths, **_kwargs: calls.append(paths)):
            with patch("verify_unified_deployment.request", return_value=(200, {}, b"{}")):
                verify_unified_gateway("http://gateway.test")
        self.assertIn(["/readyz"], calls)
        self.assertIn(["/api/diagnosis/v1/ready"], calls)
        self.assertNotIn(["/health"], calls)

    def test_topology_contracts_tls_loopback_restart_and_volumes(self):
        result = verify_topology_contracts(ROOT)
        self.assertTrue(result["tls"])
        self.assertTrue(result["loopback"])
        self.assertTrue(result["restart"])
        self.assertTrue(result["volumes"])
        self.assertTrue(result["digest"])

    def test_unified_run_command_is_hardened_and_loopback_only(self):
        digest = "sha256:" + "b" * 64
        image = "registry.example/insight-unified@" + digest
        command = hardened_unified_run_command(image, "name", 18080)
        joined = " ".join(command)
        for required in (
            "--read-only",
            "--cap-drop ALL",
            "no-new-privileges",
            "--memory 2048m",
            "--pids-limit 1024",
            "127.0.0.1:18080:8080",
        ):
            self.assertIn(required, joined)
        with self.assertRaises(ValueError):
            hardened_unified_run_command("registry.example/insight-unified:latest", "name", 18080)

    def test_scan_evidence_keyed_by_digest(self):
        digest = "sha256:" + "d" * 64
        image = "registry.example/insight-unified@" + digest
        self.assertEqual(digest, image_digest(image))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = scan_evidence_path(root, image)
            self.assertIn(digest.replace(":", "-"), str(path))
            written = write_scan_evidence(root, image, scanner="trivy", report={"Results": []})
            self.assertTrue(written.is_file())
            payload = json.loads(written.read_text(encoding="utf-8"))
            self.assertEqual("trivy", payload["scanner"])
            self.assertEqual(digest, payload["digest"])

    def test_immutable_image_reference_rejects_tags(self):
        digest = "sha256:" + "e" * 64
        good = "insight-unified@" + digest
        self.assertEqual(good, immutable_image_reference(good))
        with self.assertRaises(ValueError):
            immutable_image_reference("insight-unified:0.1.0")

    def test_smoke_matrix_rejects_unknown_module(self):
        manifest = load_manifest()
        broken = json.loads(json.dumps(manifest))
        broken["modules"].append(
            {
                **broken["modules"][0],
                "moduleId": "not-a-real-module",
                "internalPort": 8999,
                "basePath": "/api/not-a-real-module",
                "proxyPrefix": "/modules/not-a-real-module",
                "volume": {**broken["modules"][0]["volume"], "name": "not-a-real-module-data", "mountPath": "/var/lib/insight/not-a-real-module"},
                "databasePath": "/var/lib/insight/not-a-real-module/db.sqlite3",
            }
        )
        with self.assertRaises(RuntimeError):
            smoke_matrix(broken)

    def test_container_verification_requires_docker(self):
        from verify_unified_deployment import verify_container

        digest = "sha256:" + "f" * 64
        image = "registry.example/insight-unified@" + digest
        with patch("verify_unified_deployment.shutil.which", return_value=None):
            with self.assertRaises(RuntimeError) as context:
                verify_container(image, recovery=False)
        self.assertIn("docker is not available", str(context.exception))


if __name__ == "__main__":
    unittest.main()
