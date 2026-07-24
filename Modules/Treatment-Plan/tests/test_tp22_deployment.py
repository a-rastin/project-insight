import os
import json
import re
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.verify_deployment import (
    SECURITY_HEADERS,
    hardened_run_command,
    verify_backup_restore_integrity,
    verify_partial_migration_failure,
    verify_graceful_database_integrity,
    scan_evidence_path,
)
from scripts.package_release import immutable_image_reference, scan_evidence_for_image, write_scan_evidence
from treatment_plan.config import ConfigurationError, Settings
from treatment_plan.deployment import main, migration_gate, settings_from_environment


ROOT = Path(__file__).parents[1]


class TP22DeploymentTests(unittest.TestCase):
    def test_migration_gate_applies_complete_ordered_schema_and_rejects_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "runtime.db"
            settings = Settings(environment="test", database_path=database)
            self.assertTrue(migration_gate(settings))
            self.assertEqual((), migration_gate(settings))
            with closing(sqlite3.connect(database)) as connection:
                connection.execute("INSERT INTO schema_migrations(version) VALUES ('9999_unexpected.sql')")
                connection.commit()
            with self.assertRaises(RuntimeError):
                migration_gate(settings)

    def test_secret_file_mount_is_supported_without_allowing_ambiguous_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            secret = Path(directory) / "auth-url"
            secret.write_text("https://authentication.internal/session", encoding="utf-8")
            environment = {
                "TP_ENV": "production",
                "TP_AUTHENTICATION_SESSION_URL_FILE": str(secret),
                "TP_TRUSTED_INTERNAL_ORIGINS": "https://authentication.internal",
            }
            with patch.dict(os.environ, environment, clear=True):
                self.assertEqual("https://authentication.internal/session", settings_from_environment().authentication_session_url)
            environment["TP_AUTHENTICATION_SESSION_URL"] = "https://authentication.internal/other"
            with patch.dict(os.environ, environment, clear=True), self.assertRaises(ConfigurationError):
                settings_from_environment()

    def test_release_packaging_is_non_root_pinned_loopback_and_resource_bounded(self):
        dockerfile = (ROOT / "Dockerfile.release").read_text(encoding="utf-8")
        requirements = (ROOT / "requirements.lock").read_text(encoding="utf-8")
        compose = (ROOT / "compose.release.yaml").read_text(encoding="utf-8")
        self.assertIn("USER 10001:10001", dockerfile)
        self.assertIn("npm ci", dockerfile)
        self.assertNotIn(">=", requirements)
        self.assertTrue(any("==" in line for line in requirements.splitlines() if line.strip() and not line.startswith("#")))
        for required in ("127.0.0.1:", "read_only: true", "cap_drop: [ALL]", "mem_limit: 512m", "pids_limit: 256", "sbom: true", '"/tmp:size=32m,mode=1777"'):
            self.assertIn(required, compose)

    def test_release_inputs_are_digest_pinned_and_lock_files_are_reproducible(self):
        dockerfile = (ROOT / "Dockerfile.release").read_text(encoding="utf-8")
        compose = (ROOT / "compose.release.yaml").read_text(encoding="utf-8")
        requirements = (ROOT / "requirements.lock").read_text(encoding="utf-8")
        package = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
        package_lock = json.loads((ROOT / "frontend" / "package-lock.json").read_text(encoding="utf-8"))
        self.assertIsNotNone(re.search(r"^FROM node:[^@\n]+@sha256:[0-9a-f]{64} AS frontend$", dockerfile, re.MULTILINE))
        self.assertIsNotNone(re.search(r"^FROM python:[^@\n]+@sha256:[0-9a-f]{64} AS runtime$", dockerfile, re.MULTILINE))
        self.assertIn("image: ${TP_IMAGE:?set TP_IMAGE to an immutable digest}", compose)
        self.assertNotIn("latest", json.dumps(package))
        for section in ("dependencies", "devDependencies"):
            for name, version in package[section].items():
                self.assertEqual(version, package_lock["packages"][f"node_modules/{name}"]["version"])
        requirement_lines = [line for line in requirements.splitlines() if line.strip() and not line.strip().startswith("#")]
        self.assertGreater(len(requirement_lines), 5)
        self.assertTrue(all("==" in line or "--hash=" in line for line in requirement_lines))
        self.assertTrue(any("--hash=" in line for line in requirement_lines))

    def test_release_tools_require_immutable_image_references(self):
        digest = "sha256:" + "a" * 64
        self.assertEqual("registry.example/treatment-plan@" + digest, immutable_image_reference("registry.example/treatment-plan@" + digest))
        with self.assertRaises(ValueError):
            immutable_image_reference("registry.example/treatment-plan:0.1.0")
        with self.assertRaises(ValueError):
            immutable_image_reference("registry.example/treatment-plan@sha256:digest")

    def test_vps_assets_keep_systemd_on_container_only_and_nginx_on_tls_routes(self):
        unit = (ROOT / "deployment" / "treatment-plan-container.service").read_text(encoding="utf-8")
        nginx = (ROOT / "deployment" / "nginx-vps.conf").read_text(encoding="utf-8").lower()
        self.assertIn("/usr/bin/docker run", unit)
        self.assertNotIn("uvicorn", unit)
        self.assertIn("127.0.0.1:8000:8000", unit)
        for header in SECURITY_HEADERS:
            self.assertIn(header, nginx)
        self.assertIn("proxy_pass http://127.0.0.1:8000", nginx)
        self.assertIn("ssl_protocols", nginx)
        self.assertIn("tlsv1.2", nginx)
        self.assertIn("tlsv1.3", nginx)

    def test_independent_container_verifier_injects_runtime_hardening(self):
        command = hardened_run_command("image@sha256:" + "a" * 64, "name", "volume", 8123)
        joined = " ".join(command)
        for required in ("--user 10001:10001", "--read-only", "--cap-drop ALL", "no-new-privileges", "--memory 512m", "--pids-limit 256", "127.0.0.1:8123:8000"):
            self.assertIn(required, joined)

    def test_backup_restore_integrity_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            verify_backup_restore_integrity(Path(directory))

    def test_partial_migration_failure_is_rejected_by_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            verify_partial_migration_failure(Path(directory))

    def test_graceful_shutdown_path_keeps_database_uncorrupted(self):
        with tempfile.TemporaryDirectory() as directory:
            verify_graceful_database_integrity(Path(directory))

    def test_scan_evidence_is_keyed_by_image_digest(self):
        digest = "sha256:" + "c" * 64
        image = "registry.example/treatment-plan@" + digest
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = scan_evidence_path(root, image)
            self.assertIn(digest.replace(":", "-"), str(path))
            written = write_scan_evidence(root, image, scanner="trivy", report={"Results": []})
            self.assertTrue(written.is_file())
            evidence = scan_evidence_for_image(root, image)
            self.assertEqual("trivy", evidence["scanner"])
            self.assertEqual(image, evidence["image"])
            self.assertEqual(digest, evidence["digest"])

    def test_deployment_main_command_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "runtime.db"
            environment = {
                "TP_ENV": "test",
                "TP_DATABASE_PATH": str(database),
            }
            with patch.dict(os.environ, environment, clear=True), patch("sys.argv", ["deployment.py", "migration-gate"]):
                self.assertEqual(0, main())
            with patch.dict(os.environ, environment, clear=True), patch("sys.argv", ["deployment.py", "serve"]), patch("treatment_plan.deployment.serve") as mock_serve:
                self.assertEqual(0, main())
                mock_serve.assert_called_once()


if __name__ == "__main__":
    unittest.main()
