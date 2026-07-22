import os
import sqlite3
from uuid import UUID

from _support import AuthTestCase
import security


class AuthUuidContractTests(AuthTestCase):
    def test_session_contract_exposes_uuid_identity_and_structured_gates(self):
        client = self.login_admin()
        response = client.get("/api/auth/session")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body), {"schemaVersion", "authenticated", "user", "session", "gates"})
        self.assertIs(body["authenticated"], True)
        self.assertEqual(body["schemaVersion"], "1.0.0")
        self.assertEqual(set(body["user"]), {"id", "username", "roles", "displayName"})
        self.assertEqual(body["user"]["username"], "Admin")
        self.assertEqual(body["user"]["roles"], ["admin"])
        self.assertEqual(body["gates"], {"disclaimerAccepted": True, "passwordChangeRequired": False})
        UUID(body["user"]["id"])
        UUID(body["session"]["id"])
        self.assertNotIn("user_id", body)
        self.assertNotIn("message", body)

        user = security.get_user("Admin")
        token = client.cookies.get(security.cfg("AUTH_COOKIE_NAME"))
        session = security.get_conn().execute(
            "SELECT session_uuid FROM sessions WHERE token = ?", (token,)
        ).fetchone()
        self.assertEqual(body["user"]["id"], user["user_uuid"])
        self.assertEqual(body["session"]["id"], session["session_uuid"])

    def test_legacy_integer_database_backfills_uuid_keys_transactionally(self):
        self.reset_connection()
        legacy_db = os.path.join(self._tmpdir.name, "legacy-uuid.sqlite3")
        conn = sqlite3.connect(legacy_db)
        conn.executescript(
            """
            PRAGMA user_version = 6;
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL CHECK (role IN ('admin', 'psychiatrist')),
                password_hash TEXT NOT NULL,
                disabled BOOLEAN NOT NULL DEFAULT 0,
                must_change_password BOOLEAN NOT NULL DEFAULT 0,
                disclaimer_signed BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                expires_at INTEGER NOT NULL
            );
            CREATE TABLE disclaimer_acceptances (
                user_id INTEGER NOT NULL REFERENCES users(id),
                version TEXT NOT NULL,
                accepted_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, version)
            );
            CREATE TABLE login_failures (
                identity TEXT PRIMARY KEY,
                username_key TEXT NOT NULL,
                client_key TEXT NOT NULL,
                failure_count INTEGER NOT NULL,
                first_failed_at INTEGER NOT NULL,
                last_failed_at INTEGER NOT NULL,
                locked_until INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id INTEGER,
                actor_name TEXT NOT NULL,
                target_id INTEGER,
                target_name TEXT,
                action TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'success',
                metadata TEXT,
                client_ip TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        password_hash = security.hash_password("secret")
        conn.execute(
            "INSERT INTO users (username, role, password_hash) VALUES (?, ?, ?)",
            ("legacy-doc", "psychiatrist", password_hash),
        )
        user_id = conn.execute("SELECT id FROM users WHERE username = 'legacy-doc'").fetchone()[0]
        conn.execute(
            "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
            ("legacy-token", user_id, 2_000_000_000),
        )
        conn.commit()
        conn.close()

        os.environ["AUTH_DB_PATH"] = legacy_db
        user = security.get_user("legacy-doc")
        session = security.get_conn().execute(
            "SELECT user_id, session_uuid FROM sessions WHERE token = 'legacy-token'"
        ).fetchone()
        self.assertIsNotNone(user["user_uuid"])

        self.assertIsNotNone(session["session_uuid"])

        UUID(user["user_uuid"])
        UUID(session["session_uuid"])
        self.assertEqual(session["user_id"], user["id"])

        user_columns = {row[1]: row[3] for row in security.get_conn().execute("PRAGMA table_info(users)")}
        session_columns = {row[1]: row[3] for row in security.get_conn().execute("PRAGMA table_info(sessions)")}
        self.assertEqual(user_columns["user_uuid"], 1)
        self.assertEqual(session_columns["session_uuid"], 1)

        with self.assertRaises(sqlite3.IntegrityError):
            security.get_conn().execute(
                "INSERT INTO users (username, role, password_hash, user_uuid) VALUES (?, ?, ?, ?)",
                ("duplicate", "admin", password_hash, user["user_uuid"]),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            security.get_conn().execute(
                "INSERT INTO users (username, role, password_hash, user_uuid) VALUES (?, ?, ?, NULL)",
                ("null-uuid", "admin", password_hash),
            )


if __name__ == "__main__":
    import unittest

    unittest.main()

