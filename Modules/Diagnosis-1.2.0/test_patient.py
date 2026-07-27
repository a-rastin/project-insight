"""Patient-identity-adapter tests for the diagnosis API.

Strategy:
    - Stand up two tiny in-process HTTP servers: a fake Insight auth
      service (always psychiatrist — the patient adapter is the subject
      here, not auth) and a fake "Add New Patient" registry at
      ``GET /api/patients/lookup?code=...`` that maps a code to a canonical
      INSIGHT patient.
    - Force ``DIAGNOSIS_PATIENT_LOOKUP=1`` so the adapter enforces real
      lookup, point ``diagnosis.patient.PATIENT_BASE_URL`` at the fake
      registry, and assert the write routes (init + put) bind the session
      to the canonical ``patient.id`` — NOT the free-text ``code``.
    - Unknown code (registry 404), missing canonical id, empty code, and
      registry-down all map to a clean 422 / 400 — never a stack trace and
      never a row whose ``patient_id`` collapses back to the free-text
      ``code``.

Run: ``python -m test_patient`` — no test framework, ponytail style.
"""
from __future__ import annotations

import json
import hmac
from hashlib import sha256
import os
import socket
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Make the diagnosis package importable regardless of cwd.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

# Force both bypasses off — we want to exercise the real dependency.
os.environ.pop("DIAGNOSIS_AUTH_BYPASS", None)
from test_support import TEST_DB_PATH
os.environ["DIAGNOSIS_DB_PATH"] = TEST_DB_PATH
os.environ["DIAGNOSIS_PATIENT_LOOKUP"] = "1"
os.environ["WORKFLOW_SERVICE_SECRET"] = "workflow-test-secret"

from fastapi.testclient import TestClient

from diagnosis import auth as diag_auth
from diagnosis import diagnosis_api as diag_api
from diagnosis import patient as diag_patient
from diagnosis.app import app

diag_api.clinical_feature_status = lambda: {"available": True}


# ---------------------------------------------------------------------------
# Fake auth service — psychiatrist regardless of who's calling. Same shape
# as test_csrf.py's fake auth; the patient adapter is the subject here.

PSYCHIATRIST = {
    "schemaVersion": "1.0.0",
    "authenticated": True,
    "user": {"id": "u-psy-1", "roles": ["psychiatrist"]},
    "session": {"id": "s-1"},
    "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
}


class _AuthHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def do_GET(self):  # noqa: N802
        body = json.dumps(PSYCHIATRIST).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# Fake "Add New Patient" registry. Mirrors the contract documented in
# diagnosis/patient.py: GET /api/patients/lookup?code=<code> returns
# {"id", "patient_code", "display_name"} or 404 for an unknown code.
# A special code triggers a malformed-JSON body to exercise the parse
# fault path; another triggers a 500 to exercise the transport-mapping path.

_PATIENTS = {
    "P-0042-A": {"id": "insight-pid-0042", "patient_code": "P-0042-A",
                  "display_name": "Ada Lovelace"},
    "P-0007-B": {"id": "insight-pid-0007", "patient_code": "P-0007-B",
                  "display_name": None},
    "P-0099-Z": {"id": "insight-pid-0099", "patient_code": "P-0099-Z",
                   "display_name": None},
}
_WORKFLOW_REQUESTS: list[dict] = []


