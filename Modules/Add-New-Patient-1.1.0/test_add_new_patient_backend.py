from __future__ import annotations

import json
import hmac
from hashlib import sha256
import os
import socket
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import UUID


PSY_HEADER = {"x-demo-auth-user": "psy-1"}


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class MockAuthenticationServer:
    def __init__(self) -> None:
        self.payloads: dict[str, tuple[int, dict]] = {}
        self.requests: list[dict[str, str]] = []

    def set_payload(self, session_id: str, payload: dict, status: int = 200) -> None:
        self.payloads[session_id] = (status, payload)

    def __enter__(self) -> "MockAuthenticationServer":
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                cookie = self.headers.get("Cookie") or ""
                token = next((part.split("=", 1)[1] for part in cookie.split(";") if part.strip().startswith("insight_session=")), "")
                owner.requests.append({"path": self.path, "cookie": cookie})
                status, payload = owner.payloads.get(token, (401, {"authenticated": False}))
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_: object) -> None:
                return

        self.port = free_port()
        self.server = ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.port}/api/auth/session"
        return self

    def __exit__(self, *_: object) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


class AddNewPatientServer:
    def __init__(self, auth_session_url: str | None = None) -> None:
        self.auth_session_url = auth_session_url

    def __enter__(self) -> str:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, "add_new_patient.sqlite3")
        os.environ["ADD_NEW_PATIENT_DB_PATH"] = self.db_path
        if self.auth_session_url:
            os.environ["AUTH_SESSION_URL"] = self.auth_session_url
            os.environ["ADD_NEW_PATIENT_MOCK_AUTH"] = "0"
        else:
            os.environ.pop("AUTH_SESSION_URL", None)
            os.environ.pop("ADD_NEW_PATIENT_MOCK_AUTH", None)
        os.environ.pop("AUTH_BASE_URL", None)
        for name in list(sys.modules):
            if name == "add_new_patient_backend" or name.startswith("add_new_patient_backend."):
                del sys.modules[name]

        import uvicorn
        from add_new_patient_backend.main import app

        self.port = free_port()
        self.config = uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="error")
        self.server = uvicorn.Server(self.config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()

        base = f"http://127.0.0.1:{self.port}"
        deadline = time.time() + 5
        while time.time() < deadline:
            try:
                request_json(base, "/api/health")
                return base
            except Exception:
                time.sleep(0.05)
        raise RuntimeError("server did not start")

    def __exit__(self, *_: object) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)
        self.tempdir.cleanup()


def request_json(
    base: str,
    path: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict | None = None,
) -> tuple[int, dict | None]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = Request(
        f"{base}{path}",
        data=data,
        method=method,
        headers={"content-type": "application/json", **(headers or {})},
    )
    try:
        with urlopen(req, timeout=5) as response:
            raw = response.read()
            try:
                return response.status, json.loads(raw) if raw else None
            except json.JSONDecodeError:
                return response.status, {"_raw": raw.decode("utf-8", errors="replace")}
    except HTTPError as error:
        try:
            payload = json.loads(error.read().decode("utf-8"))
        finally:
            if error.fp:
                error.fp.close()
            error.close()
        return error.code, payload


def request_json_with_headers(
    base: str,
    path: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict | None = None,
) -> tuple[int, dict | None, dict[str, str]]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = Request(
        f"{base}{path}",
        data=data,
        method=method,
        headers={"content-type": "application/json", **(headers or {})},
    )
    try:
        with urlopen(req, timeout=5) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None, dict(response.headers.items())
    except HTTPError as error:
        try:
            payload = json.loads(error.read().decode("utf-8"))
        finally:
            if error.fp:
                error.fp.close()
            error.close()
        return error.code, payload, dict(error.headers.items())


