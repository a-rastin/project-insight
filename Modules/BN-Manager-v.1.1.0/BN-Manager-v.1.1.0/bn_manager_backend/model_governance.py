"""Clinical model governance for approved XML Bayesian Network artifacts (BN-04).

The module owned by BN Manager exposes:

* a stable :class:`ClinicalStatus` enumeration (``unvalidated`` / ``approved`` /
  ``retired``) — schema and dimensional validity never imply clinical safety;
* an HMAC-SHA256 signed :class:`SignedApproval` covering the stable id, status,
  model content hash, approval instant, and approver identity — sign and verify
  helpers refuse to operate without a configured governance key so the approve
  route fails-closed rather than silently minting an unsigned approval;
* an owned :class:`ModelGovernanceStore` protocol with in-memory and SQLite
  adapters so journalist approvals/retirements persist across restarts;
* the :func:`LIMITATIONS` declaration surfaced through evidence schemas and the
  module contract so callers cannot treat compact neutral CPT broadcasting as
  silent production behavior.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sqlite3
import threading
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol


DEFAULT_KEY_ID = "bn-manager-governance-key-v1"

# Compact one-row TABLE broadcasting across every parent-state combination is a
# deliberate authoring pattern for the supplied INSIGHT networks. The compiler
# records ``table_broadcast=True`` on the affected Potential; callers must not
# treat broadcast rows as calibrated clinical probabilities.
LIMITATIONS: tuple[str, ...] = ("compact-neutral-cpt-broadcast",)

LIMITATIONS_WORDING = (
    "Treatment Setting and Involuntary Treatment Considerations ship compact "
    "neutral conditional tables broadcast across parent combinations. These "
    "broadcast rows await clinical calibration and must not be treated as "
    "evidence-grade posterior drivers."
)

CLINICAL_SAFETY_NOT_BY_VALIDATION = (
    "Dimensional, schema, and structural validity never imply clinical safety. "
    "An approved model still requires licensed clinician review of patient "
    "context, source evidence, contraindications, and local policy before "
    "clinical action."
)


class ClinicalStatus(str, Enum):
    UNVALIDATED = "unvalidated"
    APPROVED = "approved"
    RETIRED = "retired"


class MissingGovernanceKey(ValueError):
    """Raised when a signing operation was requested without a governance key."""


class ModelNotApproved(ValueError):
    """Raised when a retire or revoke action targets an un-approved model."""


@dataclass(frozen=True, slots=True)
class SignedApproval:
    stable_id: str
    status: ClinicalStatus
    model_hash: str
    approved_at: str
    approved_by: str
    signature: str
    key_id: str = DEFAULT_KEY_ID

    def to_dict(self) -> dict[str, Any]:
        return {
            "stable_id": self.stable_id,
            "status": self.status.value,
            "model_hash": self.model_hash,
            "approved_at": self.approved_at,
            "approved_by": self.approved_by,
            "signature": self.signature,
            "key_id": self.key_id,
        }


def _canonical_payload(
    *,
    stable_id: str,
    status: ClinicalStatus,
    model_hash: str,
    approved_at: str,
    approved_by: str,
) -> bytes:
    return "\n".join(
        (
            stable_id,
            status.value,
            model_hash,
            approved_at,
            approved_by,
        )
    ).encode("utf-8")


def sign_approval(
    *,
    stable_id: str,
    status: ClinicalStatus,
    model_hash: str,
    approved_at: str,
    approved_by: str,
    secret_key: bytes,
    key_id: str = DEFAULT_KEY_ID,
) -> str:
    if not secret_key:
        raise MissingGovernanceKey("governance signing key is required to sign an approval")
    if not isinstance(status, ClinicalStatus):
        raise TypeError(f"status must be a ClinicalStatus, got {type(status)!r}")
    payload = _canonical_payload(
        stable_id=stable_id,
        status=status,
        model_hash=model_hash,
        approved_at=approved_at,
        approved_by=approved_by,
    )
    digest = hmac.new(secret_key, payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def verify_approval(approval: SignedApproval, secret_key: bytes) -> bool:
    if not secret_key:
        return False
    expected = sign_approval(
        stable_id=approval.stable_id,
        status=approval.status,
        model_hash=approval.model_hash,
        approved_at=approval.approved_at,
        approved_by=approval.approved_by,
        secret_key=secret_key,
        key_id=approval.key_id,
    )
    return hmac.compare_digest(expected, approval.signature)


class ModelGovernanceStore(Protocol):
    def get(self, stable_id: str) -> SignedApproval | None: ...

    def put(self, approval: SignedApproval) -> SignedApproval: ...

    def list(self) -> list[SignedApproval]: ...

    def delete(self, stable_id: str) -> None: ...


@dataclass
class InMemoryGovernanceStore:
    _records: dict[str, SignedApproval] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def get(self, stable_id: str) -> SignedApproval | None:
        with self._lock:
            return self._records.get(stable_id)

    def put(self, approval: SignedApproval) -> SignedApproval:
        with self._lock:
            self._records[approval.stable_id] = approval
            return approval

    def list(self) -> list[SignedApproval]:
        with self._lock:
            return [record for record in self._records.values()]

    def delete(self, stable_id: str) -> None:
        with self._lock:
            self._records.pop(stable_id, None)


_CREATE_GOVERNANCE = """
CREATE TABLE IF NOT EXISTS model_governance (
    stable_id    TEXT PRIMARY KEY,
    status       TEXT NOT NULL,
    model_hash   TEXT NOT NULL,
    approved_at  TEXT NOT NULL,
    approved_by  TEXT NOT NULL,
    signature    TEXT NOT NULL,
    key_id       TEXT NOT NULL,
    record_json  TEXT NOT NULL
)
"""


class SqliteGovernanceStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=5.0, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _ensure_schema(self) -> None:
        with self._lock:
            with self._connect() as connection:
                connection.execute(_CREATE_GOVERNANCE)
                connection.commit()

    def put(self, approval: SignedApproval) -> SignedApproval:
        encoded = json.dumps(approval.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        with self._lock:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO model_governance (
                        stable_id, status, model_hash, approved_at, approved_by,
                        signature, key_id, record_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(stable_id) DO UPDATE SET
                        status = excluded.status,
                        model_hash = excluded.model_hash,
                        approved_at = excluded.approved_at,
                        approved_by = excluded.approved_by,
                        signature = excluded.signature,
                        key_id = excluded.key_id,
                        record_json = excluded.record_json
                    """,
                    (
                        approval.stable_id,
                        approval.status.value,
                        approval.model_hash,
                        approval.approved_at,
                        approval.approved_by,
                        approval.signature,
                        approval.key_id,
                        encoded,
                    ),
                )
                connection.commit()
            return approval

    def get(self, stable_id: str) -> SignedApproval | None:
        with self._lock:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT record_json FROM model_governance WHERE stable_id = ?",
                    (stable_id,),
                ).fetchone()
        if row is None:
            return None
        return _approval_from_json(row["record_json"])

    def list(self) -> list[SignedApproval]:
        with self._lock:
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT record_json FROM model_governance ORDER BY stable_id"
                ).fetchall()
        return [_approval_from_json(row["record_json"]) for row in rows]

    def delete(self, stable_id: str) -> None:
        with self._lock:
            with self._connect() as connection:
                connection.execute(
                    "DELETE FROM model_governance WHERE stable_id = ?",
                    (stable_id,),
                )
                connection.commit()


