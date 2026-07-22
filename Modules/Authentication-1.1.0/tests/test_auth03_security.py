import os
import sqlite3
from unittest.mock import patch

from _support import AuthTestCase
import security


class Auth03SecurityTests(AuthTestCase):
    def test_account_state_changes_revoke_every_active_session(self):
        user_id = security.register_user("auth03-user", "psychiatrist", "secret")
        security.set_disclaimer_signed(user_id)

        disabled_token = security.issue_token(user_id, "psychiatrist")
        self.assertIsNotNone(security.resolve_session(disabled_token))
        security.set_user_disabled(user_id, True)
        self.assertIsNone(security.resolve_session(disabled_token))

        security.set_user_disabled(user_id, False)
        security.set_disclaimer_signed(user_id)
        role_token = security.issue_token(user_id, "psychiatrist")
        security.update_user_role(user_id, "admin")
        self.assertIsNone(security.resolve_session(role_token))

        password_token = security.issue_token(user_id, "admin")
        security.reset_user_password(user_id, "new-secret")
        self.assertIsNone(security.resolve_session(password_token))

    def test_session_expiry_allows_configured_clock_skew_but_not_beyond_it(self):
        original_now = security._now
        user = security.get_user("Admin")
        token = security.issue_token(user["id"], "admin", expires_in=10)
        expires_at = security.verify_token(token)["exp"]
        now = [expires_at]
        security._now = lambda: now[0]
        try:

            now[0] = expires_at
            self.assertIsNotNone(security.resolve_session(token))
            now[0] = expires_at + security.cfg_int("AUTH_CLOCK_SKEW_SECONDS", 60) - 1
            self.assertIsNotNone(security.resolve_session(token))
            now[0] += 2
            self.assertIsNone(security.resolve_session(token))
        finally:
            security._now = original_now

    def test_login_attempt_storage_is_bounded_and_success_recovers(self):
        with patch.dict(
            os.environ,
            {
                "AUTH_LOGIN_FAILURE_MAX_ENTRIES": "2",
                "AUTH_LOGIN_FAILURE_LIMIT": "3",
            },
        ):
            for _ in range(3):
                security.record_login_failure("recover", "client-4")
            self.assertFalse(security.login_attempt_allowed("recover", "client-4"))
            security.record_login_success("recover", "client-4")
            self.assertTrue(security.login_attempt_allowed("recover", "client-4"))

            security.record_login_failure("one", "client-1")
            security.record_login_failure("two", "client-2")
            security.record_login_failure("three", "client-3")
            count = security.get_conn().execute("SELECT COUNT(*) FROM login_failures").fetchone()[0]
            self.assertLessEqual(count, 2)
    def test_auth_audit_is_append_only_and_redacts_secrets(self):
        security.record_audit(
            "login",
            actor={"id": 1, "username": "clinician"},
            metadata={
                "password": "plain-secret",
                "nested": {"token": "jwt-secret", "safe": "kept"},
            },
        )
        entry = security.list_audit_entries(limit=1)[0]
        self.assertNotIn("plain-secret", entry["metadata"])
        self.assertNotIn("jwt-secret", entry["metadata"])
        self.assertIn("safe", entry["metadata"])

        conn = security.get_conn()
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("UPDATE audit_log SET status = 'failure' WHERE id = ?", (entry["id"],))
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM audit_log WHERE id = ?", (entry["id"],))

    def test_logout_persists_auth_audit_event(self):
        client = self.login_admin()
        response = client.post("/api/auth/logout")
        self.assertEqual(response.status_code, 200)
        entry = security.list_audit_entries(limit=1)[0]
        self.assertEqual(entry["action"], "logout")
        self.assertEqual(entry["status"], "success")
    def test_tls_cookie_policy_is_secure_http_only_and_same_site(self):
        with patch.dict(os.environ, {"AUTH_SECURE_COOKIE": "true"}):
            session = security.cookie_kwargs()
            csrf = security.csrf_cookie_kwargs()

        self.assertTrue(session["secure"])
        self.assertTrue(session["httponly"])
        self.assertEqual(session["samesite"], "lax")
        self.assertTrue(csrf["secure"])
        self.assertFalse(csrf["httponly"])
        self.assertEqual(csrf["samesite"], "lax")


if __name__ == "__main__":
    import unittest

    unittest.main()