class _PatientHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def do_GET(self):  # noqa: N802
        if not self.path.startswith("/api/patients/lookup"):
            self.send_response(404)
            self.end_headers()
            return
        qs = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        code = (qs.get("code") or [""])[0]

        if code == "__badjson__":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"{not valid json")
            return
        if code == "__servererr__":
            self.send_response(500)
            self.end_headers()
            return
        if code == "__noid__":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            body = json.dumps({"patient_code": code, "display_name": "no id here"}).encode("utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        rec = _PATIENTS.get(code)
        if rec is None:
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps(rec).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):  # noqa: N802
        if not self.path.startswith("/internal/workflow-drafts/"):
            self.send_response(404)
            self.end_headers()
            return
        draft_id = self.path.split("/")[3]
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
        expected = hmac.new(
            b"workflow-test-secret",
            f"{draft_id}:{payload['patientCode']}:{payload['decision']}".encode(),
            sha256,
        ).hexdigest()
        if not hmac.compare_digest(self.headers.get("X-Workflow-Signature", ""), expected):
            self.send_response(403)
            self.end_headers()
            return
        _WORKFLOW_REQUESTS.append({"draftId": draft_id, **payload})
        body = json.dumps({"workflowDraft": {"phase": "patient-information"}}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _start_fake(handler) -> tuple[HTTPServer, int]:
    port = _free_port()
    httpd = HTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, port


# ---------------------------------------------------------------------------
# Tests


def _arm_with_csrf(c: TestClient) -> None:
    r = c.get("/diagnosis/_csrf")
    assert r.status_code == 200, ("csrf mint failed", r.status_code, r.text)
    token = r.json()["token"]
    c.cookies.set("csrf", token)
    c.headers["X-CSRF-Token"] = token


def _client(auth_port: int, patient_port: int) -> TestClient:
    diag_auth.AUTH_BASE_URL = f"http://127.0.0.1:{auth_port}"
    diag_patient.PATIENT_BASE_URL = f"http://127.0.0.1:{patient_port}"
    diag_patient.WORKFLOW_SERVICE_URL = diag_patient.PATIENT_BASE_URL
    return TestClient(app, cookies={"insight_session": "test-psychiatrist"})


def test_init_binds_canonical_patient_id(auth_port, patient_port):
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    r = c.post("/diagnosis/P-0042-A/init")
    assert r.status_code == 200, (r.status_code, r.text)
    assert r.json()["created"] is True, r.text
    assert r.json()["patient_id"] == "insight-pid-0042", r.text
    # The session row's patient_id is the canonical id, NOT the free-text code.
    r = c.get("/diagnosis/P-0042-A")
    assert r.json()["patient_id"] == "insight-pid-0042", r.text
    assert r.json()["code"] == "P-0042-A", r.text


def test_put_binds_canonical_patient_id(auth_port, patient_port):
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    r = c.put(
        "/diagnosis/P-0007-B",
        json={"checked": ["A1", "A5", "A6", "B1", "C1", "D1"], "decision": "confirmed"},
    )
    assert r.status_code == 200, (r.status_code, r.text)
    assert r.json()["patient_id"] == "insight-pid-0007", r.text
    # display_name=None must round-trip without breaking the lookup.
    assert r.json()["evaluation"]["met"] is True, r.text


def test_persisted_decision_advances_signed_workflow(auth_port, patient_port):
    _WORKFLOW_REQUESTS.clear()
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    r = c.put(
        "/diagnosis/P-0007-B",
        json={"checked": ["A1", "A5", "A6", "B1", "C1", "D1"], "decision": "confirmed", "workflowId": "draft-1"},
    )
    assert r.status_code == 200, (r.status_code, r.text)
    assert _WORKFLOW_REQUESTS == [{"draftId": "draft-1", "patientCode": "P-0007-B", "decision": "confirmed"}], _WORKFLOW_REQUESTS


def test_workflow_failure_does_not_persist_decision(auth_port, patient_port):
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    diag_patient.WORKFLOW_SERVICE_SECRET = ""
    try:
        r = c.put(
            "/diagnosis/P-0099-Z",
            json={"checked": ["A1"], "decision": "definite", "workflowId": "draft-unavailable"},
        )
        assert r.status_code == 503, (r.status_code, r.text)
        assert diag_api.store.get("P-0099-Z") is None
    finally:
        diag_patient.WORKFLOW_SERVICE_SECRET = "workflow-test-secret"


def test_unknown_code_returns_422_not_404(auth_port, patient_port):
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    r = c.post("/diagnosis/__nope__/init")
    assert r.status_code == 422, (r.status_code, r.text)
    assert "Unknown patient code" in r.text, r.text


def test_registry_404_on_put_returns_422(auth_port, patient_port):
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    r = c.put("/diagnosis/__nope__", json={"checked": ["A1"], "decision": None})
    assert r.status_code == 422, (r.status_code, r.text)


def test_empty_code_returns_400(auth_port, patient_port):
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    r = c.post("/diagnosis/%20/init")
    assert r.status_code == 400, (r.status_code, r.text)
    assert "Patient code required" in r.text, r.text


def test_missing_canonical_id_returns_422(auth_port, patient_port):
    # Registry returns 200 but no "id" — the adapter must fail closed.
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    r = c.post("/diagnosis/__noid__/init")
    assert r.status_code == 422, (r.status_code, r.text)
    assert "no canonical id" in r.text, r.text


def test_registry_bad_json_returns_422(auth_port, patient_port):
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    r = c.post("/diagnosis/__badjson__/init")
    assert r.status_code == 422, (r.status_code, r.text)
    assert "registry unavailable" in r.text, r.text


def test_registry_500_returns_422(auth_port, patient_port):
    # Any non-404 HTTP error collapses to a 422 without leaking the status.
    c = _client(auth_port, patient_port)
    _arm_with_csrf(c)
    r = c.post("/diagnosis/__servererr__/init")
    assert r.status_code == 422, (r.status_code, r.text)
    assert "registry unavailable" in r.text, r.text


def test_registry_down_returns_422():
    # Bind the adapter at a port nobody is listening on, then make a request.
    dead_port = _free_port()
    diag_patient.PATIENT_BASE_URL = f"http://127.0.0.1:{dead_port}"

    # Auth still needs a live fake — start one.
    auth_httpd, auth_port = _start_fake(_AuthHandler)
    try:
        c = TestClient(app, cookies={"insight_session": "test-psychiatrist"})
        _arm_with_csrf(c)
        r = c.post("/diagnosis/P-0042-A/init")
        assert r.status_code == 422, (r.status_code, r.text)
        assert "registry unavailable" in r.text, r.text
    finally:
        auth_httpd.shutdown()


def test_lookup_disabled_env_falls_back_to_free_text(auth_port, patient_port):
    # When DIAGNOSIS_PATIENT_LOOKUP is not "1", the adapter must NEVER call
    # the registry — point it at a port that would hang if contacted, and
    # confirm a write still succeeds with patient_id == code.
    diag_patient.PATIENT_BASE_URL = "http://127.0.0.1:1"  # unroutable
    os.environ.pop("DIAGNOSIS_PATIENT_LOOKUP", None)
    try:
        c = TestClient(app, cookies={"insight_session": "test-psychiatrist"})
        _arm_with_csrf(c)
        r = c.post("/diagnosis/__free__/init")
        assert r.status_code == 200, (r.status_code, r.text)
        assert r.json()["patient_id"] == "__free__", r.text
        r = c.put("/diagnosis/__free__", json={"checked": ["A1"], "decision": None})
        assert r.status_code == 200, (r.status_code, r.text)
        assert r.json()["patient_id"] == "__free__", r.text
    finally:
        os.environ["DIAGNOSIS_PATIENT_LOOKUP"] = "1"


def main() -> None:
    auth_httpd, auth_port = _start_fake(_AuthHandler)
    patient_httpd, patient_port = _start_fake(_PatientHandler)

    failures = []
    cases = [
        ("test_init_binds_canonical_patient_id",
         lambda: test_init_binds_canonical_patient_id(auth_port, patient_port)),
        ("test_put_binds_canonical_patient_id",
         lambda: test_put_binds_canonical_patient_id(auth_port, patient_port)),
        ("test_persisted_decision_advances_signed_workflow",
         lambda: test_persisted_decision_advances_signed_workflow(auth_port, patient_port)),
        ("test_workflow_failure_does_not_persist_decision",
         lambda: test_workflow_failure_does_not_persist_decision(auth_port, patient_port)),
        ("test_unknown_code_returns_422_not_404",
         lambda: test_unknown_code_returns_422_not_404(auth_port, patient_port)),
        ("test_registry_404_on_put_returns_422",
         lambda: test_registry_404_on_put_returns_422(auth_port, patient_port)),
        ("test_empty_code_returns_400",
         lambda: test_empty_code_returns_400(auth_port, patient_port)),
        ("test_missing_canonical_id_returns_422",
         lambda: test_missing_canonical_id_returns_422(auth_port, patient_port)),
        ("test_registry_bad_json_returns_422",
         lambda: test_registry_bad_json_returns_422(auth_port, patient_port)),
        ("test_registry_500_returns_422",
         lambda: test_registry_500_returns_422(auth_port, patient_port)),
        ("test_registry_down_returns_422",
         test_registry_down_returns_422),
        ("test_lookup_disabled_env_falls_back_to_free_text",
         lambda: test_lookup_disabled_env_falls_back_to_free_text(auth_port, patient_port)),
    ]
    for name, fn in cases:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failures.append((name, repr(e)))
            print(f"FAIL  {name}: {e}")

    patient_httpd.shutdown()
    auth_httpd.shutdown()
    from diagnosis.api import store as api_store
    api_store.reset()

    # Restore the opt-in env for downstream tests in the same process.
    os.environ.pop("DIAGNOSIS_PATIENT_LOOKUP", None)

    if failures:
        print(f"\n{len(failures)}/{len(cases)} FAILED")
        sys.exit(1)
    print(f"\nOK: {len(cases)}/{len(cases)} patient tests passed")


if __name__ == "__main__":
    main()
