from __future__ import annotations

import unittest

from fastapi import Request
from fastapi.testclient import TestClient

from bn_manager_backend.auth_adapter import SessionState, session_from_payload
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

    def test_disclaimer_and_forced_password_sessions_are_blocked(self) -> None:
        blocked_payloads = (
            ({"schemaVersion": "1.0.0", "authenticated": True, "user": {"id": "psy-1", "roles": ["psychiatrist"]}, "session": {"id": "session-4", "expiresAt": "2099-01-01T00:00:00Z"}, "gates": {"disclaimerAccepted": False, "passwordChangeRequired": False}}, "disclaimer_required"),
            ({"schemaVersion": "1.0.0", "authenticated": True, "user": {"id": "psy-1", "roles": ["psychiatrist"]}, "session": {"id": "session-5", "expiresAt": "2099-01-01T00:00:00Z"}, "gates": {"disclaimerAccepted": True, "passwordChangeRequired": True}}, "forced_password_change"),
        )
        for session_payload, reason in blocked_payloads:
            with self.subTest(reason=reason):
                client = self._client(session_payload)
                response = client.post(
                    "/api/bn-manager/v1/dashboard/evaluate",
                    json={},
                    headers={"x-csrf-token": "csrf", "Cookie": "csrf_token=csrf"},
                )
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json()["error"]["details"]["reason"], reason)

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
        return TestClient(create_app(session_adapter=FakeSessionAdapter(session_from_payload(payload))))


if __name__ == "__main__":
    unittest.main()
