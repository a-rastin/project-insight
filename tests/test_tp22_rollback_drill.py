"""TP22.5 rollback drill contract tests.

The rollback drill is an offline procedure that records the current immutable
image digest and a verified backup, applies forward-only migrations, rolls the
application image back WITHOUT automatic down-migrations, restores data only
after a separately approved recovery decision, and re-runs the readiness,
unified routing, TLS, recovery, and integrity checks after rollback.

These tests pin the offline contract surface of the drill. They do not require
Docker, real images, external credentials, or fabricated clinical approvals.
"""

import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_unified_deployment import (  # noqa: E402
    ROLLBACK_DRILL_STEPS,
    image_digest,
    immutable_image_reference,
    load_manifest,
    rollback_drill_record,
    rollback_drill_rejects_down_migrations,
    rollback_drill_restore_requires_approval,
    rollback_drill_post_rollback_checks,
    rollback_drill_contract,
)


def _valid_image(digit: str) -> str:
    return "registry.example/insight-unified@sha256:" + digit * 64


class RollbackDrillRecordTests(unittest.TestCase):
    def test_record_captures_current_digest_and_backups_for_every_module(self):
        manifest = load_manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("verify_unified_deployment.shutil.which", return_value=None):
                record = rollback_drill_record(_valid_image("a"), root, manifest=manifest)
            self.assertEqual(_valid_image("a"), record["currentImage"])
            self.assertEqual(image_digest(_valid_image("a")), record["currentDigest"])
            self.assertIn("recordedAt", record)
            module_ids = {entry["moduleId"] for entry in record["moduleBackups"]}
            self.assertEqual(module_ids, {module["moduleId"] for module in manifest["modules"]})
            for entry in record["moduleBackups"]:
                self.assertTrue(str(entry["backupPath"]).endswith(".sqlite3"), f"{entry['moduleId']} backup path must end with .sqlite3")
                self.assertEqual(entry["owner"], entry["moduleId"])
                self.assertTrue(entry["verified"])

    def test_record_rejects_non_immutable_image_references(self):
        with self.assertRaises(ValueError):
            rollback_drill_record("insight-unified:latest", Path(tempfile.mkdtemp()))


class RollbackDrillMigrationPolicyTests(unittest.TestCase):
    def test_forward_only_policy_is_declared_without_down_migrations(self):
        self.assertEqual(
            list(ROLLBACK_DRILL_STEPS),
            ["record_digest_and_backups", "apply_forward_only_migrations",
             "rollback_image_without_down_migrations",
             "restore_data_only_via_approved_decision",
             "rerun_post_rollback_checks"],
        )

    def test_partial_or_drifted_schema_is_rejected_without_down_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # A drifted schema_migrations table must not produce a down-migration
            # plan; the helper returns the rejected drift marker only.
            database = root / "schema.db"
            with closing(sqlite3.connect(database)) as connection:
                connection.execute("CREATE TABLE schema_migrations (version TEXT PRIMARY KEY)")
                connection.execute("INSERT INTO schema_migrations(version) VALUES ('0002_extra.sql')")
                connection.execute("INSERT INTO schema_migrations(version) VALUES ('0003_unexpected.sql')")
                connection.commit()
            decision = rollback_drill_rejects_down_migrations(database, latest_recorded_version="0002_extra.sql")
            self.assertFalse(decision["downMigrationPlanned"])
            self.assertTrue(decision["driftDetected"])
            self.assertIn("0003_unexpected.sql", decision["unexpectedVersions"])


class RollbackDrillRestoreApprovalTests(unittest.TestCase):
    def test_restore_without_approved_decision_is_blocked(self):
        with self.assertRaises(RuntimeError) as context:
            rollback_drill_restore_requires_approval(approved=False, approver=None)
        self.assertIn("separately approved recovery decision", str(context.exception))

    def test_restore_requires_named_approver(self):
        with self.assertRaises(RuntimeError):
            rollback_drill_restore_requires_approval(approved=True, approver="   ")
        rollback_drill_restore_requires_approval(approved=True, approver="on-call-sre")

    def test_fabricated_clinical_approvals_are_rejected(self):
        # No clinical decision may be fabricated; the drill only accepts an
        # operator (non-clinical) recovery decision and never threads a clinical
        # threshold through this surface.
        with self.assertRaises(ValueError):
            rollback_drill_restore_requires_approval(
                approved=True, approver="on-call-sre", clinicalThreshold="HARD_CODED"
            )


class RollbackDrillPostRollbackChecksTests(unittest.TestCase):
    def test_post_rollback_checklist_covers_readiness_routes_tls_recovery_integrity(self):
        checks = rollback_drill_post_rollback_checks()
        self.assertEqual(
            ["readiness", "unified_routing", "tls", "recovery", "integrity"],
            checks,
        )


class RollbackDrillContractTests(unittest.TestCase):
    def test_rollback_drill_contract_offline_runs_every_step_and_records_audit_trail(self):
        manifest = load_manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("verify_unified_deployment.shutil.which", return_value=None):
                audit = rollback_drill_contract(
                    _valid_image("b"),
                    root,
                    approver="on-call-sre",
                    manifest=manifest,
                )
        self.assertEqual(list(ROLLBACK_DRILL_STEPS), list(audit["steps"].keys()))
        for step in ROLLBACK_DRILL_STEPS:
            self.assertEqual("pass", audit["steps"][step]["status"], step)
        self.assertEqual(_valid_image("b"), audit["record"]["currentImage"])
        self.assertEqual("on-call-sre", audit["restore"]["approver"])
        self.assertFalse(audit["migration"]["downMigrationPlanned"])
        self.assertEqual(
            ["readiness", "unified_routing", "tls", "recovery", "integrity"],
            audit["postRollback"]["checks"],
        )

    def test_audit_trail_rejects_approval_free_restore(self):
        manifest = load_manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("verify_unified_deployment.shutil.which", return_value=None):
                with self.assertRaises(RuntimeError):
                    rollback_drill_contract(
                        _valid_image("c"),
                        root,
                        approver="",
                        manifest=manifest,
                    )


if __name__ == "__main__":
    unittest.main()
