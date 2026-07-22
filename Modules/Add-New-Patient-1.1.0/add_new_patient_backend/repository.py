from __future__ import annotations

import json
from datetime import UTC, date, datetime
from typing import Any
from uuid import uuid4

from .db import DatabaseAdapter


def now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def json_list(value: str | None) -> list[str]:
    if not value:
        return []
    parsed = json.loads(value)
    return parsed if isinstance(parsed, list) else []


def canonical_suicidality(value: str | None) -> str:
    return "suicidality_none" if value in (None, "", "none") else value


def compute_age(dob_value: str) -> int:
    dob = date.fromisoformat(dob_value)
    today = datetime.now(UTC).date()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def patient_row(row: Any) -> dict[str, Any]:
    record = {
        "id": row["id"],
        "patientCode": row["patient_code"],
        "firstName": row["first_name"],
        "lastName": row["last_name"],
        "sex": row["sex"],
        "dob": row["dob"],
        "age": compute_age(row["dob"]),
        "phoneNumber": row["phone_number"],
        "createdByUserId": row["created_by_user_id"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }
    if "intake_id" not in row.keys() or row["intake_id"] is None:
        return record
    return {
        **record,
        "intakeId": row["intake_id"],
        "encounterDate": row["encounter_date"],
        "presentingComplaint": row["presenting_complaint"],
        "provisionalDiagnosis": row["provisional_diagnosis"],
        "treatmentHistory": json_list(row["treatment_history"]),
        "allergies": json_list(row["allergies_snapshot"]),
        "currentMedications": json_list(row["current_medications_snapshot"]),
        "riskFlags": {
            "suicidality": canonical_suicidality(row["suicidality"]),
            "substanceUse": bool(row["substance_use"]),
        },
    }


def intake_row(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "patientId": row["patient_id"],
        "encounterDate": row["encounter_date"],
        "presentingComplaint": row["presenting_complaint"],
        "provisionalDiagnosis": row["provisional_diagnosis"],
        "treatmentHistory": json_list(row["treatment_history"]),
        "allergies": json_list(row["allergies_snapshot"]),
        "currentMedications": json_list(row["current_medications_snapshot"]),
        "riskFlags": {
            "suicidality": canonical_suicidality(row["suicidality"]),
            "substanceUse": bool(row["substance_use"]),
        },
        "createdByUserId": row["created_by_user_id"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def _find_patient_id_row(conn: Any, id_or_code: str) -> Any:
    return conn.execute(
        "SELECT id FROM patients WHERE id = ? OR patient_code = ?",
        (id_or_code, id_or_code.upper()),
    ).fetchone()


CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class PatientRepository:
    def __init__(self, adapter: DatabaseAdapter) -> None:
        self.adapter = adapter

    def initialize(self) -> None:
        self.adapter.initialize()

    def ping(self) -> bool:
        return self.adapter.ping()

    def list_patients(self) -> list[dict[str, Any]]:
        with self.adapter.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                  p.*,
                  i.id AS intake_id,
                  i.encounter_date,
                  i.presenting_complaint,
                  i.provisional_diagnosis,
                  i.treatment_history,
                  i.allergies_snapshot,
                  i.current_medications_snapshot,
                  i.suicidality,
                  i.substance_use
                FROM patients p
                LEFT JOIN patient_intake_records i ON i.id = (
                  SELECT id FROM patient_intake_records
                  WHERE patient_id = p.id
                  ORDER BY encounter_date DESC, created_at DESC
                  LIMIT 1
                )
                ORDER BY p.created_at ASC
                """
            ).fetchall()
        return [patient_row(row) for row in rows]

    def get_patient(self, id_or_code: str) -> dict[str, Any] | None:
        with self.adapter.connect() as conn:
            row = conn.execute(
                """
                SELECT
                  p.*,
                  i.id AS intake_id,
                  i.encounter_date,
                  i.presenting_complaint,
                  i.provisional_diagnosis,
                  i.treatment_history,
                  i.allergies_snapshot,
                  i.current_medications_snapshot,
                  i.suicidality,
                  i.substance_use
                FROM patients p
                LEFT JOIN patient_intake_records i ON i.id = (
                  SELECT id FROM patient_intake_records
                  WHERE patient_id = p.id
                  ORDER BY encounter_date DESC, created_at DESC
                  LIMIT 1
                )
                WHERE p.id = ? OR p.patient_code = ?
                """,
                (id_or_code, id_or_code.upper()),
            ).fetchone()
        return patient_row(row) if row else None

    def list_intake_records(self, id_or_code: str) -> tuple[dict[str, Any], list[dict[str, Any]]] | None:
        with self.adapter.connect() as conn:
            patient = conn.execute(
                """
                SELECT
                  p.*,
                  i.id AS intake_id,
                  i.encounter_date,
                  i.presenting_complaint,
                  i.provisional_diagnosis,
                  i.treatment_history,
                  i.allergies_snapshot,
                  i.current_medications_snapshot,
                  i.suicidality,
                  i.substance_use
                FROM patients p
                LEFT JOIN patient_intake_records i ON i.id = (
                  SELECT id FROM patient_intake_records
                  WHERE patient_id = p.id
                  ORDER BY encounter_date DESC, created_at DESC
                  LIMIT 1
                )
                WHERE p.id = ? OR p.patient_code = ?
                """,
                (id_or_code, id_or_code.upper()),
            ).fetchone()
            if not patient:
                return None
            patient_dict = patient_row(patient)
            intake_rows = conn.execute(
                """
                SELECT id, patient_id, encounter_date, presenting_complaint, provisional_diagnosis,
                       treatment_history, allergies_snapshot, current_medications_snapshot,
                       suicidality, substance_use, created_by_user_id, created_at, updated_at
                FROM patient_intake_records
                WHERE patient_id = ?
                ORDER BY encounter_date DESC, created_at DESC
                """,
                (patient_dict["id"],),
            ).fetchall()
        return patient_dict, [intake_row(row) for row in intake_rows]

    def create_patient(self, patient: dict[str, Any], created_by_user_id: str) -> dict[str, Any]:
        now = now_iso()
        encounter_date = patient.get("encounterDate") or now
        with self.adapter.connect() as conn:
            conn.execute(
                """
                INSERT INTO patients
                  (id, patient_code, first_name, last_name, sex, dob, phone_number, created_by_user_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    patient["id"],
                    patient["patientCode"],
                    patient["firstName"],
                    patient["lastName"],
                    patient["sex"],
                    patient["dob"],
                    patient.get("phoneNumber") or None,
                    created_by_user_id,
                    now,
                    now,
                ),
            )
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
                    patient["id"],
                    encounter_date,
                    patient["presentingComplaint"],
                    patient["provisionalDiagnosis"],
                    json.dumps(patient.get("treatmentHistory") or []),
                    json.dumps(patient.get("allergies") or []),
                    json.dumps(patient.get("currentMedications") or []),
                    canonical_suicidality((patient.get("riskFlags") or {}).get("suicidality")),
                    1 if (patient.get("riskFlags") or {}).get("substanceUse", False) else 0,
                    created_by_user_id,
                    now,
                    now,
                ),
            )
        return self.get_patient(patient["id"])  # type: ignore[return-value]

    def existing_codes(self) -> set[str]:
        with self.adapter.connect() as conn:
            rows = conn.execute("SELECT patient_code FROM patients").fetchall()
        return {row["patient_code"] for row in rows}
