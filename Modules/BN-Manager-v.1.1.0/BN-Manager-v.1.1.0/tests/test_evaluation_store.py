from __future__ import annotations

import tempfile
import unittest
import uuid
from pathlib import Path

from bn_manager_backend.evaluation_store import (
    ENGINE_VERSION,
    EVALUATION_SCHEMA_VERSION,
    CanonicalEvaluationRecord,
    EvaluationStore,
    IdempotencyConflict,
    InMemoryEvaluationStore,
    SqliteEvaluationStore,
    build_canonical_evaluation,
    partition_evidence,
)


def _sample_record(
    *,
    evaluation_id: str | None = None,
    idempotency_key: str = "idemp-key-01234567",
    binding_hash: str = "sha256:" + ("a" * 64),
    posterior: dict[str, float] | None = None,
) -> CanonicalEvaluationRecord:
    return CanonicalEvaluationRecord(
        evaluation_id=evaluation_id or str(uuid.uuid4()),
        evaluated_at="2026-07-23T09:00:00Z",
        model_id="bnm.pharmacotherapy",
        model_version="1.0.0",
        model_hash="sha256:" + ("b" * 64),
        schema_version=EVALUATION_SCHEMA_VERSION,
        accepted_evidence={"MedicationAdherence": "Good"},
        ignored_evidence={"NotANode": "x"},
        target="management_recommendation",
        posterior=posterior or {"option_a": 0.6, "option_b": 0.4},
        warnings=({"severity": "warning", "code": "soft", "message": "note"},),
        engine_version=ENGINE_VERSION,
        caller={"subject": "psych-1", "surface": "Dashboard"},
        request_metadata={"request_id": "req-1", "decision_id": "pharmacotherapy"},
        idempotency_key=idempotency_key,
        binding_hash=binding_hash,
    )


class PartitionEvidenceTests(unittest.TestCase):
    def test_known_nodes_are_accepted_unknown_are_ignored(self) -> None:
        allowed = {
            "MedicationAdherence": frozenset({"Good", "Partial", "Poor"}),
            "MetabolicRisk": frozenset({"Low", "Moderate", "High"}),
        }
        accepted, ignored = partition_evidence(
            {
                "MedicationAdherence": "Good",
                "UnknownNode": "Yes",
                "MetabolicRisk": "Impossible",
            },
            allowed,
        )
        self.assertEqual(accepted, {"MedicationAdherence": "Good"})
        self.assertEqual(
            ignored,
            {
                "UnknownNode": "Yes",
                "MetabolicRisk": "Impossible",
            },
        )


class BuildCanonicalEvaluationTests(unittest.TestCase):
    def test_record_carries_required_provenance_fields(self) -> None:
        allowed = {"MedicationAdherence": frozenset({"Good", "Partial", "Poor"})}
        record = build_canonical_evaluation(
            model_id="bnm.pharmacotherapy",
            model_version="1.0.0",
            model_hash="sha256:" + ("c" * 64),
            target="management_recommendation",
            posterior={"a": 1.0},
            supplied_evidence={"MedicationAdherence": "Good", "Extra": "1"},
            allowed_evidence=allowed,
            warnings=[{"severity": "info", "message": "ok"}],
            caller={"subject": "admin-1", "surface": "Follow-up"},
            request_metadata={"request_id": "r-9"},
            idempotency_key="idemp-abcdefghijklmnopqrst",
            evaluated_at="2026-07-23T10:00:00Z",
            evaluation_id="11111111-1111-1111-1111-111111111111",
        )
        self.assertEqual(record.evaluation_id, "11111111-1111-1111-1111-111111111111")
        self.assertEqual(record.evaluated_at, "2026-07-23T10:00:00Z")
        self.assertEqual(record.model_id, "bnm.pharmacotherapy")
        self.assertEqual(record.model_version, "1.0.0")
        self.assertRegex(record.model_hash, r"^sha256:[a-f0-9]{64}$")
        self.assertEqual(record.schema_version, EVALUATION_SCHEMA_VERSION)
        self.assertEqual(record.accepted_evidence, {"MedicationAdherence": "Good"})
        self.assertEqual(record.ignored_evidence, {"Extra": "1"})
        self.assertEqual(record.target, "management_recommendation")
        self.assertEqual(record.posterior, {"a": 1.0})
        self.assertEqual(record.engine_version, ENGINE_VERSION)
        self.assertEqual(record.caller["subject"], "admin-1")
        self.assertEqual(record.request_metadata["request_id"], "r-9")
        self.assertEqual(record.idempotency_key, "idemp-abcdefghijklmnopqrst")
        self.assertRegex(record.binding_hash, r"^sha256:[a-f0-9]{64}$")
        payload = record.to_dict()
        for key in (
            "evaluationId",
            "evaluatedAt",
            "modelId",
            "modelVersion",
            "modelHash",
            "schemaVersion",
            "acceptedEvidence",
            "ignoredEvidence",
            "target",
            "posterior",
            "warnings",
            "engineVersion",
            "caller",
            "requestMetadata",
            "idempotencyKey",
            "bindingHash",
        ):
            self.assertIn(key, payload)


