from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from bn_manager_backend.model_governance import (
    DEFAULT_KEY_ID,
    LIMITATIONS,
    LIMITATIONS_WORDING,
    MissingGovernanceKey,
    ModelGovernanceStore,
    SignedApproval,
    SqliteGovernanceStore,
    InMemoryGovernanceStore,
    ClinicalStatus,
    verify_approval,
    sign_approval,
)
from bn_manager_backend.model_registry import ModelRegistryEntry


SECRET_KEY = b"test-governance-key-0123456789abcdef"


def _approved_entry() -> ModelRegistryEntry:
    return ModelRegistryEntry(
        stable_id="bnm.pharmacotherapy",
        title="Pharmacotherapy",
        file_path="xml/BN-Pharmacotherapy.xml",
        target_node="management_recommendation",
        active_version="1.0.0",
        status="active",
        limitations=("compact-neutral-cpt-broadcast",),
    )


def _make_approval(
    *,
    stable_id: str = "bnm.pharmacotherapy",
    status: ClinicalStatus = ClinicalStatus.APPROVED,
    model_hash: str = "sha256:" + "a" * 64,
    approved_at: str = "2026-07-23T12:00:00Z",
    approved_by: str = "psych-1",
    secret_key: bytes = SECRET_KEY,
    key_id: str = DEFAULT_KEY_ID,
) -> SignedApproval:
    signature = sign_approval(
        stable_id=stable_id,
        status=status,
        model_hash=model_hash,
        approved_at=approved_at,
        approved_by=approved_by,
        secret_key=secret_key,
    )
    return SignedApproval(
        stable_id=stable_id,
        status=status,
        model_hash=model_hash,
        approved_at=approved_at,
        approved_by=approved_by,
        signature=signature,
        key_id=key_id,
    )


class ClinicalStatusTests(unittest.TestCase):
    def test_status_enum_carries_the_three_required_values(self) -> None:
        self.assertEqual(
            {status.value for status in ClinicalStatus},
            {"unvalidated", "approved", "retired"},
        )

    def test_algorithm_does_not_conflate_approved_with_retired_or_unvalidated(self) -> None:
        self.assertNotEqual(ClinicalStatus.APPROVED, ClinicalStatus.RETIRED)
        self.assertNotEqual(ClinicalStatus.APPROVED, ClinicalStatus.UNVALIDATED)
        self.assertNotEqual(ClinicalStatus.RETIRED, ClinicalStatus.UNVALIDATED)


class SigningTests(unittest.TestCase):
    def test_signature_is_deterministic_for_same_payload_and_key(self) -> None:
        first = sign_approval(
            stable_id="bnm.pharmacotherapy",
            status=ClinicalStatus.APPROVED,
            model_hash="sha256:" + "a" * 64,
            approved_at="2026-07-23T12:00:00Z",
            approved_by="psych-1",
            secret_key=SECRET_KEY,
        )
        second = sign_approval(
            stable_id="bnm.pharmacotherapy",
            status=ClinicalStatus.APPROVED,
            model_hash="sha256:" + "a" * 64,
            approved_at="2026-07-23T12:00:00Z",
            approved_by="psych-1",
            secret_key=SECRET_KEY,
        )
        self.assertEqual(first, second)
        self.assertNotEqual(first, "")
        # base64url alphabet only.
        self.assertRegex(first, r"^[A-Za-z0-9_-]+$")

    def test_signature_changes_with_key_or_payload(self) -> None:
        base_kwargs = dict(
            stable_id="bnm.pharmacotherapy",
            status=ClinicalStatus.APPROVED,
            model_hash="sha256:" + "a" * 64,
            approved_at="2026-07-23T12:00:00Z",
            approved_by="psych-1",
        )
        a = sign_approval(secret_key=SECRET_KEY, **base_kwargs)
        b = sign_approval(secret_key=b"different-governance-key-00000001", **base_kwargs)
        self.assertNotEqual(a, b)

        c = sign_approval(
            secret_key=SECRET_KEY,
            **{**base_kwargs, "approved_by": "psych-2"},
        )
        self.assertNotEqual(a, c)

        d = sign_approval(
            secret_key=SECRET_KEY,
            **{**base_kwargs, "status": ClinicalStatus.RETIRED},
        )
        self.assertNotEqual(a, d)

    def test_verify_accepts_valid_signature_and_rejects_tamper(self) -> None:
        approval = _make_approval()
        self.assertTrue(verify_approval(approval, SECRET_KEY))

        tampered = SignedApproval(
            stable_id=approval.stable_id,
            status=approval.status,
            model_hash="sha256:" + "b" * 64,
            approved_at=approval.approved_at,
            approved_by=approval.approved_by,
            signature=approval.signature,
            key_id=approval.key_id,
        )
        self.assertFalse(verify_approval(tampered, SECRET_KEY))
        self.assertFalse(verify_approval(approval, b"wrong-key-0000000000000000"))

    def test_empty_key_raises_missing_governance_key(self) -> None:
        with self.assertRaises(MissingGovernanceKey):
            sign_approval(
                stable_id="bnm.pharmacotherapy",
                status=ClinicalStatus.APPROVED,
                model_hash="sha256:" + "a" * 64,
                approved_at="2026-07-23T12:00:00Z",
                approved_by="psych-1",
                secret_key=b"",
            )


