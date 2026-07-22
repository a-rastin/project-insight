from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta


def future_epoch() -> int:
    return int((datetime.now(UTC) + timedelta(hours=1)).timestamp())


class AuthAdapterContractTest(unittest.TestCase):
    def test_canonical_uuid_identity_normalizes_lowercase_multi_role_session(self) -> None:
        from add_new_patient_backend.auth import normalize_psychiatrist_session

        payload = {
            "schemaVersion": "1.0.0",
            "authenticated": True,
            "user": {
                "id": "11111111-1111-4111-8111-111111111111",
                "username": "clinician",
                "roles": ["ADMIN", "psychiatrist"],
                "displayName": "Verified Clinician",
            },
            "session": {
                "id": "22222222-2222-4222-8222-222222222222",
                "expiresAt": "2099-01-01T00:00:00Z",
            },
            "gates": {
                "disclaimerAccepted": True,
                "passwordChangeRequired": False,
            },
        }

        identity = normalize_psychiatrist_session(payload)

        self.assertIsNotNone(identity)
        assert identity is not None
        self.assertEqual(identity["authSessionId"], "22222222-2222-4222-8222-222222222222")
        self.assertEqual(identity["user"]["id"], "11111111-1111-4111-8111-111111111111")
        self.assertEqual(identity["user"]["role"], "PSYCHIATRIST")
        self.assertEqual(identity["user"]["roles"], ["ADMIN", "PSYCHIATRIST"])

    def test_structured_gate_booleans_block_without_reading_message(self) -> None:
        from add_new_patient_backend.auth import normalize_authenticated_session

        base = {
            "schemaVersion": "1.0.0",
            "authenticated": True,
            "user": {"id": "user-uuid", "roles": ["psychiatrist"]},
            "session": {"id": "session-uuid", "expiresAt": "2099-01-01T00:00:00Z"},
            "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
            "message": "password change required",
        }
        self.assertIsNotNone(normalize_authenticated_session(base))

        for gates in [
            {"disclaimerAccepted": False, "passwordChangeRequired": False},
            {"disclaimerAccepted": True, "passwordChangeRequired": True},
        ]:
            with self.subTest(gates=gates):
                blocked = {**base, "gates": gates}
                self.assertIsNone(normalize_authenticated_session(blocked))

    def test_legacy_and_canonical_adapters_preserve_identity(self) -> None:
        from add_new_patient_backend.auth import normalize_authenticated_session

        canonical = {
            "authenticated": True,
            "user": {
                "id": "11111111-1111-4111-8111-111111111111",
                "username": "clinician",
                "roles": ["psychiatrist"],
            },
            "session": {
                "id": "22222222-2222-4222-8222-222222222222",
                "expiresAt": "2099-01-01T00:00:00Z",
            },
            "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
        }
        legacy = {
            "ok": True,
            "user_uuid": "11111111-1111-4111-8111-111111111111",
            "session_uuid": "22222222-2222-4222-8222-222222222222",
            "username": "clinician",
            "role": "psychiatrist",
            "expires_at": future_epoch(),
            "disclaimer_status": "signed",
            "must_change_password": False,
            "message": "not a gate",
        }

        canonical_identity = normalize_authenticated_session(canonical)
        legacy_identity = normalize_authenticated_session(legacy)

        self.assertIsNotNone(canonical_identity)
        self.assertIsNotNone(legacy_identity)
        assert canonical_identity is not None and legacy_identity is not None
        self.assertEqual(canonical_identity["authSessionId"], legacy_identity["authSessionId"])
        self.assertEqual(canonical_identity["user"]["id"], legacy_identity["user"]["id"])
        self.assertEqual(canonical_identity["user"]["role"], legacy_identity["user"]["role"])
        self.assertEqual(canonical_identity["user"]["roles"], legacy_identity["user"]["roles"])
