from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator, Protocol
from uuid import UUID, uuid4

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
  resource_version INTEGER NOT NULL DEFAULT 1,
  created_by_user_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS patient_code_reservations (
  patient_code TEXT PRIMARY KEY COLLATE NOCASE,
  patient_id TEXT NOT NULL,
  reserved_at TEXT NOT NULL
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
    "resource_version",
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
  resource_version INTEGER NOT NULL DEFAULT 1,
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

    def initialize(self) -> dict[str, Any]:
        ...

    def ping(self) -> bool:
        ...


class SQLiteAdapter:
    def __init__(self, db_path: str) -> None:
        self.last_migration_report = _empty_migration_report()
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

    def initialize(self) -> dict[str, Any]:
        report = _empty_migration_report()
        with self.connect() as conn:
            existing_tables = {
                row["name"]
                for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            }
            if "patients" in existing_tables:
                report = migrate_patients_to_identity_table(conn)
            conn.executescript(SCHEMA)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS patient_migration_quarantine (
                  source_table TEXT NOT NULL,
                  record_id TEXT NOT NULL,
                  reason TEXT NOT NULL,
                  payload TEXT NOT NULL,
                  quarantined_at TEXT NOT NULL,
                  PRIMARY KEY (source_table, record_id)
                )
                """
            )
            conn.execute("DELETE FROM patient_code_reservations")
            conn.execute(
                """
                INSERT INTO patient_code_reservations
                  (patient_code, patient_id, reserved_at)
                SELECT patient_code, id, created_at FROM patients
                """
            )
        self.last_migration_report = report
        return report

    def ping(self) -> bool:
        with self.connect() as conn:
            conn.execute("SELECT 1").fetchone()
        return True


def now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _empty_migration_report() -> dict[str, Any]:
    return {
        "migratedPatientCount": 0,
        "migratedEncounterCount": 0,
        "quarantinedCount": 0,
        "collisionRecordIds": [],
        "unresolvedRecordIds": [],
    }


def _is_uuid(value: Any) -> bool:
    if value in (None, ""):
        return False
    try:
        parsed = UUID(str(value))
    except (AttributeError, TypeError, ValueError):
        return False
    return parsed.int != 0 and str(parsed) == str(value).lower()


def _row_value(row: sqlite3.Row, key: str, default: Any = None) -> Any:
    return row[key] if key in row.keys() and row[key] is not None else default


def _record_id(row: sqlite3.Row, row_number: int) -> str:
    value = _row_value(row, "id")
    return str(value) if value not in (None, "") else f"row-{row_number}"


def _patient_code(value: Any) -> str | None:
    if value in (None, ""):
        return None
    normalized = str(value).strip().upper()
    return normalized or None


def _row_payload(row: sqlite3.Row) -> str:
    return json.dumps(
        {key: row[key] for key in row.keys() if not key.startswith("_migration_")},
        default=str,
        sort_keys=True,
    )


def _schema_is_canonical(conn: sqlite3.Connection, patient_columns: set[str]) -> bool:
    if not PATIENT_IDENTITY_COLUMNS.issubset(patient_columns) or patient_columns & LEGACY_INTAKE_COLUMNS:
        return False

    patient_rows = conn.execute("SELECT id, patient_code FROM patients").fetchall()
    patient_ids = set()
    patient_codes: set[str] = set()
    for row in patient_rows:
        if not _is_uuid(row["id"]):
            return False
        code = _patient_code(row["patient_code"])
        if code is None or code in patient_codes:
            return False
        patient_ids.add(row["id"])
        patient_codes.add(code)

    intake_table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'patient_intake_records'"
    ).fetchone()
    if not intake_table:
        return True

    intake_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(patient_intake_records)").fetchall()
    }
    required_intake_columns = {
        "id",
        "patient_id",
        "encounter_date",
        "presenting_complaint",
        "provisional_diagnosis",
        "treatment_history",
        "allergies_snapshot",
        "current_medications_snapshot",
        "suicidality",
        "substance_use",
        "created_by_user_id",
        "created_at",
        "updated_at",
    }
    if not required_intake_columns.issubset(intake_columns):
        return False
    for row in conn.execute("SELECT id, patient_id FROM patient_intake_records").fetchall():
        if not _is_uuid(row["id"]) or row["patient_id"] not in patient_ids:
            return False
    return True


def migrate_patients_to_identity_table(conn: sqlite3.Connection) -> dict[str, Any]:
    patient_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(patients)").fetchall()
    }
    if _schema_is_canonical(conn, patient_columns):
        return _empty_migration_report()

    report = _empty_migration_report()
    patient_rows = conn.execute("SELECT rowid AS _migration_rowid, * FROM patients").fetchall()
    intake_table_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'patient_intake_records'"
    ).fetchone() is not None
    intake_rows = (
        conn.execute("SELECT rowid AS _migration_rowid, * FROM patient_intake_records").fetchall()
        if intake_table_exists
        else []
    )
    legacy_patient_rows = bool(patient_columns & LEGACY_INTAKE_COLUMNS)
    code_groups: dict[str, list[sqlite3.Row]] = {}
    for row in patient_rows:
        code = _patient_code(_row_value(row, "patient_code"))
        if code is not None:
            code_groups.setdefault(code, []).append(row)
    collision_codes = {code for code, rows in code_groups.items() if len(rows) > 1}
    collision_patient_ids = {
        _record_id(row, index)
        for index, row in enumerate(patient_rows)
        if _patient_code(_row_value(row, "patient_code")) in collision_codes
    }

    patient_outcomes: list[tuple[sqlite3.Row, str, str | None, str | None]] = []
    patient_id_map: dict[str, str] = {}
    code_map: dict[str, str] = {}
    for index, row in enumerate(patient_rows):
        code = _patient_code(_row_value(row, "patient_code"))
        required_values = (
            code,
            _row_value(row, "first_name"),
            _row_value(row, "last_name"),
            _row_value(row, "sex"),
            _row_value(row, "dob"),
        )
        if code in collision_codes:
            patient_outcomes.append((row, "collision", None, code))
        elif any(value in (None, "") for value in required_values) or _row_value(row, "sex") not in ("Male", "Female"):
            patient_outcomes.append((row, "unresolved", None, code))
        else:
            new_id = str(row["id"]) if _is_uuid(_row_value(row, "id")) else str(uuid4())
            patient_outcomes.append((row, "migrated", new_id, code))
            if _row_value(row, "id") not in (None, ""):
                patient_id_map[str(row["id"])] = new_id
            if code is not None:
                code_map[code] = new_id

    conn.execute("PRAGMA foreign_keys = OFF")
    if intake_table_exists:
        conn.execute("ALTER TABLE patient_intake_records RENAME TO patient_intake_records_legacy")
    conn.execute("ALTER TABLE patients RENAME TO patients_legacy")
    conn.execute(PATIENT_TABLE_SQL)
    conn.execute(INTAKE_TABLE_SQL)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS patient_migration_quarantine (
          source_table TEXT NOT NULL,
          record_id TEXT NOT NULL,
          reason TEXT NOT NULL,
          payload TEXT NOT NULL,
          quarantined_at TEXT NOT NULL,
          PRIMARY KEY (source_table, record_id)
        )
        """
    )

    def quarantine(source_table: str, row: sqlite3.Row, row_number: int, reason: str) -> None:
        record_id = _record_id(row, row_number)
        conn.execute(
            """
            INSERT OR REPLACE INTO patient_migration_quarantine
              (source_table, record_id, reason, payload, quarantined_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_table, record_id, reason, _row_payload(row), now_iso()),
        )
        report["quarantinedCount"] += 1
        report_key = "collisionRecordIds" if reason == "collision" else "unresolvedRecordIds"
        report[report_key].append(record_id)

    for index, (row, outcome, new_id, code) in enumerate(patient_outcomes):
        if outcome != "migrated":
            quarantine("patients", row, index, outcome)
            continue
        created_at = _row_value(row, "created_at") or now_iso()
        updated_at = _row_value(row, "updated_at") or created_at
        created_by_user_id = _row_value(row, "created_by_user_id") or "unknown"
        try:
            resource_version = int(_row_value(row, "resource_version", 1) or 1)
        except (TypeError, ValueError):
            resource_version = 1
        conn.execute(
            """
            INSERT INTO patients
              (id, patient_code, first_name, last_name, sex, dob, phone_number, status,
               resource_version, created_by_user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id,
                code,
                _row_value(row, "first_name"),
                _row_value(row, "last_name"),
                _row_value(row, "sex"),
                _row_value(row, "dob"),
                _row_value(row, "phone_number"),
                _row_value(row, "status", "active") or "active",
                resource_version,
                created_by_user_id,
                created_at,
                updated_at,
            ),
        )
        report["migratedPatientCount"] += 1

    used_encounter_ids: set[str] = set()
    if intake_table_exists:
        for index, row in enumerate(intake_rows):
            patient_ref = _row_value(row, "patient_id")
            new_patient_id = patient_id_map.get(str(patient_ref))
            if new_patient_id is None:
                new_patient_id = code_map.get(_patient_code(patient_ref))
            if new_patient_id is None:
                reason = "collision" if (
                    str(patient_ref) in collision_patient_ids
                    or _patient_code(patient_ref) in collision_codes
                ) else "unresolved"
                quarantine("patient_intake_records", row, index, reason)
                continue

            old_encounter_id = _row_value(row, "id")
            encounter_id = str(old_encounter_id) if _is_uuid(old_encounter_id) else str(uuid4())
            if encounter_id in used_encounter_ids:
                quarantine("patient_intake_records", row, index, "collision")
                continue
            used_encounter_ids.add(encounter_id)
            created_at = _row_value(row, "created_at") or now_iso()
            updated_at = _row_value(row, "updated_at") or created_at
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
                    encounter_id,
                    new_patient_id,
                    _row_value(row, "encounter_date") or created_at,
                    _row_value(row, "presenting_complaint", ""),
                    _row_value(row, "provisional_diagnosis", ""),
                    _row_value(row, "treatment_history", "[]"),
                    _row_value(row, "allergies_snapshot", "[]"),
                    _row_value(row, "current_medications_snapshot", "[]"),
                    _row_value(row, "suicidality", "suicidality_none"),
                    int(_row_value(row, "substance_use", 0) or 0),
                    _row_value(row, "created_by_user_id") or "unknown",
                    created_at,
                    updated_at,
                ),
            )
            report["migratedEncounterCount"] += 1
    elif legacy_patient_rows:
        for row, outcome, patient_id, _ in patient_outcomes:
            if outcome != "migrated":
                continue
            created_at = _row_value(row, "created_at") or now_iso()
            updated_at = _row_value(row, "updated_at") or created_at
            encounter_id = str(uuid4())
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
                    encounter_id,
                    patient_id,
                    _row_value(row, "created_at") or created_at,
                    _row_value(row, "presenting_complaint", ""),
                    _row_value(row, "provisional_diagnosis", ""),
                    _row_value(row, "treatment_history", "[]"),
                    _row_value(row, "allergies", "[]"),
                    _row_value(row, "current_medications", "[]"),
                    _row_value(row, "suicidality", "suicidality_none"),
                    int(_row_value(row, "substance_use", 0) or 0),
                    _row_value(row, "created_by_user_id") or "unknown",
                    created_at,
                    updated_at,
                ),
            )
            report["migratedEncounterCount"] += 1

    if conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'patient_code_reservations'"
    ).fetchone():
        conn.execute("DELETE FROM patient_code_reservations")
    conn.execute("DROP TABLE patients_legacy")
    if intake_table_exists:
        conn.execute("DROP TABLE patient_intake_records_legacy")
    conn.execute("PRAGMA foreign_keys = ON")
    return report
