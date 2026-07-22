import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_architecture import (  # noqa: E402
    FilesystemSourceAdapter,
    InMemorySourceAdapter,
    check_architecture,
)


def fixture_sources(*, extra=None, include_config=True):
    sources = {
        "Modules/alpha/module-config.json": (
            '{"moduleId":"alpha","dataDirectory":"data/alpha",'
            '"databasePath":"data/alpha.sqlite3"}'
        ),
        "Modules/beta/module-config.json": (
            '{"moduleId":"beta","dataDirectory":"data/beta",'
            '"databasePath":"data/beta.sqlite3"}'
        ),
    }
    if not include_config:
        sources = {}
    if extra:
        sources.update(extra)
    return sources


class ArchitectureCheckerTests(unittest.TestCase):
    def test_python_cross_module_import_is_rejected(self):
        violations = check_architecture(
            InMemorySourceAdapter(
                fixture_sources(
                    extra={
                        "Modules/alpha/service.py": "from Modules.beta.store import read\n",
                    }
                )
            )
        )
        self.assertTrue(any(item.code == "CROSS_MODULE_IMPORT" for item in violations))

    def test_node_cross_module_import_is_rejected(self):
        violations = check_architecture(
            InMemorySourceAdapter(
                fixture_sources(
                    extra={
                        "Modules/alpha/app.mjs": 'import { read } from "../beta/store.mjs";\n',
                    }
                )
            )
        )
        self.assertTrue(any(item.code == "CROSS_MODULE_IMPORT" for item in violations))

    def test_generated_client_import_remains_allowed(self):
        violations = check_architecture(
            InMemorySourceAdapter(
                fixture_sources(
                    extra={
                        "Modules/alpha/client.py": "from contracts.clients.python import Client\n",
                        "Modules/beta/client.mjs": 'import { Client } from "contracts/clients/node.mjs";\n',
                    }
                )
            )
        )
        self.assertFalse(any(item.code == "CROSS_MODULE_IMPORT" for item in violations))

    def test_reused_sqlite_path_is_rejected(self):
        violations = check_architecture(
            InMemorySourceAdapter(
                fixture_sources(
                    extra={
                        "Modules/alpha/config.py": 'DB_PATH = "../../shared.sqlite3"\n',
                        "Modules/beta/config.py": 'DB_PATH = "../../shared.sqlite3"\n',
                    }
                )
            )
        )
        self.assertTrue(any(item.code == "CROSS_MODULE_DATABASE_PATH" for item in violations))

    def test_same_working_directory_sqlite_path_is_rejected(self):
        violations = check_architecture(
            InMemorySourceAdapter(
                fixture_sources(
                    extra={
                        "Modules/alpha/config.py": 'DB_PATH = "shared.sqlite3"\n',
                        "Modules/beta/config.py": 'DB_PATH = "shared.sqlite3"\n',
                    }
                )
            )
        )
        self.assertTrue(any(item.code == "CROSS_MODULE_DATABASE_PATH" for item in violations))

    def test_shared_runtime_json_is_rejected(self):
        violations = check_architecture(
            InMemorySourceAdapter(
                fixture_sources(
                    extra={
                        "Modules/alpha/runtime.py": 'STATE = "../../shared-runtime.json"\n',
                        "Modules/beta/runtime.py": 'STATE = "../../shared-runtime.json"\n',
                    }
                )
            )
        )
        self.assertTrue(any(item.code == "SHARED_RUNTIME_JSON" for item in violations))

    def test_clinical_browser_storage_is_rejected(self):
        violations = check_architecture(
            InMemorySourceAdapter(
                fixture_sources(
                    extra={
                        "Modules/alpha/patient-ui.mjs": (
                            'const patient = localStorage.getItem("patient-record");\n'
                        ),
                    }
                )
            )
        )
        self.assertTrue(any(item.code == "CLINICAL_BROWSER_STORAGE" for item in violations))

    def test_each_module_requires_separate_data_configuration(self):
        violations = check_architecture(
            InMemorySourceAdapter(
                {
                    "Modules/alpha/module-config.json": (
                        '{"moduleId":"alpha","dataDirectory":"data/alpha",'
                        '"databasePath":"data/alpha.sqlite3"}'
                    ),
                    "Modules/beta/app.py": "print('beta')\n",
                }
            )
        )
        self.assertTrue(any(item.code == "MODULE_DATA_CONFIG_MISSING" for item in violations))

    def test_filesystem_adapter_uses_same_public_checker_interface(self):
        violations = check_architecture(FilesystemSourceAdapter(ROOT))
        self.assertFalse(any(item.code == "MODULE_DATA_CONFIG_MISSING" for item in violations))


if __name__ == "__main__":
    unittest.main()