class StoreContractMixin:
    store: EvaluationStore

    def test_put_get_round_trip(self) -> None:
        record = _sample_record()
        stored = self.store.put(record)
        self.assertEqual(stored.evaluation_id, record.evaluation_id)
        loaded = self.store.get(record.evaluation_id)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.to_dict(), record.to_dict())

    def test_identical_idempotent_retry_returns_same_record(self) -> None:
        first = _sample_record()
        self.store.put(first)
        second = _sample_record(
            evaluation_id=str(uuid.uuid4()),
            idempotency_key=first.idempotency_key,
            binding_hash=first.binding_hash,
            posterior=dict(first.posterior),
        )
        # Same binding content (hash) even if evaluation_id would differ before put:
        same_binding = CanonicalEvaluationRecord(
            evaluation_id=second.evaluation_id,
            evaluated_at=first.evaluated_at,
            model_id=first.model_id,
            model_version=first.model_version,
            model_hash=first.model_hash,
            schema_version=first.schema_version,
            accepted_evidence=dict(first.accepted_evidence),
            ignored_evidence=dict(first.ignored_evidence),
            target=first.target,
            posterior=dict(first.posterior),
            warnings=first.warnings,
            engine_version=first.engine_version,
            caller=dict(first.caller),
            request_metadata=dict(first.request_metadata),
            idempotency_key=first.idempotency_key,
            binding_hash=first.binding_hash,
        )
        again = self.store.put(same_binding)
        self.assertEqual(again.evaluation_id, first.evaluation_id)
        self.assertEqual(again.binding_hash, first.binding_hash)

    def test_conflicting_payload_for_same_key_raises(self) -> None:
        first = _sample_record()
        self.store.put(first)
        conflict = _sample_record(
            evaluation_id=str(uuid.uuid4()),
            idempotency_key=first.idempotency_key,
            binding_hash="sha256:" + ("d" * 64),
            posterior={"option_a": 0.1, "option_b": 0.9},
        )
        with self.assertRaises(IdempotencyConflict):
            self.store.put(conflict)

    def test_get_by_idempotency_key(self) -> None:
        record = _sample_record(idempotency_key="idemp-lookup-key-0001")
        self.store.put(record)
        found = self.store.get_by_idempotency_key(record.idempotency_key)
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.evaluation_id, record.evaluation_id)


class InMemoryEvaluationStoreTests(StoreContractMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryEvaluationStore()


class SqliteEvaluationStoreTests(StoreContractMixin, unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        path = Path(self._tmp.name) / "evaluations.sqlite3"
        self.store = SqliteEvaluationStore(path)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_survives_reopen(self) -> None:
        path = Path(self._tmp.name) / "persist.sqlite3"
        first_store = SqliteEvaluationStore(path)
        record = _sample_record()
        first_store.put(record)
        second_store = SqliteEvaluationStore(path)
        loaded = second_store.get(record.evaluation_id)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.to_dict(), record.to_dict())


if __name__ == "__main__":
    unittest.main()