def _approval_from_json(text: str) -> SignedApproval:
    payload = json.loads(text)
    return SignedApproval(
        stable_id=str(payload["stable_id"]),
        status=ClinicalStatus(str(payload["status"])),
        model_hash=str(payload["model_hash"]),
        approved_at=str(payload["approved_at"]),
        approved_by=str(payload["approved_by"]),
        signature=str(payload["signature"]),
        key_id=str(payload.get("key_id") or DEFAULT_KEY_ID),
    )


def clinical_status_for(
    entry_stable_id: str,
    store: ModelGovernanceStore | None,
) -> tuple[ClinicalStatus, SignedApproval | None]:
    """Return the active clinical status for a registry entry.

    The static registry entry defaults to :attr:`ClinicalStatus.UNVALIDATED`.
    A stored approval registered through the governance routes overrides the
    default when its signature verifies against the supplied governance key.
    """
    if store is None:
        return ClinicalStatus.UNVALIDATED, None
    approval = store.get(entry_stable_id)
    if approval is None:
        return ClinicalStatus.UNVALIDATED, None
    return approval.status, approval


__all__ = [
    "DEFAULT_KEY_ID",
    "LIMITATIONS",
    "LIMITATIONS_WORDING",
    "CLINICAL_SAFETY_NOT_BY_VALIDATION",
    "ClinicalStatus",
    "InMemoryGovernanceStore",
    "MissingGovernanceKey",
    "ModelGovernanceStore",
    "ModelNotApproved",
    "SignedApproval",
    "SqliteGovernanceStore",
    "clinical_status_for",
    "sign_approval",
    "verify_approval",
]