class LimitationsTests(unittest.TestCase):
    def test_compact_neutral_cpt_broadcast_is_declared(self) -> None:
        self.assertIn("compact-neutral-cpt-broadcast", LIMITATIONS)
        self.assertIn("compact", LIMITATIONS_WORDING.lower())

    def test_signing_key_id_default_is_stable_string(self) -> None:
        self.assertIsInstance(DEFAULT_KEY_ID, str)
        self.assertTrue(DEFAULT_KEY_ID.strip())


class StoreContractMixin:
    store: ModelGovernanceStore

    def test_put_get_round_trip(self) -> None:
        approval = _make_approval()
        self.store.put(approval)
        loaded = self.store.get(approval.stable_id)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.stable_id, approval.stable_id)
        self.assertEqual(loaded.status, ClinicalStatus.APPROVED)
        self.assertEqual(loaded.signature, approval.signature)
        self.assertEqual(loaded.key_id, approval.key_id)

    def test_put_is_idempotent_for_same_payload(self) -> None:
        approval = _make_approval()
        self.store.put(approval)
        self.store.put(approval)  # no raise
        loaded = self.store.get(approval.stable_id)
        assert loaded is not None
        self.assertEqual(loaded.signature, approval.signature)

    def test_put_replaces_when_payload_changes_for_same_stable_id(self) -> None:
        first = _make_approval(approved_by="psych-1")
        self.store.put(first)
        # A second signature for the same model id (e.g. re-approval) overwrites.
        second = _make_approval(approved_by="psych-2")
        self.store.put(second)
        loaded = self.store.get(first.stable_id)
        assert loaded is not None
        self.assertEqual(loaded.approved_by, "psych-2")

    def test_list_returns_all_approvals(self) -> None:
        a = _make_approval(stable_id="bnm.pharmacotherapy")
        b = _make_approval(stable_id="bnm.treatment-setting")
        self.store.put(a)
        self.store.put(b)
        listed = self.store.list()
        self.assertEqual({item.stable_id for item in listed}, {a.stable_id, b.stable_id})

    def test_get_for_unknown_stable_id_returns_none(self) -> None:
        self.assertIsNone(self.store.get("bnm.never-approved"))


class InMemoryStoreTests(StoreContractMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryGovernanceStore()


class SqliteStoreTests(StoreContractMixin, unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        path = Path(self._tmp.name) / "governance.sqlite3"
        self.store = SqliteGovernanceStore(path)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_survives_reopen(self) -> None:
        path = Path(self._tmp.name) / "persist.sqlite3"
        first = SqliteGovernanceStore(path)
        approval = _make_approval()
        first.put(approval)
        second = SqliteGovernanceStore(path)
        loaded = second.get(approval.stable_id)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.signature, approval.signature)


class RegistryEntryCarriesClinicalStateTests(unittest.TestCase):
    def test_default_clinical_status_is_unvalidated(self) -> None:
        entry = _approved_entry()
        self.assertEqual(entry.clinical_status, ClinicalStatus.UNVALIDATED)

    def test_limitations_field_exists_and_accepts_broadcast_marker(self) -> None:
        entry = _approved_entry()
        self.assertIn("compact-neutral-cpt-broadcast", entry.limitations)


if __name__ == "__main__":
    unittest.main()
