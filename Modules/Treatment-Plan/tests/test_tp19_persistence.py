import sqlite3
import tempfile
import unittest
from contextlib import closing
import os
from datetime import datetime, timezone
from pathlib import Path

from treatment_plan.repository import InMemoryRepository, RuntimeRecord
from treatment_plan.postgres_repository import PostgreSQLRepository
from treatment_plan.retention import RetentionPolicy
from treatment_plan.retention import RetentionApprovalRequired
from treatment_plan.sqlite_repository import SQLiteRepository
from treatment_plan.migration import MigrationRunner


TP19_TABLES = {
    "recommendation_runs",
    "input_snapshots",
    "plans",
    "plan_versions",
    "plan_items",
    "plan_edits",
    "safety_findings",
    "evidence_links",
    "clinical_provenance",
}


class TP19MigrationTests(unittest.TestCase):
    def test_one_migration_set_renders_for_both_database_dialects(self):
        migrations = Path(__file__).parents[1] / "treatment_plan" / "migrations"
        sqlite_migrations = MigrationRunner(migrations, "sqlite").migrations()
        postgres_migrations = MigrationRunner(migrations, "postgres").migrations()
        self.assertEqual(
            [migration.version for migration in sqlite_migrations],
            [migration.version for migration in postgres_migrations],
        )
        self.assertTrue(sqlite_migrations)
        for migration in sqlite_migrations + postgres_migrations:
            self.assertNotIn("{{", migration.up)
            self.assertNotIn("{{", migration.down)
        postgres_sql = "\n".join(migration.up for migration in postgres_migrations)
        self.assertNotIn("RAISE(ABORT", postgres_sql)
        self.assertIn("UUID", postgres_sql)
        self.assertIn("JSONB", postgres_sql)

    def test_migrations_round_trip_and_can_be_reapplied(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "treatment-plan.sqlite"
            repository = SQLiteRepository(database)

            applied = repository.migrate()
            repository.put(RuntimeRecord("round-trip", "before rollback"))

            with closing(sqlite3.connect(database)) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }
            self.assertTrue(TP19_TABLES <= tables)
            self.assertTrue(applied)

            repository.rollback()
            repository.migrate()
            repository.put(RuntimeRecord("round-trip", "after reapply"))
            self.assertEqual(
                RuntimeRecord("round-trip", "after reapply"),
                repository.get("round-trip"),
            )

    def test_uuid_idempotency_foreign_key_and_json_envelope_constraints(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "constraints.sqlite"
            SQLiteRepository(database).migrate()
            with closing(sqlite3.connect(database)) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        "INSERT INTO recommendation_runs VALUES (?, ?, ?, ?, ?, ?)",
                        ("not-a-uuid", "key", "hash", "pending", "2026-01-01", None),
                    )
                run_id = "10000000-0000-4000-8000-000000000001"
                connection.execute(
                    "INSERT INTO recommendation_runs VALUES (?, ?, ?, ?, ?, ?)",
                    (run_id, "key", "hash", "pending", "2026-01-01", None),
                )
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        "INSERT INTO recommendation_runs VALUES (?, ?, ?, ?, ?, ?)",
                        ("10000000-0000-4000-8000-000000000002", "key", "other", "pending", "2026-01-01", None),
                    )
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        "INSERT INTO input_snapshots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        ("10000000-0000-4000-8000-000000000003", run_id, "patient", "10000000-0000-4000-8000-000000000004", "1.0.0", "not-json", "2026-01-01", "2027-01-01", None),
                    )


class TP19BackupTests(unittest.TestCase):
    def test_sqlite_backup_restores_a_consistent_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "live.sqlite"
            backup = Path(directory) / "backup.sqlite"
            repository = SQLiteRepository(database)
            repository.migrate()
            repository.put(RuntimeRecord("clinical", "original"))

            repository.backup(backup)
            repository.put(RuntimeRecord("clinical", "changed"))
            repository.restore(backup)

            self.assertEqual(
                RuntimeRecord("clinical", "original"), repository.get("clinical")
            )


