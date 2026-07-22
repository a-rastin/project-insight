from __future__ import annotations

import re
from datetime import UTC, date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
TEXT_LIMIT = 2000
DIAGNOSIS_LIMIT = 240
LIST_ITEM_LIMIT = 160
ICD10_V1_PATTERN = re.compile(r"^[A-TV-Z][0-9][0-9A-Z](?:\.?[0-9A-Z])?$", re.IGNORECASE)


class ClinicalFlag(BaseModel):
    suicidality: Literal["suicidality_none", "ideation", "plan", "attempt"] = "suicidality_none"
    substanceUse: bool = False

    @field_validator("suicidality", mode="before")
    @classmethod
    def normalize_suicidality(cls, value: Any) -> Any:
        if value == "none":
            return "suicidality_none"
        return value


class PatientDemographics(BaseModel):
    patientCode: str | None = None
    firstName: str
    lastName: str
    sex: str
    dob: date
    phoneNumber: str | None = None

    @field_validator("dob")
    @classmethod
    def check_dob(cls, value: date) -> date:
        today = datetime.now(UTC).date()
        if value > today:
            raise ValueError("Date of birth cannot be in the future.")
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 1:
            raise ValueError("Date of birth must be at least 1 year ago.")
        return value

    @field_validator("sex")
    @classmethod
    def normalize_sex(cls, value: str) -> str:
        value = value.strip()
        if value not in ("Male", "Female"):
            raise ValueError("Sex must be Male or Female.")
        return value

    @field_validator("firstName", "lastName")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name is required.")
        if len(value) > 80:
            raise ValueError("Name must be 80 characters or fewer.")
        return value

    @field_validator("patientCode")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip().upper()
        if value and not re.fullmatch(r"[A-Z0-9]{6}", value):
            raise ValueError("Patient code must be 6 uppercase letters or numbers.")
        return value or None

    @field_validator("phoneNumber")
    @classmethod
    def strip_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        digits = re.sub(r"\D", "", value)
        return digits or None


class ClinicalSection(BaseModel):
    encounterDate: str | None = None
    presentingComplaint: str
    provisionalDiagnosis: str
    treatmentHistory: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    currentMedications: list[str] = Field(default_factory=list)
    riskFlags: ClinicalFlag = Field(default_factory=ClinicalFlag)

    @field_validator("presentingComplaint")
    @classmethod
    def trim_presenting_complaint(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Presenting complaint is required.")
        if len(value) > TEXT_LIMIT:
            raise ValueError(f"Presenting complaint must be {TEXT_LIMIT} characters or fewer.")
        return value

    @field_validator("provisionalDiagnosis")
    @classmethod
    def trim_provisional_diagnosis(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Provisional diagnosis is required.")
        if len(value) > DIAGNOSIS_LIMIT:
            raise ValueError(f"Provisional diagnosis must be {DIAGNOSIS_LIMIT} characters or fewer.")
        compact = value.replace(".", "")
        if " " not in value and any(char.isdigit() for char in value) and len(compact) <= 4 and not ICD10_V1_PATTERN.fullmatch(value):
            raise ValueError("Provisional diagnosis must be free text or a v1 ICD-10 code pattern.")
        return value

    @field_validator("treatmentHistory", "allergies", "currentMedications", mode="before")
    @classmethod
    def default_optional_lists(cls, value: Any) -> list[str]:
        if value is None:
            return []
        return value

    @field_validator("riskFlags", mode="before")
    @classmethod
    def default_risk_flags(cls, value: Any) -> Any:
        return {} if value is None else value

    @field_validator("treatmentHistory", "allergies", "currentMedications")
    @classmethod
    def normalize_optional_lists(cls, value: list[Any]) -> list[str]:
        normalized: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                continue
            if len(text) > LIST_ITEM_LIMIT:
                raise ValueError(f"List items must be {LIST_ITEM_LIMIT} characters or fewer.")
            normalized.append(text)
        return normalized


DEMOGRAPHICS_FIELDS = frozenset(PatientDemographics.model_fields)
CLINICAL_FIELDS = frozenset(ClinicalSection.model_fields)


class PatientIntake(BaseModel):
    demographics: PatientDemographics
    clinical: ClinicalSection

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_flat_payload(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        if "demographics" in value or "clinical" in value:
            return value
        return {
            "demographics": {field: value[field] for field in DEMOGRAPHICS_FIELDS if field in value},
            "clinical": {field: value[field] for field in CLINICAL_FIELDS if field in value},
        }

    def to_patient_record(self) -> dict[str, Any]:
        return {**self.demographics.model_dump(mode="json"), **self.clinical.model_dump(mode="json")}


PatientCreate = PatientIntake


def generate_patient_code() -> str:
    import secrets

    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(6))
