"""Owned evaluation store: canonical provenance records with idempotent put.

BN-02 requires each evaluation to capture identity/time, model identity (id,
version, hash), schema version, accepted/ignored evidence, target, posterior,
warnings, deterministic engine version, caller, request metadata, and an
idempotency binding. Squared retries with the same key and binding return the
original record; a different binding under the same key is a conflict.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Protocol

from clinical_graph_models.contract import CONTRACT_VERSION

EVALUATION_SCHEMA_VERSION = "1.0.0"
ENGINE_VERSION = f"clinical_graph_models/{CONTRACT_VERSION}"

_CREATE_EVALUATIONS = """
CREATE TABLE IF NOT EXISTS evaluations (
    evaluation_id     TEXT PRIMARY KEY,
    evaluated_at      TEXT NOT NULL,
    model_id          TEXT NOT NULL,
    model_version     TEXT NOT NULL,
    model_hash        TEXT NOT NULL,
    schema_version    TEXT NOT NULL,
    accepted_evidence TEXT NOT NULL,
    ignored_evidence  TEXT NOT NULL,
    target            TEXT NOT NULL,
    posterior         TEXT NOT NULL,
    warnings          TEXT NOT NULL,
    engine_version    TEXT NOT NULL,
    caller            TEXT NOT NULL,
    request_metadata  TEXT NOT NULL,
    idempotency_key   TEXT NOT NULL,
    binding_hash      TEXT NOT NULL,
    record_json       TEXT NOT NULL
)
"""

_CREATE_IDEMPOTENCY_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_evaluations_idempotency_key
ON evaluations(idempotency_key)
"""


class IdempotencyConflict(ValueError):
    """Same idempotency key used with a different binding hash/payload."""


@dataclass(frozen=True, slots=True)
class CanonicalEvaluationRecord:
    evaluation_id: str
    evaluated_at: str
    model_id: str
    model_version: str
    model_hash: str
    schema_version: str
    accepted_evidence: dict[str, Any]
    ignored_evidence: dict[str, Any]
    target: str
    posterior: dict[str, float]
    warnings: tuple[Mapping[str, Any], ...]
    engine_version: str
    caller: dict[str, Any]
    request_metadata: dict[str, Any]
    idempotency_key: str
    binding_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluationId": self.evaluation_id,
            "evaluatedAt": self.evaluated_at,
            "modelId": self.model_id,
            "modelVersion": self.model_version,
            "modelHash": self.model_hash,
            "schemaVersion": self.schema_version,
            "acceptedEvidence": _jsonable(self.accepted_evidence),
            "ignoredEvidence": _jsonable(self.ignored_evidence),
            "target": self.target,
            "posterior": {str(k): float(v) for k, v in self.posterior.items()},
            "warnings": [_jsonable(item) for item in self.warnings],
            "engineVersion": self.engine_version,
            "caller": _jsonable(self.caller),
            "requestMetadata": _jsonable(self.request_metadata),
            "idempotencyKey": self.idempotency_key,
            "bindingHash": self.binding_hash,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "CanonicalEvaluationRecord":
        return cls(
            evaluation_id=str(payload["evaluationId"]),
            evaluated_at=str(payload["evaluatedAt"]),
            model_id=str(payload["modelId"]),
            model_version=str(payload["modelVersion"]),
            model_hash=str(payload["modelHash"]),
            schema_version=str(payload["schemaVersion"]),
            accepted_evidence=dict(payload.get("acceptedEvidence") or {}),
            ignored_evidence=dict(payload.get("ignoredEvidence") or {}),
            target=str(payload["target"]),
            posterior={str(k): float(v) for k, v in dict(payload.get("posterior") or {}).items()},
            warnings=tuple(dict(item) for item in (payload.get("warnings") or ())),
            engine_version=str(payload["engineVersion"]),
            caller=dict(payload.get("caller") or {}),
            request_metadata=dict(payload.get("requestMetadata") or {}),
            idempotency_key=str(payload["idempotencyKey"]),
            binding_hash=str(payload["bindingHash"]),
        )


class EvaluationStore(Protocol):
    def put(self, record: CanonicalEvaluationRecord) -> CanonicalEvaluationRecord: ...

    def get(self, evaluation_id: str) -> CanonicalEvaluationRecord | None: ...

    def get_by_idempotency_key(self, idempotency_key: str) -> CanonicalEvaluationRecord | None: ...


