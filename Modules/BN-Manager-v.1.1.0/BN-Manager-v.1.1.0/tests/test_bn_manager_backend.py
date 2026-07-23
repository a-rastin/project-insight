from __future__ import annotations

import unittest

from fastapi import Request
from fastapi.testclient import TestClient

from bn_manager_backend.auth_adapter import SessionState
from bn_manager_backend.evaluation_store import InMemoryEvaluationStore
from bn_manager_backend.main import create_app
from bn_manager_backend.model_governance import (
    ClinicalStatus,
    InMemoryGovernanceStore,
    SignedApproval,
    sign_approval,
)
from bn_manager_backend.model_registry import (
    MODEL_REGISTRY,
    MODEL_REGISTRY_DIR,
    read_registry_model,
    resolve_owned_registry_file,
)
from clinical_graph_models import compile_xmlbif


GOVERNANCE_KEY = b"test-governance-key-0123456789abcdef"


class AdminSessionAdapter:
    def __init__(self) -> None:
        self.session = SessionState(
            active=True,
            subject="admin-1",
            roles=frozenset({"admin"}),
            csrf_token="csrf-validate",
        )

    def fetch_session(self, request: Request) -> SessionState:
        return self.session


class ModelManagerSessionAdapter:
    def __init__(self) -> None:
        self.session = SessionState(
            active=True,
            subject="model-mgr-1",
            roles=frozenset({"modelmanager"}),
            csrf_token="csrf-validate",
        )

    def fetch_session(self, request: Request) -> SessionState:
        return self.session


class BnManagerBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app(evaluation_store=InMemoryEvaluationStore()))
        self.admin_client = TestClient(
            create_app(
                session_adapter=AdminSessionAdapter(),
                evaluation_store=InMemoryEvaluationStore(),
                governance_store=InMemoryGovernanceStore(),
                governance_key=GOVERNANCE_KEY,
            )
        )
        self.model_manager_client = TestClient(
            create_app(
                session_adapter=ModelManagerSessionAdapter(),
                evaluation_store=InMemoryEvaluationStore(),
                governance_store=InMemoryGovernanceStore(),
                governance_key=GOVERNANCE_KEY,
            )
        )

    def test_health_ready_and_contract_endpoints(self) -> None:
        health = self.client.get("/api/health").json()
        ready = self.client.get("/api/ready").json()
        contract = self.client.get("/api/bn-manager/v1/contract").json()

        self.assertEqual(health["data"]["module_id"], "bn-manager")
        self.assertTrue(ready["data"]["contract_loaded"])
        self.assertEqual(contract["data"]["contract_version"], "2.0.0")
        self.assertEqual(contract["data"]["xml_target"]["extension"], ".xml")

    def test_models_list_contains_exactly_the_four_canonical_networks(self) -> None:
        response = self.client.get("/api/bn-manager/v1/models")

        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        self.assertEqual(
            {entry["stable_id"] for entry in payload["models"]},
            {
                "bnm.pharmacotherapy",
                "bnm.treatment-setting",
                "bnm.involuntary-treatment-considerations",
                "bnm.clozapine-suicide-risk",
            },
        )
        self.assertEqual(
            {entry["title"] for entry in payload["models"]},
            {
                "Pharmacotherapy",
                "Treatment Setting",
                "Involuntary Treatment Considerations",
                "Clozapine in Suicide Risk",
            },
        )
        self.assertEqual(payload["schema"], {
            "format": "XML",
            "version": "0.3",
            "path": "schemas/XSD.xml",
        })

    def test_schema_endpoint_returns_supplied_xsd(self) -> None:
        response = self.client.get("/api/bn-manager/v1/models/schema/xml-0.3")

        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        self.assertEqual(payload["format"], "XML")
        self.assertEqual(payload["mime_type"], "application/xml")
        self.assertIn('<xs:element name="BIF">', payload["text"])
        self.assertIn('minOccurs="2"', payload["text"])

    def test_every_model_detail_is_xsd_parseable_and_has_its_target(self) -> None:
        schema = self.client.get("/api/bn-manager/v1/models/schema/xml-0.3").json()["data"]["text"]
        for entry in MODEL_REGISTRY:
            with self.subTest(stable_id=entry.stable_id):
                response = self.client.get(f"/api/bn-manager/v1/models/{entry.stable_id}")
                self.assertEqual(response.status_code, 200)
                payload = response.json()["data"]
                self.assertEqual(payload["format"], "XML")
                self.assertTrue(payload["model"]["file_path"].endswith(".xml"))
                model = compile_xmlbif(payload["text"], schema_text=schema)
                self.assertIn(entry.target_node, model.node_map())

    def test_model_detail_exposes_evidence_schema_version_and_hash(self) -> None:
        for entry in MODEL_REGISTRY:
            with self.subTest(stable_id=entry.stable_id):
                response = self.client.get(f"/api/bn-manager/v1/models/{entry.stable_id}")
                self.assertEqual(response.status_code, 200)
                payload = response.json()["data"]
                evidence = payload["evidence_schema"]
                self.assertEqual(evidence["stable_id"], entry.stable_id)
                self.assertEqual(evidence["model_version"], entry.active_version)
                self.assertRegex(evidence["model_hash"], r"^sha256:[a-f0-9]{64}$")
                self.assertEqual(evidence["target"]["node_id"], entry.target_node)
                self.assertTrue(evidence["target"]["states"])
                self.assertIn("semantic_meaning", evidence["target"])

                allowed_ids = {node["node_id"] for node in evidence["allowed_evidence"]}
                self.assertNotIn(entry.target_node, allowed_ids)
                self.assertTrue(allowed_ids)
                for node in evidence["allowed_evidence"]:
                    self.assertTrue(node["states"])
                    self.assertIn(node["required"], (True, False))
                    self.assertIn("semantic_meaning", node)
                    self.assertIsInstance(node["semantic_meaning"], str)

                required = set(evidence["required_evidence"])
                optional = set(evidence["optional_evidence"])
                self.assertEqual(required | optional, allowed_ids)
                self.assertEqual(required & optional, set())
                for node in evidence["allowed_evidence"]:
                    if node["required"]:
                        self.assertIn(node["node_id"], required)
                    else:
                        self.assertIn(node["node_id"], optional)

                # Registry XML does not encode clinical required-flags yet.
                self.assertEqual(required, set())
                self.assertEqual(optional, allowed_ids)

    def test_per_model_evidence_schema_endpoint_matches_detail(self) -> None:
        for entry in MODEL_REGISTRY:
            with self.subTest(stable_id=entry.stable_id):
                detail = self.client.get(f"/api/bn-manager/v1/models/{entry.stable_id}").json()["data"]
                schema = self.client.get(
                    f"/api/bn-manager/v1/models/{entry.stable_id}/schema"
                )
                self.assertEqual(schema.status_code, 200)
                self.assertEqual(schema.json()["data"], detail["evidence_schema"])

    def test_unknown_model_schema_endpoint_returns_404(self) -> None:
        response = self.client.get("/api/bn-manager/v1/models/bnm.does-not-exist/schema")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "BNM_MODEL_NOT_FOUND")

    def test_unknown_and_traversal_like_model_ids_return_404(self) -> None:
        for stable_id in (
            "bnm.does-not-exist",
            "..%2Fxml%2FBN-Pharmacotherapy.xml",
            "bnm..pharmacotherapy",
        ):
            with self.subTest(stable_id=stable_id):
                response = self.client.get(f"/api/bn-manager/v1/models/{stable_id}")
                self.assertEqual(response.status_code, 404)

    def test_registry_resolver_rejects_external_paths(self) -> None:
        for path in (
            "../xml/BN-Pharmacotherapy.xml",
            "/etc/passwd",
            str((MODEL_REGISTRY_DIR.parent.parent / "README.md").resolve()),
        ):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    resolve_owned_registry_file(path)

    def test_dashboard_route_discovery_payload_shape(self) -> None:
        response = self.client.get("/internal/dashboard/module-routes/bn-manager")
        route = response.json()["routes"][0]

        self.assertEqual(route["id"], "bn-manager")
        self.assertTrue(route["embed"])
        self.assertTrue(route["requires_verified_session"])

    def test_validate_accepts_registry_model_id_and_compact_cpts(self) -> None:
        for entry in MODEL_REGISTRY:
            with self.subTest(stable_id=entry.stable_id):
                response = self.admin_client.post(
                    "/api/bn-manager/v1/models/validate",
                    json={"model": {"model_id": entry.stable_id}},
                    headers={"x-csrf-token": "csrf-validate"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["data"]["valid"])

    def test_validate_reports_requested_missing_target_node(self) -> None:
        response = self.admin_client.post(
            "/api/bn-manager/v1/models/validate",
            json={
                "model": {"model_id": "bnm.pharmacotherapy"},
                "target_node_ids": ["management_recommendation", "NotARealNode"],
            },
            headers={"x-csrf-token": "csrf-validate"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        self.assertFalse(payload["valid"])
        self.assertTrue(any(m["path"] == "target_nodes.NotARealNode" for m in payload["messages"]))

    def test_legacy_net_format_is_rejected_and_convert_route_is_removed(self) -> None:
        _, xml = read_registry_model("bnm.clozapine-suicide-risk")
        validate = self.admin_client.post(
            "/api/bn-manager/v1/models/validate",
            json={"model": {"format": "NET", "text": xml}},
            headers={"x-csrf-token": "csrf-validate"},
        )
        convert = self.admin_client.post(
            "/api/bn-manager/v1/models/convert",
            json={"model": {"format": "NET", "text": "net {}"}},
            headers={"x-csrf-token": "csrf-validate"},
        )

        self.assertEqual(validate.status_code, 415)
        self.assertEqual(validate.json()["error"]["code"], "BNM_UNSUPPORTED_FORMAT")
        self.assertEqual(convert.status_code, 405)

    def test_unknown_registry_model_id_returns_structured_404(self) -> None:
        response = self.admin_client.post(
            "/api/bn-manager/v1/models/validate",
            json={"model": {"model_id": "bnm.unknown"}},
            headers={"x-csrf-token": "csrf-validate"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "BNM_MODEL_NOT_FOUND")

    def test_evidence_schema_defaults_to_unvalidated_status_without_signature(self) -> None:
        for entry in MODEL_REGISTRY:
            with self.subTest(stable_id=entry.stable_id):
                response = self.client.get(f"/api/bn-manager/v1/models/{entry.stable_id}/schema")
                self.assertEqual(response.status_code, 200)
                evidence = response.json()["data"]
                self.assertEqual(evidence["clinical_status"], "unvalidated")
                self.assertNotIn("signed_approval", evidence)
                # Dimensional/schema validity must not imply clinical safety.
                self.assertFalse(evidence["clinical_safety_asserted"])
                self.assertIn(evidence["clinical_safety_wording"], [
                    "BN Manager output is clinical decision support, not a diagnosis, prescription, "
                    "or a treatment order. A licensed clinician must review patient context, source "
                    "evidence, contraindications, and local policy before clinical action.",
                ])

    def test_evidence_schema_surfaces_compact_neutral_cpt_bias_limitation(self) -> None:
        # Treatment Setting and Involuntary Treatment Considerations ship the compact one-row
        # TABLE the compiler broadcasts across parent combinations (table_broadcast=True).
        for stable_id in ("bnm.treatment-setting", "bnm.involuntary-treatment-considerations"):
            with self.subTest(stable_id=stable_id):
                evidence = self.client.get(
                    f"/api/bn-manager/v1/models/{stable_id}/schema"
                ).json()["data"]
                self.assertIn("compact-neutral-cpt-broadcast", evidence["limitations"])

    def test_governance_endpoint_reports_unvalidated_model(self) -> None:
        response = self.admin_client.get(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/governance",
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        self.assertEqual(payload["stable_id"], "bnm.pharmacotherapy")
        self.assertEqual(payload["clinical_status"], "unvalidated")
        self.assertEqual(payload["signed_approval"], None)

    def test_approve_requires_authenticated_model_manager_role_and_csrf(self) -> None:
        # Unauthenticated caller blocked.
        unauth = self.client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/approve",
            json={"approved_by": "psych-1"},
        )
        self.assertEqual(unauth.status_code, 401)

        # Authenticated but missing the governance write permission.
        clinician_session = SessionState(
            active=True,
            subject="clinician-1",
            roles=frozenset({"psychiatrist"}),
            csrf_token="csrf-validate",
        )
        class ClinicianAdapter:
            def fetch_session(self, request: Request) -> SessionState:
                return clinician_session
        clinician_client = TestClient(
            create_app(
                session_adapter=ClinicianAdapter(),
                evaluation_store=InMemoryEvaluationStore(),
                governance_store=InMemoryGovernanceStore(),
                governance_key=GOVERNANCE_KEY,
            )
        )
        forbidden = clinician_client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/approve",
            json={"approved_by": "psych-1"},
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(forbidden.status_code, 403)

        # Authenticated with permission but missing CSRF token.
        no_csrf = self.model_manager_client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/approve",
            json={"approved_by": "psych-1"},
        )
        self.assertEqual(no_csrf.status_code, 403)

    def test_approve_records_signed_signature_and_marks_model_approved(self) -> None:
        response = self.model_manager_client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/approve",
            json={"approved_by": "model-mgr-1"},
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        payload = response.json()["data"]
        self.assertEqual(payload["stable_id"], "bnm.pharmacotherapy")
        self.assertEqual(payload["clinical_status"], "approved")
        approval = payload["signed_approval"]
        self.assertEqual(approval["status"], "approved")
        self.assertEqual(approval["approved_by"], "model-mgr-1")
        self.assertRegex(approval["signature"], r"^[A-Za-z0-9_-]+$")
        self.assertRegex(approval["model_hash"], r"^sha256:[a-f0-9]{64}$")

        # Evidence schema now reports the approval.
        evidence = self.model_manager_client.get(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/schema",
            headers={"x-csrf-token": "csrf-validate"},
        ).json()["data"]
        self.assertEqual(evidence["clinical_status"], "approved")
        self.assertIsNotNone(evidence["signed_approval"])
        self.assertEqual(evidence["signed_approval"]["approved_by"], "model-mgr-1")
        # Clinical safety assertion stays false: schema validity never implies clinical safety.
        self.assertFalse(evidence["clinical_safety_asserted"])

    def test_retire_requires_prior_approval(self) -> None:
        retire_without_approval = self.model_manager_client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/retire",
            json={"retired_by": "model-mgr-1", "rationale": "superseded"},
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(retire_without_approval.status_code, 409)
        self.assertEqual(
            retire_without_approval.json()["error"]["code"], "BNM_MODEL_NOT_APPROVED"
        )

        self.model_manager_client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/approve",
            json={"approved_by": "model-mgr-1"},
            headers={"x-csrf-token": "csrf-validate"},
        )
        retire = self.model_manager_client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/retire",
            json={"retired_by": "model-mgr-1", "rationale": "superseded"},
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(retire.status_code, 200, retire.text)
        payload = retire.json()["data"]
        self.assertEqual(payload["clinical_status"], "retired")
        self.assertEqual(payload["signed_approval"]["status"], "retired")

    def test_revoke_returns_model_to_unvalidated(self) -> None:
        self.model_manager_client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/approve",
            json={"approved_by": "model-mgr-1"},
            headers={"x-csrf-token": "csrf-validate"},
        )
        revoke = self.model_manager_client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/revoke",
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(revoke.status_code, 200)
        payload = revoke.json()["data"]
        self.assertEqual(payload["clinical_status"], "unvalidated")
        self.assertIsNone(payload["signed_approval"])

    def test_approve_rejects_unknown_stable_id_with_404(self) -> None:
        response = self.model_manager_client.post(
            "/api/bn-manager/v1/models/bnm.never-heard-of/approve",
            json={"approved_by": "model-mgr-1"},
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "BNM_MODEL_NOT_FOUND")

    def test_governance_routes_fail_closed_when_key_is_missing(self) -> None:
        # Without a governance signing key the approve endpoint refuses rather than
        # silently fabricating an unsigned approval.
        response = self.model_manager_client.post(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/approve",
            json={"approved_by": "model-mgr-1"},
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(response.status_code, 201)

        # Build a second client without a governance key.
        keyless_client = TestClient(
            create_app(
                session_adapter=ModelManagerSessionAdapter(),
                evaluation_store=InMemoryEvaluationStore(),
                governance_store=InMemoryGovernanceStore(),
                governance_key=None,
            )
        )
        approved = self.model_manager_client.get(
            "/api/bn-manager/v1/models/bnm.pharmacotherapy/governance",
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(approved.status_code, 200)

        keyless_response = keyless_client.post(
            "/api/bn-manager/v1/models/bnm.treatment-setting/approve",
            json={"approved_by": "model-mgr-2"},
            headers={"x-csrf-token": "csrf-validate"},
        )
        self.assertEqual(keyless_response.status_code, 503)
        self.assertEqual(
            keyless_response.json()["error"]["code"], "BNM_GOVERNANCE_KEY_UNAVAILABLE"
        )

    def test_signed_approval_signature_round_trips_through_store(self) -> None:
        approval = SignedApproval(
            stable_id="bnm.pharmacotherapy",
            status=ClinicalStatus.APPROVED,
            model_hash="sha256:" + "f" * 64,
            approved_at="2026-07-23T13:00:00Z",
            approved_by="model-mgr-3",
            signature=sign_approval(
                stable_id="bnm.pharmacotherapy",
                status=ClinicalStatus.APPROVED,
                model_hash="sha256:" + "f" * 64,
                approved_at="2026-07-23T13:00:00Z",
                approved_by="model-mgr-3",
                secret_key=GOVERNANCE_KEY,
            ),
        )
        store = InMemoryGovernanceStore()
        store.put(approval)
        loaded = store.get(approval.stable_id)
        assert loaded is not None
        self.assertEqual(loaded.to_dict()["signature"], approval.signature)


if __name__ == "__main__":
    unittest.main()
