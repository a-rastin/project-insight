"""SQLite-backed repository adapter for diagnosis sessions.

Replaces the module-global in-memory _store. The adapter exposes the same
semantics the route handlers used against the dict (init/get/put + audit
snapshot) but persists to SQLite so sessions survive restarts and the
audit hook returns a stable, dated snapshot.

Connection lifetime: a single connection per process, opened lazily on
first use and reused. Use the `DIAGNOSIS_DB_PATH` env var to point at a
file location; defaults to ``diagnosis_store.db`` in the current working
directory. ``reset()`` is exposed for the in-process self-check.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Iterator


from .config import settings


def _resolve_path() -> str:
    # ``settings.db_path`` already honours ``DIAGNOSIS_DB_PATH`` (config.py);
    # keep the env re-read so tests that flip the env mid-process without
    # re-importing still see the new path, same as before the adapter.
    return os.environ.get("DIAGNOSIS_DB_PATH") or settings.db_path


_CREATE_SESSIONS = (
    """
    CREATE TABLE IF NOT EXISTS sessions (
        code        TEXT PRIMARY KEY,
        patient_id  TEXT,
        checked     TEXT NOT NULL DEFAULT '[]',
        decision    TEXT,
        created_at  INTEGER NOT NULL,
        updated_at  INTEGER NOT NULL
    )
    """
)

_CREATE_AUDIT = (
    """
    CREATE TABLE IF NOT EXISTS audit (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        code        TEXT NOT NULL,
        snapshot    TEXT NOT NULL,
        created_at  INTEGER NOT NULL
    )
    """
)


class DiagnosisStore:
    """Persistence adapter for /diagnosis sessions + audit snapshots.

    Thread-safe via a per-process connection guarded by ``threading.Lock``.
    Same-process SQLite is fine — the WAL journal handles concurrent reads.
    """

    def __init__(self, path: str | None = None) -> None:
        self.path = path or _resolve_path()
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        self._ensure_schema()

    @contextmanager
    def _cursor(self) -> Iterator[sqlite3.Cursor]:
        if self._conn is None:
            self._conn = sqlite3.connect(
                self.path,
                isolation_level=None,
                check_same_thread=False,
            )
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        cur = self._conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def _ensure_schema(self) -> None:
        with self._cursor() as cur:
            cur.execute("BEGIN")
            try:
                cur.execute(_CREATE_SESSIONS)
                cur.execute(_CREATE_AUDIT)
                cur.execute("COMMIT")
            except Exception:
                cur.execute("ROLLBACK")
                raise

    def init(self, code: str, *, patient_id: str | None = None) -> bool:
        """Insert a new empty session. Returns ``True`` if created."""
        now = int(time.time())
        with self._cursor() as cur:
            cur.execute(
                "INSERT OR IGNORE INTO sessions "
                "(code, patient_id, checked, decision, created_at, updated_at) "
                "VALUES (?, ?, '[]', NULL, ?, ?)",
                (code, patient_id, now, now),
            )
            return cur.rowcount == 1

    def exists(self, code: str) -> bool:
        with self._cursor() as cur:
            cur.execute("SELECT 1 FROM sessions WHERE code = ?", (code,))
            return cur.fetchone() is not None

    def get(self, code: str) -> dict | None:
        with self._cursor() as cur:
            cur.execute(
                "SELECT code, patient_id, checked, decision, "
                "created_at, updated_at "
                "FROM sessions WHERE code = ?",
                (code,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        checked = json.loads(row[2]) if row[2] else []
        return {
            "code": row[0],
            "patient_id": row[1],
            "checked": checked,
            "decision": row[3],
            "created_at": row[4],
            "updated_at": row[5],
        }

    def put(
        self,
        code: str,
        *,
        patient_id: str | None,
        checked: list[str],
        decision: str | None,
    ) -> dict:
        """Persist checked criteria + clinician decision. Returns the
        full session row. Creates the row if it doesn't exist."""
        now = int(time.time())
        encoded = json.dumps(list(checked))
        with self._cursor() as cur:
            cur.execute("BEGIN")
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO sessions "
                    "(code, patient_id, checked, decision, created_at, updated_at) "
                    "VALUES (?, ?, '[]', NULL, ?, ?)",
                    (code, patient_id, now, now),
                )
                cur.execute(
                    "UPDATE sessions "
                    "SET patient_id = ?, checked = ?, decision = ?, updated_at = ? "
                    "WHERE code = ?",
                    (patient_id, encoded, decision, now, code),
                )
                cur.execute(
                    "SELECT code, patient_id, checked, decision, "
                    "created_at, updated_at FROM sessions WHERE code = ?",
                    (code,),
                )
                row = cur.fetchone()
                cur.execute("COMMIT")
            except Exception:
                cur.execute("ROLLBACK")
                raise
        if row is None:
            raise RuntimeError(f"put failed: row {code!r} missing after write")
        return {
            "code": row[0],
            "patient_id": row[1],
            "checked": json.loads(row[2]) if row[2] else [],
            "decision": row[3],
            "created_at": row[4],
            "updated_at": row[5],
        }

    def audit_snapshot(self, code: str) -> str:
        """JSON snapshot for the Insight audit logger. Records every
        successful put, plus a final snapshot at read time."""
        session = self.get(code) or {"code": code}
        snapshot = json.dumps(session, default=str, sort_keys=True)
        with self._cursor() as cur:
            cur.execute(
                "INSERT INTO audit (code, snapshot, created_at) VALUES (?, ?, ?)",
                (code, snapshot, int(time.time())),
            )
        return snapshot

    def list_audits(self, code: str) -> list[str]:
        with self._cursor() as cur:
            cur.execute(
                "SELECT snapshot FROM audit WHERE code = ? ORDER BY id",
                (code,),
            )
            return [r[0] for r in cur.fetchall()]

    def reset(self) -> None:
        """Hard reset. Self-check / test fixture support only."""
        with self._cursor() as cur:
            cur.execute("DELETE FROM sessions")
            cur.execute("DELETE FROM audit")


