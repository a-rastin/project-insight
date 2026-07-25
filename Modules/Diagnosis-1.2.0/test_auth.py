"""Auth-enforcement tests for the diagnosis API.

Strategy:
    - Stand up a tiny in-process HTTP server that mimics the Insight auth
      service at ``GET /api/auth/session``. The server inspects a query
      parameter ``as`` on the path and returns a JSON body shaped per
      ``auth._build_session``. That lets each test case pick a role
      without dragging in real auth infrastructure.
    - Point ``diagnosis.auth.AUTH_BASE_URL`` at the test server, send a
      ``Cookie`` header on each request, and assert the expected status
      code from each protected route.
    - The diagnosis module catches every protected path with a 401 when
      no session header is present, 403 when the role isn't allowed,
      200 when it's a matching role. The unauthenticated checks are
      independent of the test server (they fail before it talks to us).

Run: ``python -m test_auth`` — no test framework, ponytail style.
"""
from __future__ import annotations

import json
import os
import socket
import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Make the diagnosis package importable regardless of cwd.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

# Force the auth bypass off — we want to exercise the real dependency.
os.environ.pop("DIAGNOSIS_AUTH_BYPASS", None)
from test_support import TEST_DB_PATH
os.environ["DIAGNOSIS_DB_PATH"] = TEST_DB_PATH

from fastapi.testclient import TestClient

from diagnosis import auth as diag_auth
from diagnosis import diagnosis_api as diag_api
from diagnosis.app import app

# Existing authorization tests exercise a released clinical workflow. Stub only
# feature availability; no test supplies a clinical coding identifier.
diag_api.clinical_feature_status = lambda: {"available": True}


# ---------------------------------------------------------------------------
# CSRF helper — writes (init + put) are CSRF-gated. Mint a token once per
# client via the public /diagnosis/_csrf route and stamp both the cookie
# the server expects and the X-CSRF-Token header every write carries.

def _arm_with_csrf(c: TestClient) -> None:
    """Fetch /diagnosis/_csrf once so the client has a matching cookie,
    then capture the same token to replay as the X-CSRF-Token header on
    subsequent writes."""
    r = c.get("/diagnosis/_csrf")
    assert r.status_code == 200, ("csrf mint failed", r.status_code, r.text)
    token = r.json()["token"]
    c.cookies.set("csrf", token)  # explicit in case the Set-Cookie was filtered
    c.headers["X-CSRF-Token"] = token


def _write_headers() -> dict[str, str]:
    """Header dict for inline writes in the auth tests. The token itself
    is stored on the TestClient by ``_arm_with_csrf`` and replayed on
    every request via c.headers."""
    return {}  # headers live on the client; kept here for symmetry


# ---------------------------------------------------------------------------
# Fake auth service