class InMemoryEvaluationStore:
    def __init__(self) -> None:
        self._by_id: dict[str, CanonicalEvaluationRecord] = {}
        self._by_key: dict[str, str] = {}
        self._lock = threading.Lock()

    def put(self, record: CanonicalEvaluationRecord) -> CanonicalEvaluationRecord:
        key = record.idempotency_key.strip()
        if not key:
            raise ValueError("idempotency_key is required")
        with self._lock:
            existing_id = self._by_key.get(key)
            if existing_id is not None:
                previous = self._by_id[existing_id]
                if previous.binding_hash != record.binding_hash:
                    raise IdempotencyConflict(
                        "idempotency key is already bound to a different evaluation payload"
                    )
                return previous
            stored = record
            self._by_id[stored.evaluation_id] = stored
            self._by_key[key] = stored.evaluation_id
            return stored

    def get(self, evaluation_id: str) -> CanonicalEvaluationRecord | None:
        with self._lock:
            return self._by_id.get(evaluation_id)

    def get_by_idempotency_key(self, idempotency_key: str) -> CanonicalEvaluationRecord | None:
        with self._lock:
            evaluation_id = self._by_key.get(idempotency_key.strip())
            if evaluation_id is None:
                return None
            return self._by_id.get(evaluation_id)


class SqliteEvaluationStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=5.0, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _ensure_schema(self) -> None:
        with self._lock:
            with self._connect() as connection:
                connection.execute(_CREATE_EVALUATIONS)
                connection.execute(_CREATE_IDEMPOTENCY_INDEX)
                connection.commit()

    def put(self, record: CanonicalEvaluationRecord) -> CanonicalEvaluationRecord:
        key = record.idempotency_key.strip()
        if not key:
            raise ValueError("idempotency_key is required")
        payload = record.to_dict()
        encoded = _dump(payload)
        with self._lock:
            with self._connect() as connection:
                try:
                    connection.execute("BEGIN IMMEDIATE")
                    existing = connection.execute(
                        "SELECT record_json, binding_hash FROM evaluations WHERE idempotency_key = ?",
                        (key,),
                    ).fetchone()
                    if existing is not None:
                        if existing["binding_hash"] != record.binding_hash:
                            connection.execute("ROLLBACK")
                            raise IdempotencyConflict(
                                "idempotency key is already bound to a different evaluation payload"
                            )
                        connection.execute("COMMIT")
                        return CanonicalEvaluationRecord.from_dict(json.loads(existing["record_json"]))
                    connection.execute(
                        """
                        INSERT INTO evaluations (
                            evaluation_id, evaluated_at, model_id, model_version, model_hash,
                            schema_version, accepted_evidence, ignored_evidence, target, posterior,
                            warnings, engine_version, caller, request_metadata, idempotency_key,
                            binding_hash, record_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            record.evaluation_id,
                            record.evaluated_at,
                            record.model_id,
                            record.model_version,
                            record.model_hash,
                            record.schema_version,
                            _dump(record.accepted_evidence),
                            _dump(record.ignored_evidence),
                            record.target,
                            _dump(record.posterior),
                            _dump(list(record.warnings)),
                            record.engine_version,
                            _dump(record.caller),
                            _dump(record.request_metadata),
                            key,
                            record.binding_hash,
                            encoded,
                        ),
                    )
                    connection.execute("COMMIT")
                    return record
                except IdempotencyConflict:
                    raise
                except sqlite3.IntegrityError as exc:
                    connection.execute("ROLLBACK")
                    existing = connection.execute(
                        "SELECT record_json, binding_hash FROM evaluations WHERE idempotency_key = ?",
                        (key,),
                    ).fetchone()
                    if existing is not None and existing["binding_hash"] == record.binding_hash:
                        return CanonicalEvaluationRecord.from_dict(json.loads(existing["record_json"]))
                    raise IdempotencyConflict(
                        "idempotency key is already bound to a different evaluation payload"
                    ) from exc
                except Exception:
                    connection.execute("ROLLBACK")
                    raise

    def get(self, evaluation_id: str) -> CanonicalEvaluationRecord | None:
        with self._lock:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT record_json FROM evaluations WHERE evaluation_id = ?",
                    (evaluation_id,),
                ).fetchone()
        if row is None:
            return None
        return CanonicalEvaluationRecord.from_dict(json.loads(row["record_json"]))

    def get_by_idempotency_key(self, idempotency_key: str) -> CanonicalEvaluationRecord | None:
        with self._lock:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT record_json FROM evaluations WHERE idempotency_key = ?",
                    (idempotency_key.strip(),),
                ).fetchone()
        if row is None:
            return None
        return CanonicalEvaluationRecord.from_dict(json.loads(row["record_json"]))


def partition_evidence(
    supplied: Mapping[str, Any] | None,
    allowed: Mapping[str, frozenset[str]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Split caller evidence into accepted (known node+state) vs ignored."""
    accepted: dict[str, Any] = {}
    ignored: dict[str, Any] = {}
    for node_id, value in dict(supplied or {}).items():
        states = allowed.get(node_id)
        if states is None:
            ignored[node_id] = value
            continue
        if isinstance(value, str) and value in states:
            accepted[node_id] = value
            continue
        if isinstance(value, dict):
            if all(isinstance(k, str) and k in states for k in value):
                accepted[node_id] = value
                continue
        ignored[node_id] = value
    return accepted, ignored


def compute_binding_hash(
    *,
    model_id: str,
    model_version: str,
    model_hash: str,
    target: str,
    accepted_evidence: Mapping[str, Any],
    ignored_evidence: Mapping[str, Any],
    schema_version: str,
    engine_version: str,
    caller: Mapping[str, Any],
    request_metadata: Mapping[str, Any],
) -> str:
    payload = {
        "modelId": model_id,
        "modelVersion": model_version,
        "modelHash": model_hash,
        "target": target,
        "acceptedEvidence": _jsonable(accepted_evidence),
        "ignoredEvidence": _jsonable(ignored_evidence),
        "schemaVersion": schema_version,
        "engineVersion": engine_version,
        "caller": _jsonable(caller),
        "requestMetadata": _strip_volatile_metadata(request_metadata),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()


def build_canonical_evaluation(
    *,
    model_id: str,
    model_version: str,
    model_hash: str,
    target: str,
    posterior: Mapping[str, float],
    supplied_evidence: Mapping[str, Any] | None,
    allowed_evidence: Mapping[str, frozenset[str]],
    warnings: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None,
    caller: Mapping[str, Any],
    request_metadata: Mapping[str, Any],
    idempotency_key: str,
    evaluated_at: str | None = None,
    evaluation_id: str | None = None,
    schema_version: str = EVALUATION_SCHEMA_VERSION,
    engine_version: str = ENGINE_VERSION,
) -> CanonicalEvaluationRecord:
    accepted, ignored = partition_evidence(supplied_evidence, allowed_evidence)
    evaluated_at_value = evaluated_at or _now_iso()
    warning_tuple = tuple(dict(item) for item in (warnings or ()))
    caller_dict = dict(caller)
    meta = dict(request_metadata)
    binding = compute_binding_hash(
        model_id=model_id,
        model_version=model_version,
        model_hash=model_hash,
        target=target,
        accepted_evidence=accepted,
        ignored_evidence=ignored,
        schema_version=schema_version,
        engine_version=engine_version,
        caller=caller_dict,
        request_metadata=meta,
    )
    return CanonicalEvaluationRecord(
        evaluation_id=evaluation_id or str(uuid.uuid4()),
        evaluated_at=evaluated_at_value,
        model_id=model_id,
        model_version=model_version,
        model_hash=model_hash,
        schema_version=schema_version,
        accepted_evidence=accepted,
        ignored_evidence=ignored,
        target=target,
        posterior={str(k): float(v) for k, v in posterior.items()},
        warnings=warning_tuple,
        engine_version=engine_version,
        caller=caller_dict,
        request_metadata=meta,
        idempotency_key=idempotency_key.strip(),
        binding_hash=binding,
    )


def _strip_volatile_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Drop values that correctly vary across retries of the same clinical request."""
    skip = {"request_id", "requestId", "correlation_id", "correlationId"}
    return {str(k): _jsonable(v) for k, v in metadata.items() if k not in skip}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _dump(value: Any) -> str:
    return json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, float):
        return float(value)
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return str(value)
