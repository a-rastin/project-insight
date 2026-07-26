from __future__ import annotations

import unittest

from fastapi import Request
from fastapi.testclient import TestClient

from bn_manager_backend.auth_adapter import SessionState, session_from_payload
from bn_manager_backend.evaluation_store import InMemoryEvaluationStore
from bn_manager_backend.main import create_app


class FakeSessionAdapter:
    def __init__(self, session: SessionState) -> None:
        self.session = session

    def fetch_session(self, request: Request) -> SessionState:
        return self.session


class AuthenticationGuardTests(unittest.TestCase):
    def test_valid_psychiatrist_can_evaluate_registered_xml_model(self) -> None:
        client = self._client(
            {
                "schemaVersion": "1.0.0",
                "authenticated": True,
                "user": {"id": "psy-1", "roles": ["psychiatrist"]},
                "session": {"id": "session-1", "expiresAt": "2099-01-01T00:00:00Z"},
                "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
            }
        )
        response = client.post(
            "/api/bn-manager/v1/dashboard/evaluate",
            json={
                "model": {"model_id": "bnm.clozapine-suicide-risk"},
                "evidence": {
                    "Schizophrenia_Suicide_Indication": "Met",
                },
            },
            headers={"x-csrf-token": "csrf-1", "Cookie": "csrf_token=csrf-1"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["target"], "Clinical_Action_Pattern")
        self.assertAlmostEqual(sum(payload["data"]["values"].values()), 1.0)
        self.assertTrue(all("probability" in row for row in payload["data"]["rankings"]))
        evaluation = payload["data"]["evaluation"]
        self.assertRegex(evaluation["evaluationId"], r"^[0-9a-f-]{36}$")
        self.assertEqual(evaluation["modelId"], "bnm.clozapine-suicide-risk")
        self.assertRegex(evaluation["modelHash"], r"^sha256:[a-f0-9]{64}$")
        self.assertEqual(evaluation["target"], "Clinical_Action_Pattern")
        self.assertIn("Schizophrenia_Suicide_Indication", evaluation["acceptedEvidence"])
        self.assertEqual(evaluation["caller"]["subject"], "psy-1")
        self.assertEqual(evaluation["caller"]["surface"], "Dashboard")
        self.assertTrue(evaluation["idempotencyKey"])
        self.assertRegex(evaluation["bindingHash"], r"^sha256:[a-f0-9]{64}$")
        self.assertEqual(evaluation["engineVersion"].split("/")[0], "clinical_graph_models")

    def test_treatment_plan_adapter_uses_shared_evaluation_interface(self) -> None:
        client = self._client(
            {
                "schemaVersion": "1.0.0",
                "authenticated": True,
                "user": {"id": "psy-1", "roles": ["psychiatrist"]},
                "session": {"id": "session-tp", "expiresAt": "2099-01-01T00:00:00Z"},
                "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
            }
        )

        response = client.post(
            "/api/bn-manager/v1/treatment-plan/evaluate",
            json={"model": {"model_id": "bnm.clozapine-suicide-risk"}},
            headers={"x-csrf-token": "csrf-tp", "Cookie": "csrf_token=csrf-tp"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["surface"], "Treatment Plan")

    def test_evaluation_adapters_enforce_caller_specific_roles(self) -> None:
        cases = (
            ("intake", ["intakeclinician"], "/api/bn-manager/v1/add-new-patient/evaluate", 200),
            ("intake", ["intakeclinician"], "/api/bn-manager/v1/dashboard/evaluate", 403),
            ("care", ["careteam"], "/api/bn-manager/v1/follow-up/evaluate", 200),
            ("care", ["careteam"], "/api/bn-manager/v1/add-new-patient/evaluate", 403),
        )
        for name, roles, path, expected_status in cases:
            with self.subTest(name=name, path=path):
                client = self._client(
                    {
                        "schemaVersion": "1.0.0",
                        "authenticated": True,
                        "user": {"id": f"{name}-1", "roles": roles},
                        "session": {"id": f"session-{name}", "expiresAt": "2099-01-01T00:00:00Z"},
                        "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
                    }
                )
                response = client.post(
                    path,
                    json={"model": {"model_id": "bnm.clozapine-suicide-risk"}},
                    headers={"x-csrf-token": "csrf", "Cookie": "csrf_token=csrf"},
                )
                self.assertEqual(response.status_code, expected_status)

    def test_evaluate_idempotent_retry_returns_same_record(self) -> None:
        store = InMemoryEvaluationStore()
        client = TestClient(
            create_app(
                session_adapter=FakeSessionAdapter(
                    session_from_payload(
                        {
                            "schemaVersion": "1.0.0",
                            "authenticated": True,
                            "user": {"id": "psy-1", "roles": ["psychiatrist"]},
                            "session": {"id": "session-idem", "expiresAt": "2099-01-01T00:00:00Z"},
                            "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
                        }
                    )
                ),
                evaluation_store=store,
            )
        )
        body = {
            "model": {"model_id": "bnm.clozapine-suicide-risk"},
            "evidence": {"Schizophrenia_Suicide_Indication": "Met"},
        }
        headers = {
            "x-csrf-token": "csrf-1",
            "Cookie": "csrf_token=csrf-1",
            "Idempotency-Key": "idemp-evaluate-retry-0001",
        }
        first = client.post("/api/bn-manager/v1/dashboard/evaluate", json=body, headers=headers)
        second = client.post("/api/bn-manager/v1/dashboard/evaluate", json=body, headers=headers)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            first.json()["data"]["evaluation"]["evaluationId"],
            second.json()["data"]["evaluation"]["evaluationId"],
        )

    def test_evaluate_idempotency_conflict_on_changed_payload(self) -> None:
        store = InMemoryEvaluationStore()
        client = TestClient(
            create_app(
                session_adapter=FakeSessionAdapter(
                    session_from_payload(
                        {
                            "schemaVersion": "1.0.0",
                            "authenticated": True,
                            "user": {"id": "psy-1", "roles": ["psychiatrist"]},
                            "session": {"id": "session-conflict", "expiresAt": "2099-01-01T00:00:00Z"},
                            "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
                        }
                    )
                ),
                evaluation_store=store,
            )
        )
        headers = {
            "x-csrf-token": "csrf-1",
            "Cookie": "csrf_token=csrf-1",
            "Idempotency-Key": "idemp-evaluate-conflict-01",
        }
        first = client.post(
            "/api/bn-manager/v1/dashboard/evaluate",
            json={
                "model": {"model_id": "bnm.clozapine-suicide-risk"},
                "evidence": {"Schizophrenia_Suicide_Indication": "Met"},
            },
            headers=headers,
        )
        second = client.post(
            "/api/bn-manager/v1/dashboard/evaluate",
            json={
                "model": {"model_id": "bnm.clozapine-suicide-risk"},
                "evidence": {"Schizophrenia_Suicide_Indication": "NotMet"},
            },
            headers=headers,
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(second.json()["error"]["code"], "BNM_IDEMPOTENCY_CONFLICT")

    def test_valid_admin_can_validate_registered_xml_model(self) -> None:
        client = self._client(
            {
                "schemaVersion": "1.0.0",
                "authenticated": True,
                "user": {"id": "admin-1", "roles": ["admin"]},
                "session": {"id": "session-2", "expiresAt": "2099-01-01T00:00:00Z"},
                "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
            }
        )
        response = client.post(
            "/api/bn-manager/v1/models/validate",
            json={"model": {"model_id": "bnm.pharmacotherapy"}},
            headers={"x-csrf-token": "csrf-2", "Cookie": "csrf_token=csrf-2"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["data"]["valid"])
        self.assertEqual(payload["data"]["checked_by"], "admin-1")

    def test_expired_session_is_rejected_before_model_loading(self) -> None:
        client = self._client(
            {
                "schemaVersion": "1.0.0",
                "authenticated": True,
                "user": {"id": "psy-1", "roles": ["psychiatrist"]},
                "session": {"id": "session-3", "expiresAt": "2000-01-01T00:00:00Z"},
                "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
            }
        )
        response = client.post(
            "/api/bn-manager/v1/dashboard/evaluate",
            json={},
            headers={"x-csrf-token": "csrf-3", "Cookie": "csrf_token=csrf-3"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "BNM_UNAUTHORIZED")

    def test_disclaimer_and_forced_password_flags_do_not_block_sessions(self) -> None:
        for gates in (
            {"disclaimerAccepted": False, "passwordChangeRequired": False},
            {"disclaimerAccepted": True, "passwordChangeRequired": True},
        ):
            with self.subTest(gates=gates):
                session = session_from_payload({"schemaVersion": "1.0.0", "authenticated": True, "user": {"id": "psy-1", "roles": ["psychiatrist"]}, "session": {"id": "session-4", "expiresAt": "2099-01-01T00:00:00Z"}, "gates": gates})
                self.assertTrue(session.active)

    def test_csrf_rejection_blocks_write_route(self) -> None:
        client = self._client(
            {
                "schemaVersion": "1.0.0",
                "authenticated": True,
                "user": {"id": "psy-1", "roles": ["psychiatrist"]},
                "session": {"id": "session-6", "expiresAt": "2099-01-01T00:00:00Z"},
                "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
            }
        )
        response = client.post(
            "/api/bn-manager/v1/dashboard/evaluate",
            json={},
            headers={"x-csrf-token": "csrf-bad", "Cookie": "csrf_token=csrf-good"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "BNM_FORBIDDEN")

    def test_legacy_flat_payload_is_rejected(self) -> None:
        self.assertFalse(session_from_payload({"authenticated": True, "userId": "psy-1", "roles": ["psychiatrist"]}).active)

    def _client(self, payload: dict) -> TestClient:
        return TestClient(
            create_app(
                session_adapter=FakeSessionAdapter(session_from_payload(payload)),
                evaluation_store=InMemoryEvaluationStore(),
            )
        )


if __name__ == "__main__":
    unittest.main()
