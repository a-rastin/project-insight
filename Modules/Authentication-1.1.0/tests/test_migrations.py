import os
import sqlite3

from _support import AuthTestCase, assert_auth_schema
import security


class AuthMigrationTests(AuthTestCase):
    def test_legacy_user_role_database_migrates_in_place(self):
        self.reset_connection()
        legacy_db = os.path.join(self._tmpdir.name, "legacy.sqlite3")
        conn = sqlite3.connect(legacy_db)
        conn.executescript(
            """
            CREATE TABLE users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT NOT NULL UNIQUE,
                role          TEXT NOT NULL CHECK (role IN ('admin', 'user')),
                password_hash TEXT NOT NULL,
                disclaimer_signed BOOLEAN NOT NULL DEFAULT 0,
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE sessions (
                token  TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                expires_at INTEGER NOT NULL
            );
            """
        )
        conn.execute(
            "INSERT INTO users (username, role, password_hash, disclaimer_signed) VALUES (?, ?, ?, 1)",
            ("legacy-doc", "user", security.hash_password("secret")),
        )
        conn.commit()
        conn.close()

        os.environ["AUTH_DB_PATH"] = legacy_db
        migrated_user = security.get_user("legacy-doc")
        self.assertEqual(migrated_user["role"], "psychiatrist")
        assert_auth_schema(self, security.get_conn())

        client = self.client()
        login = client.post(
            "/api/auth/login",
            json={"username": "legacy-doc", "password": "secret", "role": "user"},
        )
        self.assertEqual(login.status_code, 200)
        self.assertEqual(client.get("/api/auth/session/legacy").json()["role"], "psychiatrist")

    def test_current_unversioned_database_gets_schema_version_without_data_loss(self):
        self.reset_connection()
        current_db = os.path.join(self._tmpdir.name, "current-unversioned.sqlite3")
        conn = sqlite3.connect(current_db)
        conn.executescript(
            """
            CREATE TABLE users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT NOT NULL UNIQUE,
                role          TEXT NOT NULL CHECK (role IN ('admin', 'psychiatrist')),
                password_hash TEXT NOT NULL,
                disabled      BOOLEAN NOT NULL DEFAULT 0,
                must_change_password BOOLEAN NOT NULL DEFAULT 0,
                disclaimer_signed BOOLEAN NOT NULL DEFAULT 0,
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE sessions (
                token  TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                expires_at INTEGER NOT NULL
            );
            CREATE TABLE disclaimer_acceptances (
                user_id     INTEGER NOT NULL REFERENCES users(id),
                version     TEXT NOT NULL,
                accepted_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, version)
            );
            CREATE INDEX idx_disclaimer_acceptances_user_id ON disclaimer_acceptances(user_id);
            CREATE TABLE login_failures (
                identity        TEXT PRIMARY KEY,
                username_key    TEXT NOT NULL,
                client_key      TEXT NOT NULL,
                failure_count   INTEGER NOT NULL,
                first_failed_at INTEGER NOT NULL,
                last_failed_at  INTEGER NOT NULL,
                locked_until    INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX idx_login_failures_last_failed_at ON login_failures(last_failed_at);
            CREATE TABLE audit_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id    INTEGER,
                actor_name  TEXT NOT NULL,
                target_id   INTEGER,
                target_name TEXT,
                action      TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT 'success',
                metadata    TEXT,
                client_ip   TEXT,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
            CREATE INDEX idx_audit_log_actor_id ON audit_log(actor_id);
            """
        )
        conn.execute(
            """
            INSERT INTO users (
                username, role, password_hash, disabled,
                must_change_password, disclaimer_signed
            ) VALUES (?, ?, ?, 1, 1, 1)
            """,
            ("current-doc", "psychiatrist", security.hash_password("secret")),
        )
        conn.commit()
        conn.close()

        os.environ["AUTH_DB_PATH"] = current_db
        current_user = security.get_user("current-doc")
        self.assertEqual(current_user["role"], "psychiatrist")
        self.assertEqual(current_user["disabled"], 1)
        self.assertEqual(current_user["must_change_password"], 1)
        assert_auth_schema(self, security.get_conn())


if __name__ == "__main__":
    import unittest

    unittest.main()
