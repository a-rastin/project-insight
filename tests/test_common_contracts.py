import copy
import json
import sys
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).parents[1]
CONTRACTS = ROOT / "contracts"
sys.path.insert(0, str(ROOT / "scripts"))

from check_common_contracts import (  # noqa: E402
    CompatibilityError,
    check_examples,
    check_no_domain_implementation,
    check_openapi_references,
    check_schema_compatibility,
    load_json,
    validate_instance,
)


class CommonContractTests(unittest.TestCase):
    def test_root_schema_catalog_is_versioned(self):
        version_dir = CONTRACTS / "schemas" / "1.0.0"
        expected = {
            "audit-event.schema.json",
            "auth-session.schema.json",
            "identifiers.schema.json",
            "module-contract.schema.json",
            "pagination.schema.json",
            "problem-details.schema.json",
            "provenance.schema.json",
            "request-metadata.schema.json",
            "resource-version.schema.json",
            "response-envelope.schema.json",
        }
        self.assertEqual({path.name for path in version_dir.glob("*.json")}, expected)

    def test_all_examples_validate(self):
        check_examples(CONTRACTS)

    def test_openapi_references_resolve_without_network(self):
        check_openapi_references(CONTRACTS)

    def test_intentional_breaking_schema_change_fails_compatibility(self):
        schema = load_json(CONTRACTS / "schemas" / "1.0.0" / "module-contract.schema.json")
        example = load_json(CONTRACTS / "examples" / "1.0.0" / "success.json")
        broken = copy.deepcopy(schema)
        broken["required"] = ["moduleId", "newRequiredField"]
        with self.assertRaises(CompatibilityError):
            check_schema_compatibility(schema, broken, [example], "module-contract")

    def test_shared_package_static_rule_rejects_domain_code(self):
        check_no_domain_implementation(CONTRACTS)

    def test_python_production_and_memory_adapters_share_registry_interface(self):
        from contracts.adapters.python.filesystem import FilesystemContractAdapter
        from contracts.adapters.python.memory import InMemoryContractAdapter

        filesystem = FilesystemContractAdapter(CONTRACTS)
        memory = InMemoryContractAdapter.from_directory(CONTRACTS)
        self.assertEqual(
            filesystem.get_schema("1.0.0", "problem-details"),
            memory.get_schema("1.0.0", "problem-details"),
        )
        self.assertEqual(filesystem.get_openapi(), memory.get_openapi())

    def test_fastapi_routes_use_contract_interface(self):
        from contracts.adapters.python.fastapi import install_common_routes
        from contracts.adapters.python.memory import InMemoryContractAdapter

        contract = load_json(CONTRACTS / "examples" / "1.0.0" / "success.json")["data"]
        app = FastAPI()
        install_common_routes(
            app,
            InMemoryContractAdapter.from_directory(CONTRACTS),
            contract=contract,
            readiness=lambda: {
                "migrations": "ok",
                "configuration": "ok",
                "contractCompatibility": "ok",
                "dependencies": "ok",
            },
        )
        client = TestClient(app)
        self.assertEqual(client.get("/health").status_code, 200)
        ready = client.get("/ready")
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(ready.json()["status"], "ready")
        self.assertNotIn("url", ready.text.lower())
        self.assertEqual(client.get("/contract").json()["moduleId"], contract["moduleId"])
        self.assertEqual(client.get("/openapi.json").status_code, 200)
        self.assertEqual(
            client.get("/schemas/1.0.0/problem-details").json()["$id"],
            "https://insight.example/contracts/common/1.0.0/problem-details.schema.json",
        )

    def test_response_envelope_contains_request_and_correlation_ids(self):
        schema = load_json(CONTRACTS / "schemas" / "1.0.0" / "response-envelope.schema.json")
        example = load_json(CONTRACTS / "examples" / "1.0.0" / "success.json")
        validate_instance(example, schema, CONTRACTS / "schemas" / "1.0.0" / "response-envelope.schema.json")


if __name__ == "__main__":
    unittest.main()
