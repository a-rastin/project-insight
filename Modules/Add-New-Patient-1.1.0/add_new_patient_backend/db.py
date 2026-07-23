from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator, Protocol
from uuid import uuid4

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
  id TEXT PRIMARY KEY,
  patient_code TEXT NOT NULL UNIQUE,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  sex TEXT NOT NULL CHECK (sex IN ('Male', 'Female')),
  dob TEXT NOT NULL,
  phone_number TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_by_user_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS patient_intake_records (
  id TEXT PRIMARY KEY,
  patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  encounter_date TEXT NOT NULL,
  presenting_complaint TEXT NOT NULL DEFAULT '',
  provisional_diagnosis TEXT NOT NULL DEFAULT '',
  treatment_history TEXT NOT NULL DEFAULT '[]',
  allergies_snapshot TEXT NOT NULL DEFAULT '[]',
  current_medications_snapshot TEXT NOT NULL DEFAULT '[]',
  suicidality TEXT NOT NULL DEFAULT 'suicidality_none' CHECK (suicidality IN ('suicidality_none', 'ideation', 'plan', 'attempt')),
  substance_use INTEGER NOT NULL DEFAULT 0 CHECK (substance_use IN (0, 1)),
  created_by_user_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_patient_intake_records_patient_id
  ON patient_intake_records(patient_id);

CREATE TABLE IF NOT EXISTS idempotency_records (
  scope TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  status_code INTEGER NOT NULL,
  response_body TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (scope, idempotency_key)
);
"""

PATIENT_IDENTITY_COLUMNS = {
    "id",
    "patient_code",
    "first_name",
    "last_name",
    "sex",
    "dob",
    "phone_number",
    "status",
    "created_by_user_id",
    "created_at",
    "updated_at",
}

LEGACY_INTAKE_COLUMNS = {
    "presenting_complaint",
    "provisional_diagnosis",
    "treatment_history",
    "allergies",
    "current_medications",
    "suicidality",
    "substance_use",
}

PATIENT_TABLE_SQL = """
CREATE TABLE patients (
  id TEXT PRIMARY KEY,
  patient_code TEXT NOT NULL UNIQUE,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  sex TEXT NOT NULL CHECK (sex IN ('Male', 'Female')),
  dob TEXT NOT NULL,
  phone_number TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_by_user_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
"""

INTAKE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS patient_intake_records (
  id TEXT PRIMARY KEY,
  patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  encounter_date TEXT NOT NULL,
  presenting_complaint TEXT NOT NULL DEFAULT '',
  provisional_diagnosis TEXT NOT NULL DEFAULT '',
  treatment_history TEXT NOT NULL DEFAULT '[]',
  allergies_snapshot TEXT NOT NULL DEFAULT '[]',
  current_medications_snapshot TEXT NOT NULL DEFAULT '[]',
  suicidality TEXT NOT NULL DEFAULT 'suicidality_none' CHECK (suicidality IN ('suicidality_none', 'ideation', 'plan', 'attempt')),
  substance_use INTEGER NOT NULL DEFAULT 0 CHECK (substance_use IN (0, 1)),
  created_by_user_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
"""


class DatabaseAdapter(Protocol):
    @contextmanager
    def connect(self) -> Iterator[Any]:
        ...

    def initialize(self) -> None:
        ...

    def ping(self) -> bool:
        ...


class SQLiteAdapter:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            existing_tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()}
            if "patients" in existing_tables:
                migrate_patients_to_identity_table(conn)
            conn.executescript(SCHEMA)

    def ping(self) -> bool:
        with self.connect() as conn:
            conn.execute("SELECT 1").fetchone()
        return True


def now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def migrate_patients_to_identity_table(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(patients)").fetchall()}
    if PATIENT_IDENTITY_COLUMNS.issubset(columns) and not (columns & LEGACY_INTAKE_COLUMNS) and "age" not in columns and "status" in columns:
        return

    rows = conn.execute("SELECT * FROM patients ORDER BY created_at ASC").fetchall()
    conn.execute("ALTER TABLE patients RENAME TO patients_legacy")
    conn.execute(PATIENT_TABLE_SQL)
    conn.execute(INTAKE_TABLE_SQL)

    for row in rows:
        row_keys = set(row.keys())
        created_at = row["created_at"] if "created_at" in row_keys else now_iso()
        updated_at = row["updated_at"] if "updated_at" in row_keys else created_at
        created_by_user_id = row["created_by_user_id"] if "created_by_user_id" in row_keys else "unknown"
        if "dob" not in row_keys:
            continue
        conn.execute(
            """
            INSERT INTO patients
              (id, patient_code, first_name, last_name, sex, dob, phone_number, status, created_by_user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["patient_code"],
                row["first_name"],
                row["last_name"],
                row["sex"],
                row["dob"],
                row["phone_number"] if "phone_number" in row_keys else None,
                row["status"] if "status" in row_keys else "active",
                created_by_user_id,
                created_at,
                updated_at,
            ),
        )

        if LEGACY_INTAKE_COLUMNS.issubset(row_keys):
            conn.execute(
                """
                INSERT INTO patient_intake_records
                  (
                    id, patient_id, encounter_date, presenting_complaint, provisional_diagnosis,
                    treatment_history, allergies_snapshot, current_medications_snapshot,
                    suicidality, substance_use, created_by_user_id, created_at, updated_at
                  )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    row["id"],
                    created_at,
                    row["presenting_complaint"],
                    row["provisional_diagnosis"],
                    row["treatment_history"],
                    row["allergies"],
                    row["current_medications"],
                    row["suicidality"],
                    row["substance_use"],
                    created_by_user_id,
                    created_at,
                    updated_at,
                ),
            )

    conn.execute("DROP TABLE patients_legacy")