SCENARIOS = {
    # path query 'as'    ->   payload
    "psychiatrist": {
        "schemaVersion": "1.0.0",
        "authenticated": True,
        "user": {"id": "u-psy-1", "username": "psychiatrist", "roles": ["psychiatrist"], "displayName": "Clinician"},
        "session": {"id": "s-1", "expiresAt": "2099-01-01T00:00:00Z"},
        "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
    },
    "admin": {
        "schemaVersion": "1.0.0",
        "authenticated": True,
        "user": {"id": "u-adm-1", "username": "admin", "roles": ["admin"], "displayName": "Admin"},
        "session": {"id": "s-2", "expiresAt": "2099-01-01T00:00:00Z"},
        "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
    },
    "nora": {  # neither role
        "schemaVersion": "1.0.0",
        "authenticated": True,
        "user": {"id": "u-other", "username": "nora", "roles": ["nurse"], "displayName": "Nora"},
        "session": {"id": "s-3", "expiresAt": "2099-01-01T00:00:00Z"},
        "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
    },
    "anon": {"schemaVersion": "1.0.0", "authenticated": False, "user": None, "session": None, "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False}},
}


class _Handler(BaseHTTPRequestHandler):
    # Silence stdout noise.
    def log_message(self, *_args):
        return

    def do_GET(self):  # noqa: N802 (BaseHTTPRequestHandler API)
        # /api/auth/session
        if not self.path.startswith("/api/auth/session"):
            self.send_response(404)
            self.end_headers()
            return
        # Real auth service reads the Cookie header to resolve the
        # session. Mirror that here: cookie value == scenario name,
        # absent cookie -> anon.
        scenario = "anon"
        cookie_header = self.headers.get("Cookie", "")
        for part in cookie_header.split(";"):
            k, _, v = part.strip().partition("=")
            if k == "insight_session":
                # cookie value is "test-<scenario>"
                v = v.strip()
                if v.startswith("test-"):
                    scenario = v[len("test-"):]
                break
        body = json.dumps(SCENARIOS.get(scenario, SCENARIOS["anon"])).encode("utf-8")
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


def _start_fake_auth() -> tuple[HTTPServer, int]:
    port = _free_port()
    httpd = HTTPServer(("127.0.0.1", port), _Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, port


# ---------------------------------------------------------------------------
# Tests


def _cookie_for(scenario: str) -> str:
    # We don't send a real session cookie — just a marker the fake server
    # could care about. The fake server ignores the cookie and reads ?as=.
    return f"insight_session=test-{scenario}"


def _client_for(scenario: str | None, port: int) -> TestClient:
    """TestClient + rebind auth base URL. The rebind is process-global,
    but each call rewrites it before the next request, so isolation holds.
    """
    base = f"http://127.0.0.1:{port}"
    diag_auth.AUTH_BASE_URL = base
    if scenario is None:
        return TestClient(app)
    return TestClient(app, cookies={"insight_session": f"test-{scenario}"})


def _exercise(c: TestClient, code: str = "__auth_test__") -> None:
    """Touch every protected path. Returns Status enum via raise if any
    route returns the wrong code; the caller asserts."""
    # Writes (init + put) are CSRF-gated; arm the client first.
    _arm_with_csrf(c)
    # init
    r = c.post(f"/diagnosis/{code}/init")
    assert r.status_code == 200, (r.status_code, r.text)
    # _meta read
    r = c.get("/diagnosis/_meta")
    assert r.status_code == 200 and len(r.json()["criteria"]) == 9, r.text
    # get
    r = c.get(f"/diagnosis/{code}")
    assert r.status_code == 200, (r.status_code, r.text)
    # put
    r = c.put(
        f"/diagnosis/{code}",
        json={"checked": ["A1", "A5", "A6", "B1", "C1", "D1"], "decision": "confirmed"},
    )
    assert r.status_code == 200, (r.status_code, r.text)
    # html shell
    r = c.get("/")
    assert r.status_code == 200, (r.status_code, r.text)


def test_no_cookie_returns_401_on_every_protected_path(port):
    c = _client_for(None, port)
    for path, method in [
        ("/diagnosis/__x__/init", "POST"),
        ("/diagnosis/__x__", "GET"),
        ("/diagnosis/__x__", "PUT"),
        ("/diagnosis/_meta", "GET"),
        ("/", "GET"),
    ]:
        r = c.request(method, path, json={"checked": [], "decision": None})
        assert r.status_code == 401, (method, path, r.status_code, r.text)


def test_unauthenticated_payload_returns_401(port):
    # Cookies present but the fake auth service decides 'anon'.
    c = _client_for("anon", port)
    for path, method in [
        ("/diagnosis/__x__/init", "POST"),
        ("/diagnosis/__x__", "GET"),
        ("/diagnosis/__x__", "PUT"),
        ("/diagnosis/_meta", "GET"),
        ("/", "GET"),
    ]:
        r = c.request(method, path, json={"checked": [], "decision": None})
        assert r.status_code == 401, (method, path, r.status_code, r.text)


def test_nurse_role_is_403_on_every_protected_path(port):
    c = _client_for("nora", port)
    for path, method in [
        ("/diagnosis/__x__/init", "POST"),
        ("/diagnosis/__x__", "GET"),
        ("/diagnosis/__x__", "PUT"),
        ("/diagnosis/_meta", "GET"),
        ("/", "GET"),
    ]:
        r = c.request(method, path, json={"checked": [], "decision": None})
        assert r.status_code == 403, (method, path, r.status_code, r.text)


def test_psychiatrist_can_read_and_write(port):
    c = _client_for("psychiatrist", port)
    _exercise(c)


def test_psychiatrist_is_told_when_clinical_feature_is_disabled(port):
    c = _client_for("psychiatrist", port)
    _arm_with_csrf(c)
    saved = diag_api.clinical_feature_status
    diag_api.clinical_feature_status = lambda: {"available": False, "reason": "clinical_scope_unresolved"}
    try:
        r = c.post("/diagnosis/__feature_disabled__/init")
        assert r.status_code == 409, (r.status_code, r.text)
        assert r.json()["detail"] == "Clinical diagnosis feature disabled: coding approval pending", r.text
    finally:
        diag_api.clinical_feature_status = saved


def test_admin_can_read_but_not_write(port):
    c = _client_for("admin", port)
    code = "__admin_test__"
    # Reads: _meta, get on a code we just init'd as admin... init is a write.
    # So test the read paths only, against a code we seed another way:
    # we cannot seed without a write-capable session. Instead, init must
    # already exist *before* this test, or we init as psychiatrist first
    # to set up the row, then a second TestClient as admin reads it.
    # Simplest: the admin role test asserts *writes* are 403 and reads
    # against a non-existent code are 403 (we don't have a write path to
    # seed). Use /diagnosis/_meta and / as reads — those are protected
    # by read-or-write policy.
    r = c.get("/diagnosis/_meta"); assert r.status_code == 200, r.text
    r = c.get("/"); assert r.status_code == 200, r.text
    # Writes must be 403
    r = c.post(f"/diagnosis/{code}/init")
    assert r.status_code == 403, (r.status_code, r.text)
    r = c.put(f"/diagnosis/{code}", json={"checked": ["A1"], "decision": None})
    assert r.status_code == 403, (r.status_code, r.text)


def test_admin_can_read_existing_session_after_psychiatrist_seeds_it(port):
    # Seed as psychiatrist, then read as admin.
    c_psy = _client_for("psychiatrist", port)
    _arm_with_csrf(c_psy)
    code = "__handoff__"
    r = c_psy.post(f"/diagnosis/{code}/init"); assert r.status_code == 200, r.text
    r = c_psy.put(
        f"/diagnosis/{code}",
        json={"checked": ["A1", "A5", "A6", "B1", "C1", "D1"], "decision": "confirmed"},
    )
    assert r.status_code == 200, r.text

    c_adm = _client_for("admin", port)
    r = c_adm.get(f"/diagnosis/{code}")
    assert r.status_code == 200 and r.json()["decision"] == "confirmed", r.text


def test_auth_service_down_returns_401():
    # Spin up a separate fake auth server for this test, shut it down,
    # then issue the request. We rebind AUTH_BASE_URL at the start so
    # the dependency points at the dead server. The dependency should
    # map the transport failure to a 401.
    local_httpd, local_port = _start_fake_auth()
    diag_auth.AUTH_BASE_URL = f"http://127.0.0.1:{local_port}"
    local_httpd.shutdown()
    c = TestClient(app, cookies={"insight_session": "test-psychiatrist"})
    r = c.get("/diagnosis/_meta")
    assert r.status_code == 401, (r.status_code, r.text)


def test_legacy_flat_payload_is_rejected():
    import pytest
    from diagnosis.auth import _build_session
    with pytest.raises(Exception):
        _build_session({"authenticated": True, "user_id": "u-1", "roles": ["psychiatrist"], "session_id": "s-1"})

def main() -> None:
    _global_httpd, _global_port = _start_fake_auth()

    failures = []
    cases = [
        ("test_no_cookie_returns_401_on_every_protected_path",
         lambda: test_no_cookie_returns_401_on_every_protected_path(_global_port)),
        ("test_unauthenticated_payload_returns_401",
         lambda: test_unauthenticated_payload_returns_401(_global_port)),
        ("test_nurse_role_is_403_on_every_protected_path",
         lambda: test_nurse_role_is_403_on_every_protected_path(_global_port)),
        ("test_psychiatrist_can_read_and_write",
         lambda: test_psychiatrist_can_read_and_write(_global_port)),
        ("test_psychiatrist_is_told_when_clinical_feature_is_disabled",
         lambda: test_psychiatrist_is_told_when_clinical_feature_is_disabled(_global_port)),
        ("test_admin_can_read_but_not_write",
         lambda: test_admin_can_read_but_not_write(_global_port)),
        ("test_admin_can_read_existing_session_after_psychiatrist_seeds_it",
         lambda: test_admin_can_read_existing_session_after_psychiatrist_seeds_it(_global_port)),
        ("test_auth_service_down_returns_401",
         test_auth_service_down_returns_401),
    ]
    for name, fn in cases:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failures.append((name, repr(e)))
            print(f"FAIL  {name}: {e}")

    _global_httpd.shutdown()
    from diagnosis.api import store as api_store
    api_store.reset()

    if failures:
        print(f"\n{len(failures)}/{len(cases)} FAILED")
        sys.exit(1)
    print(f"\nOK: {len(cases)}/{len(cases)} auth tests passed")


if __name__ == "__main__":
    main()