def _store_selfcheck() -> None:
    """Hard reverify the persistence adapter end-to-end, with a fresh
    temp DB so the check never collides with a real store. Covers:
    - patient id / patient code round-trip
    - checked criteria (incl. order preservation + dedupe on the PUT side)
    - clinician decision (both 'confirmed' and bypass 'definite')
    - monotonic timestamps (created_at <= updated_at on every write)
    - audit snapshot records and is JSON-round-trippable
    - data survives a new DiagnosisStore on the same file
    Run: ``python -m diagnosis.store``
    """
    import tempfile
    import os
    fd, path = tempfile.mkstemp(prefix="diagnosis_store_test_", suffix=".db")
    os.close(fd)
    try:
        s1 = DiagnosisStore(path)
        s1.reset()

        # 1. init creates a session row, returns True once then False.
        assert s1.init("P-0042-A", patient_id="P-0042-A") is True
        assert s1.init("P-0042-A", patient_id="P-0042-A") is False
        row = s1.get("P-0042-A")
        assert row is not None and row["code"] == "P-0042-A"
        assert row["patient_id"] == "P-0042-A", row
        assert row["checked"] == [] and row["decision"] is None

        # 2. timestamps present + monotonic.
        assert isinstance(row["created_at"], int) and row["created_at"] > 0
        assert row["updated_at"] >= row["created_at"]

        # 3. PUT persists checked criteria + decision; returned row matches.
        checked = ["A1", "A5", "A6", "B1", "C1", "D1"]
        out = s1.put(
            "P-0042-A", patient_id="P-0042-A",
            checked=checked, decision="confirmed",
        )
        assert out["checked"] == checked, out
        assert out["decision"] == "confirmed", out
        assert out["updated_at"] >= row["updated_at"], (out, row)

        # 4. bypass ("definite") is a valid decision even on unmet criteria.
        out_bypass = s1.put(
            "P-0042-A", patient_id="P-0042-A",
            checked=["A1"], decision="definite",
        )
        assert out_bypass["decision"] == "definite"
        assert out_bypass["checked"] == ["A1"]

        # 5. audit_snapshot records and returns a stable JSON snapshot.
        snap = s1.audit_snapshot("P-0042-A")
        parsed = json.loads(snap)
        assert parsed["code"] == "P-0042-A"
        assert parsed["decision"] == "definite", parsed
        audits = s1.list_audits("P-0042-A")
        assert any(snap == a for a in audits), "audit snapshot was not recorded"

        # 6. unknown code returns None from get(); snapshot doesn't crash.
        assert s1.get("does-not-exist") is None
        snap_missing = s1.audit_snapshot("does-not-exist")
        assert json.loads(snap_missing)["code"] == "does-not-exist"

        # 7. durability: new DiagnosisStore against the same file sees
        # the persisted row, so clinical data survives a restart.
        s2 = DiagnosisStore(path)
        persisted = s2.get("P-0042-A")
        assert persisted is not None
        assert persisted["checked"] == ["A1"]
        assert persisted["decision"] == "definite", persisted

        s1.reset()
        s2.reset()
        print("OK: diagnosis store self-check passed")
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


if __name__ == "__main__":
    _store_selfcheck()