def csrf_headers(base: str, headers: dict[str, str] | None = None) -> dict[str, str]:
    req = Request(f"{base}/api/add-new-patient/csrf", method="GET")
    with urlopen(req, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
        cookie = response.headers["set-cookie"].split(";", 1)[0]
    existing_cookie = (headers or {}).get("cookie")
    return {
        **(headers or {}),
        "cookie": "; ".join(part for part in (existing_cookie, cookie) if part),
        "x-csrf-token": payload["csrfToken"],
    }


def valid_payload(**overrides: object) -> dict:
    payload = {
        "demographics": {
            "patientCode": "TEST01",
            "firstName": "Jane",
            "lastName": "Doe",
            "sex": "Female",
            "dob": dob_for_age(40),
            "phoneNumber": "5551234567",
        },
        "clinical": {
            "presentingComplaint": "Persistent low mood and insomnia.",
            "provisionalDiagnosis": "F32.1",
            "treatmentHistory": ["CBT in 2024"],
            "allergies": ["penicillin"],
            "currentMedications": ["sertraline 50 mg"],
            "riskFlags": {"suicidality": "ideation", "substanceUse": False},
        },
    }
    for key, value in overrides.items():
        if key in payload["demographics"]:
            payload["demographics"][key] = value
        elif key in payload["clinical"]:
            payload["clinical"][key] = value
        else:
            payload[key] = value
    return payload


def flat_payload(**overrides: object) -> dict:
    payload = {**valid_payload()["demographics"], **valid_payload()["clinical"]}
    payload.update(overrides)
    return payload


def canonical_patient_payload(**overrides: object) -> dict:
    payload = {**valid_payload()["demographics"], "status": "active"}
    payload.update(overrides)
    return payload


def canonical_encounter_payload(patient_id: str, **overrides: object) -> dict:
    payload = {"patientId": patient_id, **valid_payload()["clinical"]}
    payload.update(overrides)
    return payload


def dob_for_age(age: int) -> str:
    today = datetime.now(UTC).date()
    try:
        return today.replace(year=today.year - age).isoformat()
    except ValueError:
        return today.replace(year=today.year - age, day=28).isoformat()


def dob_days_ago(days: int) -> str:
    return (datetime.now(UTC).date() - timedelta(days=days)).isoformat()


def future_dob() -> str:
    return (datetime.now(UTC).date() + timedelta(days=1)).isoformat()


def future_iso() -> str:
    return (datetime.now(UTC) + timedelta(hours=1)).isoformat().replace("+00:00", "Z")


def auth_payload(**overrides: dict) -> dict:
    payload = {
        "schemaVersion": "1.0.0",
        "authenticated": True,
        "session": {"id": "auth-1", "expiresAt": future_iso()},
        "user": {"id": "psy-1", "roles": ["psychiatrist"], "displayName": "Verified Clinician"},
        "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(payload.get(key), dict):
            payload[key] = {**payload[key], **value}
        else:
            payload[key] = value
    return payload


class AuthIdentityNormalizationTest(unittest.TestCase):
    def test_normalize_accepts_psychiatrist_with_valid_session(self) -> None:
        from add_new_patient_backend.auth import normalize_auth_identity

        identity = normalize_auth_identity(auth_payload())
        assert identity is not None
        self.assertEqual(identity["authSessionId"], "auth-1")
        self.assertEqual(identity["user"]["id"], "psy-1")
        self.assertEqual(identity["user"]["role"], "PSYCHIATRIST")
        self.assertEqual(identity["user"]["fullName"], "Verified Clinician")
        self.assertEqual(identity["user"]["title"], "Dr.")

    def test_normalize_authenticated_accepts_admin_but_psychiatrist_rejects_it(self) -> None:
        from add_new_patient_backend.auth import normalize_authenticated_session, normalize_psychiatrist_session

        payload = auth_payload(user={"id": "admin-1", "roles": ["ADMIN"], "displayName": "Admin"})
        self.assertIsNotNone(normalize_authenticated_session(payload))
        self.assertIsNone(normalize_psychiatrist_session(payload))

    def test_normalize_rejects_missing_or_expired_sessions(self) -> None:
        from add_new_patient_backend.auth import normalize_auth_identity

        blocked_payloads = [
            auth_payload(session=None),
            auth_payload(authenticated=False),
            auth_payload(session={"expiresAt": "2000-01-01T00:00:00Z"}),
        ]
        for payload in blocked_payloads:
            with self.subTest(payload=payload):
                self.assertIsNone(normalize_auth_identity(payload))


class AddNewPatientBackendTest(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/health")
            self.assertEqual(status, 200)
            self.assertEqual(data, {"module": "Add New Patient", "status": "ok"})

    def test_dashboard_module_route_contract(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/internal/dashboard/module-routes/add-new-patient")
            self.assertEqual(status, 200)
            self.assertEqual(
                data,
                {
                    "moduleId": "add-new-patient",
                    "title": "Add New Patient",
                    "href": "/modules/add-new-patient/",
                },
            )

    def test_dashboard_discovery_contract_and_readiness(self) -> None:
        with AddNewPatientServer() as base:
            contract_status, contract = request_json(base, "/modules/add-new-patient/contract")
            ready_status, ready = request_json(base, "/modules/add-new-patient/ready")

        self.assertEqual(contract_status, 200)
        self.assertEqual(
            contract,
            {
                "moduleId": "add-new-patient",
                "interfaceVersion": "1.0.0",
                "basePath": "/modules/add-new-patient/",
            },
        )
        self.assertEqual(ready_status, 200)
        self.assertEqual(ready, {"status": "ready"})

    def test_workflow_draft_reserves_identity_and_expires_safely(self) -> None:
        server = AddNewPatientServer()
        with server as base:
            headers = csrf_headers(base, PSY_HEADER)
            status, created = request_json(
                base,
                "/api/add-new-patient/v1/workflow-drafts",
                method="POST",
                headers=headers,
            )
            self.assertEqual(status, 201)
            draft = created["workflowDraft"]
            self.assertEqual(draft["phase"], "diagnosis")
            self.assertRegex(draft["id"], r"^[0-9a-f-]{36}$")
            self.assertIsNotNone(UUID(draft["patientId"]))
            self.assertRegex(draft["patientCode"], r"^[A-Z0-9]{6}$")
            self.assertIn("expiresAt", draft)
            self.assertIsNone(draft["retentionUntil"])

            status, resumed = request_json(
                base,
                f"/api/add-new-patient/v1/workflow-drafts/{draft['id']}",
                headers=PSY_HEADER,
            )
            self.assertEqual(status, 200)
            self.assertEqual(resumed["workflowDraft"], draft)

            status, resolution = request_json(
                base,
                f"/api/patients/lookup?code={draft['patientCode']}",
                headers=PSY_HEADER,
            )
            self.assertEqual(status, 200)
            self.assertEqual(resolution["id"], draft["patientId"])
            self.assertEqual(resolution["patient_code"], draft["patientCode"])

            with sqlite3.connect(server.db_path) as conn:
                conn.execute(
                    "UPDATE workflow_drafts SET expires_at = '2000-01-01T00:00:00Z' WHERE id = ?",
                    (draft["id"],),
                )
            status, expired = request_json(
                base,
                f"/api/add-new-patient/v1/workflow-drafts/{draft['id']}",
                headers=PSY_HEADER,
            )
            self.assertEqual(status, 200)
            self.assertEqual(expired["workflowDraft"]["phase"], "expired")
            self.assertIsNotNone(expired["workflowDraft"]["retentionUntil"])
            status, _ = request_json(
                base,
                f"/api/patients/lookup?code={draft['patientCode']}",
                headers=PSY_HEADER,
            )
            self.assertEqual(status, 404)

    def test_workflow_draft_cancellation_requires_psychiatrist_and_csrf(self) -> None:
        with AddNewPatientServer() as base:
            headers = csrf_headers(base, PSY_HEADER)
            _, created = request_json(
                base,
                "/api/add-new-patient/v1/workflow-drafts",
                method="POST",
                headers=headers,
            )
            draft_id = created["workflowDraft"]["id"]
            status, _ = request_json(
                base,
                f"/api/add-new-patient/v1/workflow-drafts/{draft_id}",
                method="DELETE",
                headers=PSY_HEADER,
            )
            self.assertEqual(status, 403)
            status, cancelled = request_json(
                base,
                f"/api/add-new-patient/v1/workflow-drafts/{draft_id}",
                method="DELETE",
                headers=headers,
            )
            self.assertEqual(status, 200)
            self.assertEqual(cancelled["workflowDraft"]["phase"], "cancelled")
            self.assertIsNotNone(cancelled["workflowDraft"]["retentionUntil"])

    def test_signed_diagnosis_completion_advances_only_matching_draft(self) -> None:
        secret = "workflow-test-secret"
        previous = os.environ.get("WORKFLOW_SERVICE_SECRET")
        os.environ["WORKFLOW_SERVICE_SECRET"] = secret
        try:
            with AddNewPatientServer() as base:
                headers = csrf_headers(base, PSY_HEADER)
                _, created = request_json(
                    base,
                    "/api/add-new-patient/v1/workflow-drafts",
                    method="POST",
                    headers=headers,
                )
                draft = created["workflowDraft"]
                payload = {"patientCode": draft["patientCode"], "decision": "confirmed"}
                signature = hmac.new(
                    secret.encode(),
                    f"{draft['id']}:{draft['patientCode']}:confirmed".encode(),
                    sha256,
                ).hexdigest()
                status, completed = request_json(
                    base,
                    f"/internal/workflow-drafts/{draft['id']}/diagnosis-complete",
                    method="POST",
                    headers={"X-Workflow-Signature": signature},
                    body=payload,
                )
                self.assertEqual(status, 200)
                self.assertEqual(completed["workflowDraft"]["phase"], "patient-information")
                self.assertEqual(completed["workflowDraft"]["diagnosisDecision"], "confirmed")
                status, _ = request_json(
                    base,
                    f"/internal/workflow-drafts/{draft['id']}/diagnosis-complete",
                    method="POST",
                    headers={"X-Workflow-Signature": "bad"},
                    body=payload,
                )
                self.assertEqual(status, 403)
        finally:
            if previous is None:
                os.environ.pop("WORKFLOW_SERVICE_SECRET", None)
            else:
                os.environ["WORKFLOW_SERVICE_SECRET"] = previous

    def test_workflow_finalization_is_atomic_owned_and_idempotent(self) -> None:
        server = AddNewPatientServer()
        with server as base:
            headers = csrf_headers(base, PSY_HEADER)
            _, created = request_json(
                base,
                "/api/add-new-patient/v1/workflow-drafts",
                method="POST",
                headers=headers,
            )
            draft = created["workflowDraft"]
            payload = valid_payload(patient_code="WRONG1")
            path = f"/api/add-new-patient/v1/workflow-drafts/{draft['id']}/finalize"
            blocked_status, _ = request_json(base, path, method="POST", headers=headers, body=payload)
            self.assertEqual(blocked_status, 409)
            with sqlite3.connect(server.db_path) as conn:
                conn.execute(
                    "UPDATE workflow_drafts SET phase = 'patient-information' WHERE id = ?",
                    (draft["id"],),
                )

            status, finalized = request_json(base, path, method="POST", headers=headers, body=payload)
            self.assertEqual(status, 201)
            self.assertEqual(finalized["patientId"], draft["patientId"])
            self.assertEqual(finalized["patient"]["patientCode"], draft["patientCode"])
            self.assertIsNotNone(UUID(finalized["encounterId"]))

            retry_status, retry = request_json(base, path, method="POST", headers=headers, body=payload)
            self.assertEqual(retry_status, 200)
            self.assertEqual(retry, finalized)
            with sqlite3.connect(server.db_path) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0], 1)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM patient_intake_records").fetchone()[0], 1)
                row = conn.execute(
                    "SELECT phase, completed_at FROM workflow_drafts WHERE id = ?", (draft["id"],)
                ).fetchone()
                self.assertEqual(row[0], "completed")
                self.assertIsNotNone(row[1])

            with sqlite3.connect(server.db_path) as conn:
                conn.execute(
                    "UPDATE workflow_drafts SET owner_session_id = 'different-session' WHERE id = ?",
                    (draft["id"],),
                )
            denied_status, _ = request_json(base, path, method="POST", headers=headers, body=payload)
            self.assertEqual(denied_status, 404)

    def test_versioned_intake_api_creates_lists_and_resolves_patients(self) -> None:
        with AddNewPatientServer() as base:
            headers = csrf_headers(base, PSY_HEADER)
            self.assertEqual(request_json(base, "/api/add-new-patient/v1/csrf")[0], 200)
            status, created = request_json(
                base,
                "/api/add-new-patient/v1/intakes",
                method="POST",
                headers=headers,
                body=valid_payload(),
            )
            self.assertEqual(status, 201)
            status, listed = request_json(base, "/api/add-new-patient/v1/patients", headers=PSY_HEADER)
            self.assertEqual(status, 200)
            self.assertEqual([patient["patientCode"] for patient in listed["patients"]], ["TEST01"])
            status, resolved = request_json(base, "/api/add-new-patient/v1/patients/TEST01", headers=PSY_HEADER)

        self.assertEqual(status, 200)
        self.assertEqual(resolved["patient"]["id"], created["patient"]["id"])

    def test_create_patient_returns_201_with_full_record(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload())
            self.assertEqual(status, 201)
            patient = data["patient"]
            self.assertEqual(patient["patientCode"], "TEST01")
            self.assertEqual(patient["firstName"], "Jane")
            self.assertEqual(patient["lastName"], "Doe")
            self.assertEqual(patient["sex"], "Female")
            self.assertEqual(patient["dob"], valid_payload()["demographics"]["dob"])
            self.assertEqual(patient["age"], 40)
            self.assertEqual(patient["phoneNumber"], "5551234567")
            self.assertEqual(patient["createdByUserId"], "psy-1")
            self.assertIn("intakeId", patient)
            self.assertIn("encounterDate", patient)
            self.assertEqual(patient["presentingComplaint"], "Persistent low mood and insomnia.")
            self.assertEqual(patient["provisionalDiagnosis"], "F32.1")
            self.assertEqual(patient["treatmentHistory"], ["CBT in 2024"])
            self.assertEqual(patient["allergies"], ["penicillin"])
            self.assertEqual(patient["currentMedications"], ["sertraline 50 mg"])
            self.assertEqual(patient["riskFlags"], {"suicidality": "ideation", "substanceUse": False})
            self.assertIn("id", patient)
            self.assertIn("createdAt", patient)
            self.assertIn("updatedAt", patient)
            self.assertEqual(data["patientId"], patient["id"])
            self.assertEqual(data["encounterId"], patient["intakeId"])
    def test_structured_clinical_fields_preserve_text_and_leave_coding_unresolved(self) -> None:
        diagnosis = "Patient-reported mood disorder; clinician review pending"
        medications = ["Sertraline 50 mg nightly", "Unidentified white tablet"]
        payload = valid_payload(
            patientCode="STRC01",
            provisionalDiagnosis=diagnosis,
            currentMedications=medications,
        )
        with AddNewPatientServer() as base:
            status, created = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=payload,
            )
            self.assertEqual(status, 201)
            patient_id = created["patient"]["id"]
            expected_codings = [
                {
                    "system": None,
                    "code": None,
                    "display": medication,
                    "resolutionStatus": "unresolved",
                }
                for medication in medications
            ]
            for response in (
                created,
                request_json(base, f"/api/patients/{patient_id}", headers=PSY_HEADER)[1],
                request_json(base, "/api/patients/STRC01/intake", headers=PSY_HEADER)[1],
            ):
                self.assertEqual(response["schemaVersion"], "1.0.0")
                record = response["patient"] if "patient" in response and "intakeRecords" not in response else response["intakeRecords"][0]
                self.assertEqual(record["provisionalDiagnosis"], diagnosis)
                self.assertEqual(record["diagnosisCoding"], {
                    "system": None,
                    "code": None,
                    "display": diagnosis,
                    "resolutionStatus": "unresolved",
                })
                self.assertEqual(record["currentMedications"], medications)
                self.assertEqual(record["medicationCodings"], expected_codings)
                if "sex" in record:
                    self.assertEqual(record["sex"], "Female")
                self.assertNotIn("gender", record)

    def test_canonical_success_responses_include_schema_version(self) -> None:
        with AddNewPatientServer() as base:
            status, patient_response = request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="VERS01"),
            )
            self.assertEqual(status, 201)
            self.assertEqual(patient_response["schemaVersion"], "1.0.0")
            patient_id = patient_response["patient"]["id"]

            status, encounter_response = request_json(
                base,
                "/api/add-new-patient/v1/encounters",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_encounter_payload(patient_id),
            )
            self.assertEqual(status, 201)
            self.assertEqual(encounter_response["schemaVersion"], "1.0.0")

            for path in (
                f"/api/add-new-patient/v1/patients/{patient_id}",
                f"/api/add-new-patient/v1/encounters/{encounter_response['encounter']['id']}",
                f"/api/add-new-patient/v1/patient-resolutions/{patient_id}",
            ):
                status, response = request_json(base, path, headers=PSY_HEADER)
                self.assertEqual(status, 200)
                self.assertEqual(response["schemaVersion"], "1.0.0")

    def test_canonical_patient_can_have_multiple_encounters(self) -> None:
        with AddNewPatientServer() as base:
            status, patient_response = request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="CAN001"),
            )
            self.assertEqual(status, 201)
            patient = patient_response["patient"]
            self.assertEqual(patient["patientCode"], "CAN001")
            self.assertEqual(patient["status"], "active")
            self.assertNotIn("presentingComplaint", patient)

            first_status, first_response = request_json(
                base,
                "/api/add-new-patient/v1/encounters",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_encounter_payload(patient["id"], encounterDate="2026-07-20T10:00:00Z"),
            )
            second_status, second_response = request_json(
                base,
                "/api/add-new-patient/v1/encounters",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_encounter_payload(
                    patient["id"],
                    encounterDate="2026-07-21T10:00:00Z",
                    presentingComplaint="A later episode.",
                ),
            )
            self.assertEqual(first_status, 201)
            self.assertEqual(second_status, 201)
            self.assertEqual(first_response["encounter"]["patientId"], patient["id"])
            self.assertEqual(second_response["encounter"]["patientId"], patient["id"])
            self.assertNotEqual(first_response["encounter"]["id"], second_response["encounter"]["id"])

            get_patient_status, get_patient_response = request_json(
                base,
                f"/api/add-new-patient/v1/patients/{patient['id']}",
                headers=PSY_HEADER,
            )
            self.assertEqual(get_patient_status, 200)
            self.assertEqual(get_patient_response["patient"]["id"], patient["id"])
            for encounter_id in (first_response["encounter"]["id"], second_response["encounter"]["id"]):
                encounter_status, encounter_response = request_json(
                    base,
                    f"/api/add-new-patient/v1/encounters/{encounter_id}",
                    headers=PSY_HEADER,
                )
                self.assertEqual(encounter_status, 200)
                self.assertEqual(encounter_response["encounter"]["patientId"], patient["id"])

    def test_allergies_and_medications_are_encounter_snapshots(self) -> None:
        with AddNewPatientServer() as base:
            _, patient_response = request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="SNAP01"),
            )
            patient_id = patient_response["patient"]["id"]
            encounter_bodies = [
                canonical_encounter_payload(
                    patient_id,
                    allergies=["penicillin"],
                    currentMedications=["sertraline 50 mg"],
                ),
                canonical_encounter_payload(
                    patient_id,
                    allergies=["latex"],
                    currentMedications=["mirtazapine 15 mg"],
                ),
            ]
            encounter_ids = []
            for body in encounter_bodies:
                status, response = request_json(
                    base,
                    "/api/add-new-patient/v1/encounters",
                    method="POST",
                    headers=csrf_headers(base, PSY_HEADER),
                    body=body,
                )
                self.assertEqual(status, 201)
                encounter_ids.append(response["encounter"]["id"])

            for encounter_id, allergies, medications in zip(
                encounter_ids,
                [["penicillin"], ["latex"]],
                [["sertraline 50 mg"], ["mirtazapine 15 mg"]],
            ):
                status, response = request_json(
                    base,
                    f"/api/add-new-patient/v1/encounters/{encounter_id}",
                    headers=PSY_HEADER,
                )
                self.assertEqual(status, 200)
                self.assertEqual(response["encounter"]["allergies"], allergies)
                self.assertEqual(response["encounter"]["currentMedications"], medications)

            status, response = request_json(
                base,
                f"/api/add-new-patient/v1/patients/{patient_id}",
                headers=PSY_HEADER,
            )
            self.assertEqual(status, 200)
            self.assertNotIn("allergies", response["patient"])
            self.assertNotIn("currentMedications", response["patient"])
    def test_patient_resolution_by_uuid_and_code_returns_canonical_version_and_etag(self) -> None:
        with AddNewPatientServer() as base:
            _, created = request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="RES001"),
            )
            patient_id = created["patient"]["id"]
            uuid_status, by_uuid, uuid_headers = request_json_with_headers(
                base,
                f"/api/add-new-patient/v1/patient-resolutions/{patient_id}",
                headers=PSY_HEADER,
            )
            code_status, by_code, code_headers = request_json_with_headers(
                base,
                "/api/add-new-patient/v1/patient-resolutions/res001",
                headers=PSY_HEADER,
            )
            self.assertEqual(uuid_status, 200)
            self.assertEqual(code_status, 200)
            self.assertEqual(by_uuid, by_code)
            self.assertEqual(
                by_uuid,
                {
                    "schemaVersion": "1.0.0",
                    "patientId": patient_id,
                    "patientCode": "RES001",
                    "status": "active",
                    "resourceVersion": 1,
                    "etag": f'"patient:{patient_id}:v1"',
                },
            )
            self.assertEqual(uuid_headers["etag"], by_uuid["etag"])
            self.assertEqual(code_headers["etag"], by_uuid["etag"])

    def test_patient_resolution_returns_merged_and_inactive_statuses(self) -> None:
        server = AddNewPatientServer()
        with server as base:
            headers = csrf_headers(base, PSY_HEADER)
            _, merged = request_json(base, "/api/add-new-patient/v1/patients", "POST", headers, canonical_patient_payload(patientCode="MERGE1"))
            _, inactive = request_json(base, "/api/add-new-patient/v1/patients", "POST", headers, canonical_patient_payload(patientCode="INACT1"))
            with sqlite3.connect(server.db_path) as conn:
                conn.executemany(
                    "UPDATE patients SET status = ?, resource_version = ? WHERE id = ?",
                    [("merged", 2, merged["patient"]["id"]), ("inactive", 3, inactive["patient"]["id"])],
                )
            conn.close()
            for code, patient, expected_status, version in [
                ("MERGE1", merged, "merged", 2),
                ("INACT1", inactive, "inactive", 3),
            ]:
                status, resolution = request_json(base, f"/api/add-new-patient/v1/patient-resolutions/{code}", headers=PSY_HEADER)
                self.assertEqual(status, 200)
                self.assertEqual(resolution["patientId"], patient["patient"]["id"])
                self.assertEqual(resolution["status"], expected_status)
                self.assertEqual(resolution["resourceVersion"], version)

    def test_patient_resolution_quarantines_ambiguous_legacy_alias(self) -> None:
        server = AddNewPatientServer()
        with server as base:
            with sqlite3.connect(server.db_path) as conn:
                for patient_id, patient_code in [
                    ("COLL01", "FIRST1"),
                    ("22222222-2222-4222-8222-222222222222", "COLL01"),
                ]:
                    conn.execute(
                        """
                        INSERT INTO patients
                          (id, patient_code, first_name, last_name, sex, dob, status,
                           created_by_user_id, created_at, updated_at, resource_version)
                        VALUES (?, ?, 'Jane', 'Doe', 'Female', '1986-01-01', 'active',
                                'psy-1', '2026-07-22T00:00:00Z', '2026-07-22T00:00:00Z', 1)
                        """,
                        (patient_id, patient_code),
                    )
            conn.close()
            status, data = request_json(
                base,
                "/api/add-new-patient/v1/patient-resolutions/COLL01",
                headers=PSY_HEADER,
            )
            self.assertEqual(status, 409)
            self.assertEqual(data, {"error": "patient_alias_collision"})

    def test_patient_resolution_rejects_stale_if_match(self) -> None:
        server = AddNewPatientServer()
        with server as base:
            _, created = request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="STALE1"),
            )
            patient_id = created["patient"]["id"]
            _, current, headers = request_json_with_headers(
                base,
                f"/api/add-new-patient/v1/patient-resolutions/{patient_id}",
                headers=PSY_HEADER,
            )
            with sqlite3.connect(server.db_path) as conn:
                conn.execute("UPDATE patients SET resource_version = 2 WHERE id = ?", (patient_id,))
            conn.close()
            status, data = request_json(
                base,
                f"/api/add-new-patient/v1/patient-resolutions/{patient_id}",
                headers={**PSY_HEADER, "If-Match": headers["etag"]},
            )
            self.assertEqual(current["resourceVersion"], 1)
            self.assertEqual(status, 412)
            self.assertEqual(data, {"error": "etag_mismatch"})

    def test_patient_code_is_not_reused_after_patient_becomes_inactive(self) -> None:
        server = AddNewPatientServer()
        with server as base:
            _, created = request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="NOREU1"),
            )
            with sqlite3.connect(server.db_path) as conn:
                conn.execute(
                    "UPDATE patients SET status = 'inactive', resource_version = 2 WHERE id = ?",
                    (created["patient"]["id"],),
                )
            conn.close()
            status, data = request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="NOREU1"),
            )
            self.assertEqual(status, 409)
            self.assertEqual(data["error"], "patient_alias_already_exists")

    def test_canonical_patient_lookup_accepts_patient_code(self) -> None:
        with AddNewPatientServer() as base:
            request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="CAN001"),
            )
            status, data = request_json(
                base,
                "/api/add-new-patient/v1/patients/CAN001",
                headers=PSY_HEADER,
            )
            self.assertEqual(status, 200)
            self.assertEqual(data["patient"]["patientCode"], "CAN001")

    def test_encounter_canonical_route_requires_patient_uuid(self) -> None:
        with AddNewPatientServer() as base:
            request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="ENC001"),
            )
            status, data = request_json(
                base,
                "/api/add-new-patient/v1/encounters",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_encounter_payload("ENC001"),
            )
            self.assertEqual(status, 404)
            self.assertEqual(data, {"message": "Patient was not found."})

    def test_encounter_patient_binding_cannot_be_changed(self) -> None:
        with AddNewPatientServer() as base:
            _, first_patient_response = request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="BIND01"),
            )
            _, second_patient_response = request_json(
                base,
                "/api/add-new-patient/v1/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_patient_payload(patientCode="BIND02"),
            )
            first_patient_id = first_patient_response["patient"]["id"]
            second_patient_id = second_patient_response["patient"]["id"]
            _, encounter_response = request_json(
                base,
                "/api/add-new-patient/v1/encounters",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=canonical_encounter_payload(first_patient_id),
            )
            encounter_id = encounter_response["encounter"]["id"]

            status, _ = request_json(
                base,
                f"/api/add-new-patient/v1/encounters/{encounter_id}",
                method="PATCH",
                headers=csrf_headers(base, PSY_HEADER),
                body={"patientId": second_patient_id},
            )
            self.assertEqual(status, 405)
            _, stored = request_json(
                base,
                f"/api/add-new-patient/v1/encounters/{encounter_id}",
                headers=PSY_HEADER,
            )
            self.assertEqual(stored["encounter"]["patientId"], first_patient_id)

    def test_legacy_adapter_is_atomic_and_idempotent(self) -> None:
        server = AddNewPatientServer()
        with server as base:
            key = "legacy-patient-key-01"
            headers = csrf_headers(base, {**PSY_HEADER, "Idempotency-Key": key})
            first_status, first_response = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=headers,
                body=valid_payload(patientCode="IDEM01"),
            )
            retry_status, retry_response = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=headers,
                body=valid_payload(patientCode="IDEM01"),
            )
            self.assertEqual(first_status, 201)
            self.assertEqual(retry_status, 201)
            self.assertEqual(retry_response, first_response)

            conflict_status, conflict_response = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=headers,
                body=valid_payload(patientCode="IDEM02"),
            )
            self.assertEqual(conflict_status, 409)
            self.assertEqual(conflict_response, {"error": "idempotency_key_reused"})

            conn = sqlite3.connect(server.db_path)
            try:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0], 1)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM patient_intake_records").fetchone()[0], 1)
            finally:
                conn.close()
    def test_optional_intake_fields_default_safely(self) -> None:
        with AddNewPatientServer() as base:
            payload = valid_payload()
            for field in ["treatmentHistory", "allergies", "currentMedications", "riskFlags"]:
                payload["clinical"][field] = None
            status, data = request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=payload)
            self.assertEqual(status, 201)
            patient = data["patient"]
            self.assertEqual(patient["treatmentHistory"], [])
            self.assertEqual(patient["allergies"], [])
            self.assertEqual(patient["currentMedications"], [])
            self.assertEqual(patient["riskFlags"], {"suicidality": "suicidality_none", "substanceUse": False})

    def test_patient_identity_and_intake_record_persist_separately(self) -> None:
        server = AddNewPatientServer()
        with server as base:
            status, data = request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload())
            self.assertEqual(status, 201)
            patient_id = data["patient"]["id"]

            conn = sqlite3.connect(server.db_path)
            conn.row_factory = sqlite3.Row
            try:
                patient_columns = {row["name"] for row in conn.execute("PRAGMA table_info(patients)").fetchall()}
                self.assertTrue({"id", "patient_code", "first_name", "last_name", "sex", "dob", "phone_number", "created_by_user_id", "created_at", "updated_at"}.issubset(patient_columns))
                self.assertNotIn("age", patient_columns)
                self.assertNotIn("presenting_complaint", patient_columns)
                self.assertNotIn("current_medications", patient_columns)

                patient = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
                self.assertEqual(patient["created_by_user_id"], "psy-1")
                self.assertEqual(patient["dob"], valid_payload()["demographics"]["dob"])

                intakes = conn.execute("SELECT * FROM patient_intake_records WHERE patient_id = ?", (patient_id,)).fetchall()
                self.assertEqual(len(intakes), 1)
                self.assertEqual(intakes[0]["presenting_complaint"], "Persistent low mood and insomnia.")
                self.assertEqual(json.loads(intakes[0]["current_medications_snapshot"]), ["sertraline 50 mg"])
                self.assertEqual(intakes[0]["created_by_user_id"], "psy-1")
            finally:
                conn.close()

    def test_list_patients_returns_all_persisted(self) -> None:
        with AddNewPatientServer() as base:
            request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload(patientCode="LIST01"))
            request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload(patientCode="LIST02"))
            status, data = request_json(base, "/api/patients", headers=PSY_HEADER)
            self.assertEqual(status, 200)
            codes = [patient["patientCode"] for patient in data["patients"]]
            self.assertEqual(sorted(codes), ["LIST01", "LIST02"])

    def test_get_patient_by_code_and_id(self) -> None:
        with AddNewPatientServer() as base:
            request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload())
            _, created = request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload(patientCode="GETIT1"))
            patient_id = created["patient"]["id"]
            status, by_code = request_json(base, "/api/patients/GETIT1", headers=PSY_HEADER)
            status_id, by_id = request_json(base, f"/api/patients/{patient_id}", headers=PSY_HEADER)
            self.assertEqual(status, 200)
            self.assertEqual(status_id, 200)
            self.assertEqual(by_code["patient"]["id"], patient_id)
            self.assertEqual(by_id["patient"]["patientCode"], "GETIT1")

    def test_get_patient_intake_returns_patient_and_records_newest_first(self) -> None:
        server = AddNewPatientServer()
        with server as base:
            create_headers = csrf_headers(base, PSY_HEADER)
            create_status, created = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=create_headers,
                body=valid_payload(patientCode="INTK01"),
            )
            if create_status != 201:
                raise AssertionError(f"create failed: {create_status} {created}")
            patient_id = created["patient"]["id"]
            today_dt = datetime.fromisoformat(created["patient"]["encounterDate"].replace("Z", "+00:00"))
            yesterday_iso = (today_dt - timedelta(days=1)).isoformat().replace("+00:00", "Z")
            last_year_iso = (today_dt - timedelta(days=365)).isoformat().replace("+00:00", "Z")

            conn = sqlite3.connect(server.db_path)
            conn.row_factory = sqlite3.Row
            try:
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
                        "intake-older",
                        patient_id,
                        last_year_iso,
                        "Earlier episode.",
                        "F33.1",
                        "[]",
                        "[]",
                        "[]",
                        "ideation",
                        1,
                        "psy-1",
                        last_year_iso,
                        last_year_iso,
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
                        "intake-mid",
                        patient_id,
                        yesterday_iso,
                        "Mid episode.",
                        "F33.1",
                        "[]",
                        "[]",
                        "[]",
                        "suicidality_none",
                        0,
                        "psy-1",
                        yesterday_iso,
                        yesterday_iso,
                    ),
                )
                conn.commit()
            finally:
                conn.close()

            status, data = request_json(base, f"/api/patients/{patient_id}/intake", headers=PSY_HEADER)
            self.assertEqual(status, 200)
            self.assertEqual(data["patient"]["id"], patient_id)
            self.assertEqual(data["patient"]["patientCode"], "INTK01")
            self.assertEqual(len(data["intakeRecords"]), 3)
            self.assertEqual(
                [record["id"] for record in data["intakeRecords"]],
                [created["patient"]["intakeId"], "intake-mid", "intake-older"],
            )
            self.assertEqual(data["intakeRecords"][0]["encounterDate"], created["patient"]["encounterDate"])
            self.assertEqual(data["intakeRecords"][1]["encounterDate"], yesterday_iso)
            self.assertEqual(data["intakeRecords"][2]["encounterDate"], last_year_iso)
            for record in data["intakeRecords"]:
                self.assertIn("id", record)
                self.assertIn("patientId", record)
                self.assertIn("encounterDate", record)
                self.assertIn("presentingComplaint", record)
                self.assertIn("provisionalDiagnosis", record)
                self.assertIn("treatmentHistory", record)
                self.assertIn("allergies", record)
                self.assertIn("currentMedications", record)
                self.assertIn("riskFlags", record)
                self.assertIn("createdByUserId", record)
                self.assertIn("createdAt", record)
                self.assertIn("updatedAt", record)

            status_code, by_code = request_json(base, "/api/patients/INTK01/intake", headers=PSY_HEADER)
            self.assertEqual(status_code, 200)
            self.assertEqual(by_code["patient"]["id"], patient_id)
            self.assertEqual(len(by_code["intakeRecords"]), 3)

            _ = server.db_path

            missing_status, missing_data = request_json(base, "/api/patients/MISSING/intake", headers=PSY_HEADER)
            self.assertEqual(missing_status, 404)
            self.assertEqual(missing_data, {"message": "Patient was not found."})

    def test_get_patient_intake_accepts_admin_role(self) -> None:
        with MockAuthenticationServer() as mock_auth:
            mock_auth.set_payload("psy-sess", auth_payload())
            mock_auth.set_payload(
                "admin-sess",
                auth_payload(user={"id": "admin-1", "roles": ["ADMIN"], "displayName": "Admin"}),
            )
            with AddNewPatientServer(auth_session_url=mock_auth.url) as base:
                create_status, _ = request_json(
                    base,
                    "/api/patients",
                    method="POST",
                    headers=csrf_headers(base, {"cookie": "insight_session=psy-sess"}),
                    body=valid_payload(),
                )
                if create_status != 201:
                    raise AssertionError(f"seed create failed: {create_status}")
                status, data = request_json(
                    base,
                    "/api/patients/TEST01/intake",
                    headers={"cookie": "insight_session=admin-sess"},
                )
                self.assertEqual(status, 200)
                self.assertEqual(data["patient"]["patientCode"], "TEST01")
                self.assertEqual(len(data["intakeRecords"]), 1)

    def test_get_patient_intake_rejects_unknown_role(self) -> None:
        with MockAuthenticationServer() as mock_auth:
            mock_auth.set_payload("psy-sess", auth_payload())
            mock_auth.set_payload(
                "nurse-sess",
                auth_payload(user={"id": "nurse-1", "roles": ["NURSE"], "displayName": "Nurse"}),
            )
            with AddNewPatientServer(auth_session_url=mock_auth.url) as base:
                create_status, _ = request_json(
                    base,
                    "/api/patients",
                    method="POST",
                    headers=csrf_headers(base, {"cookie": "insight_session=psy-sess"}),
                    body=valid_payload(),
                )
                if create_status != 201:
                    raise AssertionError(f"seed create failed: {create_status}")
                status, data = request_json(
                    base,
                    "/api/patients/TEST01/intake",
                    headers={"cookie": "insight_session=nurse-sess"},
                )
                self.assertEqual(status, 403)
                self.assertEqual(data, {"error": "psychiatrist_or_admin_required"})

    def test_get_patient_intake_rejects_unauthenticated(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/patients/ANY/intake")
            self.assertEqual(status, 401)
            self.assertEqual(data, {"error": "authentication_session_required"})

    def test_missing_patient_returns_404(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/patients/MISSING", headers=PSY_HEADER)
            self.assertEqual(status, 404)
            self.assertEqual(data, {"message": "Patient was not found."})

    def test_duplicate_patient_code_rejected_422(self) -> None:
        with AddNewPatientServer() as base:
            request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload())
            status, data = request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload())
            self.assertEqual(status, 422)
            self.assertEqual(data["message"], "Patient data failed validation.")
            self.assertIn("Patient code already exists", data["errors"]["demographics.patientCode"])

    def test_missing_patient_code_generates_server_side(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=valid_payload(patientCode=None),
            )
            self.assertEqual(status, 201)
            self.assertRegex(data["patient"]["patientCode"], r"^[A-Z0-9]{6}$")

    def test_dob_rejects_future_date(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload(dob=future_dob()))
            self.assertEqual(status, 422)
            self.assertIn("demographics.dob", data["errors"])

    def test_dob_rejects_patient_younger_than_one_year(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload(dob=dob_days_ago(364)))
            self.assertEqual(status, 422)
            self.assertIn("demographics.dob", data["errors"])

    def test_old_dob_is_accepted_and_age_is_computed(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload(dob=dob_for_age(111)))
            self.assertEqual(status, 201)
            self.assertEqual(data["patient"]["dob"], dob_for_age(111))
            self.assertEqual(data["patient"]["age"], 111)

    def test_invalid_sex_rejected(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/patients", method="POST", headers=csrf_headers(base, PSY_HEADER), body=valid_payload(sex="Other"))
            self.assertEqual(status, 422)
            self.assertIn("demographics.sex", data["errors"])

    def test_long_name_rejected(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=valid_payload(firstName="x" * 81),
            )
            self.assertEqual(status, 422)
            self.assertIn("demographics.firstName", data["errors"])

    def test_phone_normalization_strips_non_digits(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=valid_payload(patientCode="PHN001", phoneNumber="(555) 123-4567"),
            )
            self.assertEqual(status, 201)
            self.assertEqual(data["patient"]["phoneNumber"], "5551234567")

    def test_missing_required_clinical_intake_rejected(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=valid_payload(presentingComplaint="", provisionalDiagnosis=""),
            )
            self.assertEqual(status, 422)
            self.assertIn("clinical.presentingComplaint", data["errors"])
            self.assertIn("clinical.provisionalDiagnosis", data["errors"])

    def test_flat_payload_is_validated_with_section_error_keys(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=csrf_headers(base, PSY_HEADER),
                body=flat_payload(dob=future_dob(), provisionalDiagnosis=""),
            )
            self.assertEqual(status, 422)
            self.assertIn("demographics.dob", data["errors"])
            self.assertIn("clinical.provisionalDiagnosis", data["errors"])

    def test_static_assets_served_only_from_allowlist(self) -> None:
        with AddNewPatientServer() as base:
            self.assertEqual(request_json(base, "/")[0], 200)
            self.assertEqual(request_json(base, "/app.js")[0], 200)
            self.assertEqual(request_json(base, "/styles.css")[0], 200)

    def test_dashboard_embedded_module_path_serves_shell_and_assets(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/modules/add-new-patient")
            self.assertEqual(status, 200)
            self.assertIn('data-module="add-new-patient"', data["_raw"])

            self.assertEqual(request_json(base, "/modules/app.js")[0], 200)
            self.assertEqual(request_json(base, "/modules/styles.css")[0], 200)
            self.assertEqual(request_json(base, "/modules/add-new-patient/app.js")[0], 200)
            self.assertEqual(request_json(base, "/modules/add-new-patient/styles.css")[0], 200)

    def test_browser_uses_diagnosis_first_workflow(self) -> None:
        with AddNewPatientServer() as base:
            _, script = request_json(base, "/app.js")
            _, page = request_json(base, "/")
        source = script["_raw"]
        self.assertIn('/api/add-new-patient/v1/workflow-drafts', source)
        self.assertIn('/modules/diagnosis?workflow=', source)
        self.assertIn('draft.phase !== "patient-information"', source)
        self.assertIn('/finalize', source)
        self.assertIn('window.location.assign("/dashboard/")', source)
        self.assertNotIn("generateBrowserPatientCode", source)
        self.assertNotIn("regenerateCodeButton", page["_raw"])

    def test_private_paths_not_served(self) -> None:
        with AddNewPatientServer() as base:
            for path in [
                "/data/patients.json",
                "/server.py",
                "/schema/add-new-patient.schema.json",
                "/add_new_patient_backend/main.py",
                "/requirements.txt",
                "/modules/server.py",
                "/modules/add-new-patient/server.py",
            ]:
                with self.subTest(path=path):
                    status, _ = request_json(base, path)
                    self.assertEqual(status, 404)


class MigrationTest(unittest.TestCase):
    def test_legacy_records_are_backfilled_with_uuid_ids_and_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = os.path.join(tempdir, "legacy.sqlite3")
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE patients (
                      id TEXT PRIMARY KEY,
                      patient_code TEXT,
                      first_name TEXT,
                      last_name TEXT,
                      sex TEXT,
                      dob TEXT,
                      phone_number TEXT,
                      presenting_complaint TEXT,
                      provisional_diagnosis TEXT,
                      treatment_history TEXT,
                      allergies TEXT,
                      current_medications TEXT,
                      suicidality TEXT,
                      substance_use INTEGER,
                      created_by_user_id TEXT,
                      created_at TEXT,
                      updated_at TEXT
                    )
                    """
                )
                conn.executemany(
                    "INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        (
                            "legacy-patient-1",
                            "LEG001",
                            "Jane",
                            "Doe",
                            "Female",
                            "1986-01-01",
                            "5551234567",
                            "Low mood",
                            "F32.1",
                            '["CBT"]',
                            '["penicillin"]',
                            '["sertraline"]',
                            "ideation",
                            0,
                            "psy-1",
                            "2026-07-01T00:00:00Z",
                            "2026-07-01T00:00:00Z",
                        ),
                        (
                            "legacy-patient-2",
                            "LEG002",
                            "John",
                            "Doe",
                            "Male",
                            "1980-01-01",
                            None,
                            "Insomnia",
                            "G47.0",
                            "[]",
                            "[]",
                            '["melatonin"]',
                            "suicidality_none",
                            0,
                            "psy-1",
                            "2026-07-02T00:00:00Z",
                            "2026-07-02T00:00:00Z",
                        ),
                    ],
                )
                conn.commit()
            conn.close()

            from add_new_patient_backend.db import SQLiteAdapter
            from add_new_patient_backend.repository import PatientRepository

            adapter = SQLiteAdapter(db_path)
            report = adapter.initialize()
            self.assertEqual(report["migratedPatientCount"], 2)
            self.assertEqual(report["migratedEncounterCount"], 2)
            self.assertEqual(report["quarantinedCount"], 0)
            self.assertEqual(report["collisionRecordIds"], [])
            self.assertEqual(report["unresolvedRecordIds"], [])

            patients = PatientRepository(adapter).list_patients()
            self.assertEqual({patient["patientCode"] for patient in patients}, {"LEG001", "LEG002"})
            for patient in patients:
                UUID(patient["id"])
                UUID(patient["intakeId"])
            leg001 = next(patient for patient in patients if patient["patientCode"] == "LEG001")
            self.assertEqual(leg001["allergies"], ["penicillin"])
            self.assertEqual(leg001["currentMedications"], ["sertraline"])

    def test_code_keyed_collisions_and_unresolved_rows_are_quarantined(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = os.path.join(tempdir, "code-keyed.sqlite3")
            with sqlite3.connect(db_path) as conn:
                conn.executescript(
                    """
                    CREATE TABLE patients (
                      id TEXT PRIMARY KEY,
                      patient_code TEXT,
                      first_name TEXT,
                      last_name TEXT,
                      sex TEXT,
                      dob TEXT,
                      phone_number TEXT,
                      status TEXT,
                      resource_version INTEGER,
                      created_by_user_id TEXT,
                      created_at TEXT,
                      updated_at TEXT
                    );
                    CREATE TABLE patient_intake_records (
                      id TEXT PRIMARY KEY,
                      patient_id TEXT,
                      encounter_date TEXT,
                      presenting_complaint TEXT,
                      provisional_diagnosis TEXT,
                      treatment_history TEXT,
                      allergies_snapshot TEXT,
                      current_medications_snapshot TEXT,
                      suicidality TEXT,
                      substance_use INTEGER,
                      created_by_user_id TEXT,
                      created_at TEXT,
                      updated_at TEXT
                    );
                    """
                )
                conn.executemany(
                    "INSERT INTO patients VALUES (?, ?, 'Jane', 'Doe', 'Female', '1986-01-01', NULL, 'active', 1, 'psy-1', ?, ?)",
                    [
                        ("patient-good", "GOOD01", "2026-07-01T00:00:00Z", "2026-07-01T00:00:00Z"),
                        ("patient-collision-a", "DUP001", "2026-07-02T00:00:00Z", "2026-07-02T00:00:00Z"),
                        ("patient-collision-b", "dup001", "2026-07-03T00:00:00Z", "2026-07-03T00:00:00Z"),
                    ],
                )
                conn.executemany(
                    "INSERT INTO patient_intake_records VALUES (?, ?, ?, 'Complaint', 'Diagnosis', '[]', '[]', '[]', 'suicidality_none', 0, 'psy-1', ?, ?)",
                    [
                        ("encounter-good", "GOOD01", "2026-07-04T00:00:00Z", "2026-07-04T00:00:00Z", "2026-07-04T00:00:00Z"),
                        ("encounter-collision", "DUP001", "2026-07-05T00:00:00Z", "2026-07-05T00:00:00Z", "2026-07-05T00:00:00Z"),
                        ("encounter-unresolved", "MISSING1", "2026-07-06T00:00:00Z", "2026-07-06T00:00:00Z", "2026-07-06T00:00:00Z"),
                    ],
                )
                conn.commit()
            conn.close()

            from add_new_patient_backend.db import SQLiteAdapter
            from add_new_patient_backend.repository import PatientRepository

            adapter = SQLiteAdapter(db_path)
            report = adapter.initialize()
            self.assertEqual(report["migratedPatientCount"], 1)
            self.assertEqual(report["migratedEncounterCount"], 1)
            self.assertEqual(report["quarantinedCount"], 4)
            self.assertEqual(
                set(report["collisionRecordIds"]),
                {"patient-collision-a", "patient-collision-b", "encounter-collision"},
            )
            self.assertEqual(report["unresolvedRecordIds"], ["encounter-unresolved"])
            self.assertNotIn("GOOD01", json.dumps(report))
            self.assertNotIn("Jane", json.dumps(report))

            patients = PatientRepository(adapter).list_patients()
            self.assertEqual(len(patients), 1)
            UUID(patients[0]["id"])
            self.assertEqual(patients[0]["patientCode"], "GOOD01")
            UUID(patients[0]["intakeId"])

class AuthBoundaryTest(unittest.TestCase):
    def test_patients_endpoints_reject_unauthenticated(self) -> None:
        with AddNewPatientServer() as base:
            for path in ["/api/patients", "/api/patients/ANY"]:
                with self.subTest(path=path):
                    status, data = request_json(base, path)
                    self.assertEqual(status, 401)
                    self.assertEqual(data, {"error": "authentication_session_required"})
            status, data = request_json(
                base,
                "/api/patients",
                method="POST",
                headers=csrf_headers(base),
                body=valid_payload(),
            )
            self.assertEqual(status, 401)
            self.assertEqual(data, {"error": "authentication_session_required"})

    def test_csrf_endpoint_issues_cookie_and_token(self) -> None:
        with AddNewPatientServer() as base:
            headers = csrf_headers(base, PSY_HEADER)
            self.assertIn("add_new_patient_csrf=", headers["cookie"])
            self.assertTrue(headers["x-csrf-token"])

    def test_write_rejects_missing_csrf(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/patients", method="POST", headers=PSY_HEADER, body=valid_payload())
            self.assertEqual(status, 403)
            self.assertEqual(data, {"error": "csrf_token_invalid"})

    def test_write_rejects_mismatched_csrf(self) -> None:
        with AddNewPatientServer() as base:
            headers = csrf_headers(base, PSY_HEADER)
            headers["x-csrf-token"] = "wrong-token"
            status, data = request_json(base, "/api/patients", method="POST", headers=headers, body=valid_payload())
            self.assertEqual(status, 403)
            self.assertEqual(data, {"error": "csrf_token_invalid"})

    def test_write_rejects_tampered_csrf_cookie(self) -> None:
        with AddNewPatientServer() as base:
            headers = csrf_headers(base, PSY_HEADER)
            headers["cookie"] = f"add_new_patient_csrf={headers['x-csrf-token']}.bad-signature"
            status, data = request_json(base, "/api/patients", method="POST", headers=headers, body=valid_payload())
            self.assertEqual(status, 403)
            self.assertEqual(data, {"error": "csrf_token_invalid"})

    def test_mock_auth_session_resolves_demo_user(self) -> None:
        with AddNewPatientServer() as base:
            status, data = request_json(base, "/api/auth/session", headers=PSY_HEADER)
            self.assertEqual(status, 200)
            self.assertTrue(data["authenticated"])
            self.assertEqual(data["user"]["id"], "psy-1")
            self.assertEqual(data["user"]["roles"], ["psychiatrist"])

    def test_mock_auth_session_404_when_mock_disabled(self) -> None:
        with MockAuthenticationServer() as mock_auth:
            with AddNewPatientServer(auth_session_url=mock_auth.url) as base:
                status, data = request_json(base, "/api/auth/session")
                self.assertEqual(status, 404)
                self.assertEqual(data, {"error": "not_found"})

    def test_real_auth_session_returns_401_when_unknown_session(self) -> None:
        with MockAuthenticationServer() as mock_auth:
            with AddNewPatientServer(auth_session_url=mock_auth.url) as base:
                status, data = request_json(base, "/api/patients", headers={"cookie": "insight_session=unknown"})
                self.assertEqual(status, 401)
                self.assertEqual(data, {"error": "authentication_session_required"})

    def test_real_auth_session_accepts_verified_psychiatrist(self) -> None:
        with MockAuthenticationServer() as mock_auth:
            mock_auth.set_payload("auth-1", auth_payload())
            with AddNewPatientServer(auth_session_url=mock_auth.url) as base:
                status, data = request_json(
                    base,
                    "/api/patients",
                    method="POST",
                    headers=csrf_headers(base, {"cookie": "insight_session=auth-1"}),
                    body=valid_payload(),
                )
                self.assertEqual(status, 201)
                self.assertEqual(data["patient"]["patientCode"], "TEST01")
                self.assertEqual(mock_auth.requests[0]["path"], "/api/auth/session")
                self.assertIn("insight_session=auth-1", mock_auth.requests[0]["cookie"])

    def test_real_auth_session_rejects_admin_role(self) -> None:
        with MockAuthenticationServer() as mock_auth:
            mock_auth.set_payload(
                "admin-sess",
                auth_payload(user={"id": "admin-1", "roles": ["ADMIN"], "displayName": "Admin"}),
            )
            with AddNewPatientServer(auth_session_url=mock_auth.url) as base:
                status, data = request_json(
                    base,
                    "/api/patients",
                    method="POST",
                    headers=csrf_headers(base, {"cookie": "insight_session=admin-sess"}),
                    body=valid_payload(),
                )
                self.assertEqual(status, 401)
                self.assertEqual(data, {"error": "authentication_session_required"})

    def test_real_auth_session_accepts_admin_on_read_endpoints(self) -> None:
        with MockAuthenticationServer() as mock_auth:
            mock_auth.set_payload(
                "admin-sess",
                auth_payload(user={"id": "admin-1", "roles": ["ADMIN"], "displayName": "Admin"}),
            )
            with AddNewPatientServer(auth_session_url=mock_auth.url) as base:
                status, data = request_json(base, "/api/patients", headers={"cookie": "insight_session=admin-sess"})
                self.assertEqual(status, 200)
                self.assertEqual(data, {"schemaVersion": "1.0.0", "patients": []})

                status, data = request_json(base, "/api/patients/MISSING", headers={"cookie": "insight_session=admin-sess"})
                self.assertEqual(status, 404)
                self.assertEqual(data, {"message": "Patient was not found."})

    def test_disclaimer_status_does_not_block_authenticated_session(self) -> None:
        with MockAuthenticationServer() as mock_auth:
            mock_auth.set_payload("auth-blocked", auth_payload(gates={"disclaimerAccepted": False, "passwordChangeRequired": False}))
            with AddNewPatientServer(auth_session_url=mock_auth.url) as base:
                status, data = request_json(
                    base,
                    "/api/patients",
                    headers={"cookie": "insight_session=auth-blocked"},
                )
                self.assertEqual(status, 200)
                self.assertEqual(data, {"schemaVersion": "1.0.0", "patients": []})

    def test_auth_session_unavailable_returns_502(self) -> None:
        # ponytail: point at a port nobody owns -> connection refused -> AuthSessionError -> 502
        with AddNewPatientServer(auth_session_url="http://127.0.0.1:1/api/auth/session") as base:
            status, data = request_json(base, "/api/patients", headers={"cookie": "insight_session=auth-1"})
            self.assertEqual(status, 502)
            self.assertEqual(data["error"], "authentication_session_unavailable")


class ConcurrencyTest(unittest.TestCase):
    def test_concurrent_patient_creation_preserves_all(self) -> None:
        import concurrent.futures

        with AddNewPatientServer() as base:
            codes = [f"C{i:05d}" for i in range(10)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
                futures = [
                    pool.submit(
                        request_json,
                        base,
                        "/api/patients",
                        "POST",
                        csrf_headers(base, PSY_HEADER),
                        valid_payload(patientCode=code),
                    )
                    for code in codes
                ]
                results = [future.result() for future in futures]
            self.assertEqual([status for status, _ in results], [201] * 10)
            _, data = request_json(base, "/api/patients", headers=PSY_HEADER)
            stored = sorted(patient["patientCode"] for patient in data["patients"])
            self.assertEqual(stored, sorted(codes))


if __name__ == "__main__":
    unittest.main()
