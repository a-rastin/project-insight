import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from treatment_plan.app import create_app
from treatment_plan.config import ConfigurationError, Settings
from treatment_plan.repository import InMemoryRepository, RuntimeRecord
from treatment_plan.sqlite_repository import SQLiteRepository


class ScaffoldTests(unittest.TestCase):
    def test_health_and_readiness_use_in_memory_adapter(self):
        repository = InMemoryRepository()
        with TestClient(create_app(Settings(environment="test"), repository)) as client:
            self.assertEqual({"status": "ok"}, client.get("/health").json())
            self.assertEqual(200, client.get("/ready").status_code)

    def test_repository_adapters_share_interface_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            adapters = [InMemoryRepository(), SQLiteRepository(Path(directory) / "db.sqlite")]
            for adapter in adapters:
                adapter.migrate()
                adapter.put(RuntimeRecord("key", "value"))
                self.assertEqual(RuntimeRecord("key", "value"), adapter.get("key"))

    def test_auth_stub_defaults_off(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(Settings.from_env().auth_stub_enabled)

    def test_auth_stub_is_rejected_outside_development(self):
        with patch.dict(os.environ, {"TP_ENV": "production", "TP_AUTH_STUB_ENABLED": "true"}, clear=True):
            with self.assertRaisesRegex(ConfigurationError, "only in development"):
                Settings.from_env()

    def test_disabled_auth_stub_fails_closed(self):
        with TestClient(create_app(Settings(environment="test"), InMemoryRepository())) as client:
            self.assertEqual(503, client.get("/api/treatment-plan/v1/session").status_code)

    def test_development_auth_stub_is_explicit(self):
        settings = Settings(environment="development", auth_stub_enabled=True)
        with TestClient(create_app(settings, InMemoryRepository())) as client:
            self.assertEqual("doctor-test", client.get("/api/treatment-plan/v1/session", headers={"X-Development-Actor": "doctor-test"}).json()["actor"])


if __name__ == "__main__":
    unittest.main()