class RepositoryContractTests(unittest.TestCase):
    def assert_repository_contract(self, repository):
        self.assertTrue(repository.migrate())
        self.assertEqual((), repository.migrate())
        self.assertTrue(repository.ping())
        self.assertIsNone(repository.get("contract-key"))
        repository.put(RuntimeRecord("contract-key", "first"))
        repository.put(RuntimeRecord("contract-key", "updated"))
        self.assertEqual(
            RuntimeRecord("contract-key", "updated"), repository.get("contract-key")
        )

    def test_in_memory_adapter_passes_repository_contract(self):
        self.assert_repository_contract(InMemoryRepository())

    def test_sqlite_adapter_passes_repository_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assert_repository_contract(
                SQLiteRepository(Path(directory) / "contract.sqlite")
            )

    def test_postgresql_adapter_passes_repository_contract(self):
        dsn = os.getenv("TP_TEST_POSTGRES_DSN")
        if not dsn:
            self.skipTest("TP_TEST_POSTGRES_DSN is not configured")
        repository = PostgreSQLRepository(dsn)
        repository.rollback()
        self.assert_repository_contract(repository)
        repository.rollback()


class RetentionPolicyTests(unittest.TestCase):
    def test_retention_rejects_incomplete_governance_approval(self):
        with self.assertRaises(RetentionApprovalRequired):
            RetentionPolicy.approved(
                "policy-2026-01",
                {"privacy_officer"},
                datetime(2026, 1, 2, tzinfo=timezone.utc),
            )

    def test_expired_phi_is_redacted_while_audit_records_are_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "retention.sqlite"
            repository = SQLiteRepository(database)
            repository.migrate()
            run_id = "00000000-0000-4000-8000-000000000001"
            snapshot_id = "00000000-0000-4000-8000-000000000002"
            plan_id = "00000000-0000-4000-8000-000000000003"
            version_id = "00000000-0000-4000-8000-000000000004"
            edit_id = "00000000-0000-4000-8000-000000000005"
            provenance_id = "00000000-0000-4000-8000-000000000006"
            audit_id = "00000000-0000-4000-8000-000000000007"
            expired = "2026-01-01T00:00:00+00:00"
            retained = "2036-01-01T00:00:00+00:00"
            with closing(sqlite3.connect(database)) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
                connection.execute(
                    "INSERT INTO recommendation_runs VALUES (?, ?, ?, ?, ?, ?)",
                    (run_id, "run-key", "sha256:input", "completed", expired, expired),
                )
                connection.execute(
                    "INSERT INTO input_snapshots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (snapshot_id, run_id, "patient-hash", audit_id, "1.0.0", "{}", expired, expired, None),
                )
                connection.execute(
                    "INSERT INTO plans VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (plan_id, run_id, "plan-key", "final", 1, expired, expired, expired, None),
                )
                connection.execute(
                    "INSERT INTO plan_versions VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (version_id, plan_id, 1, "1.0.0", "sha256:plan", "{}", expired),
                )
                connection.execute(
                    "INSERT INTO plan_edits VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (edit_id, plan_id, version_id, 1, "doctor", "edit-key", "1.0.0", "{}", expired),
                )
                connection.execute(
                    "INSERT INTO clinical_provenance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (provenance_id, version_id, audit_id, "Diagnosis", "source-1", "v1", "1.0.0", "{}", expired, retained),
                )
                connection.commit()

            result = repository.apply_retention(
                RetentionPolicy.approved(
                    "policy-2026-01",
                    {"privacy_officer", "clinical_safety_officer"},
                    datetime(2026, 1, 2, tzinfo=timezone.utc),
                ),
                datetime(2027, 1, 1, tzinfo=timezone.utc),
            )

            with closing(sqlite3.connect(database)) as connection:
                snapshot = connection.execute(
                    "SELECT snapshot_envelope, deleted_at FROM input_snapshots"
                ).fetchone()
                edits = connection.execute("SELECT COUNT(*) FROM plan_edits").fetchone()[0]
                provenance = connection.execute(
                    "SELECT COUNT(*) FROM clinical_provenance"
                ).fetchone()[0]
            self.assertIsNone(snapshot[0])
            self.assertIsNotNone(snapshot[1])
            self.assertEqual(1, result.snapshots_redacted)
            self.assertEqual(1, edits)
            self.assertEqual(1, provenance)
if __name__ == "__main__":
    unittest.main()
