"""CSRF tests for the diagnosis write routes.

Mirrors the ``test_auth.py`` strategy — stand up a tiny fake auth service
that returns ``psychiatrist`` for every cookie-bearing request, so the
role dependency passes and we can isolate the CSRF gate. The CSRF
secret is pinned via ``csrf.reset_secret_for_tests`` so we can mint
matching tokens for the happy path.

Run: ``python -m test_csrf`` — no test framework, ponytail style.
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

# Force the auth bypass off — we want to exercise the real auth dependency.
os.environ.pop("DIAGNOSIS_AUTH_BYPASS", None)
from test_support import TEST_DB_PATH
os.environ["DIAGNOSIS_DB_PATH"] = TEST_DB_PATH

from fastapi.testclient import TestClient

from diagnosis import auth as diag_auth
from diagnosis import csrf as diag_csrf
from diagnosis.app import app


# ---------------------------------------------------------------------------
# Fake auth service — psychiatrist regardless of who's calling.

PSYCHIATRIST = {
    "schemaVersion": "1.0.0",
    "authenticated": True,
    "user": {"id": "u-psy-1", "roles": ["psychiatrist"]},
    "session": {"id": "s-1"},
    "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
}


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def do_GET(self):  # noqa: N802
        body = json.dumps(PSYCHIATRIST).encode("utf-8")
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


def _client(port: int) -> TestClient:
    """A TestClient with a psychiatrist cookie and the live auth base URL."""
    diag_auth.AUTH_BASE_URL = f"http://127.0.0.1:{port}"
    return TestClient(app, cookies={"insight_session": "test-psychiatrist"})


def _mint_valid_token() -> str:
    """Mint a token signed with the test secret. Mirrors ``csrf.mint``
    but does not use the env bypass — production callers must go through
    the server route."""
    import secrets
    raw = secrets.token_hex(16)
    # Reproduce the server's signing using the pinned secret.
    import hmac, hashlib
    sig = hmac.new(diag_csrf._SECRET, raw.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def _mint_bad_token() -> str:
    """A token with the right shape but a wrong signature."""
    raw = "0" * 32
    return f"{raw}.deadbeef"


def test_missing_csrf_blocks_put(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    r = c.put("/diagnosis/__x__", json={"checked": [], "decision": None})
    assert r.status_code == 403, (r.status_code, r.text)
    assert "CSRF" in r.text, r.text


def test_missing_csrf_blocks_init(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    r = c.post("/diagnosis/__x__/init")
    assert r.status_code == 403, (r.status_code, r.text)
    assert "CSRF" in r.text, r.text


def test_header_only_blocked(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    token = _mint_valid_token()
    # header present, NO cookie set by us; expect mismatch.
    r = c.put(
        "/diagnosis/__x__",
        json={"checked": [], "decision": None},
        headers={"X-CSRF-Token": token},
    )
    assert r.status_code == 403, (r.status_code, r.text)


def test_cookie_only_blocked(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    token = _mint_valid_token()
    c.cookies.set("csrf", token)
    r = c.put("/diagnosis/__x__", json={"checked": [], "decision": None})
    assert r.status_code == 403, (r.status_code, r.text)


def test_cookie_header_mismatch_blocked(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    cookie_tok = _mint_valid_token()
    header_tok = _mint_valid_token()  # different valid token
    c.cookies.set("csrf", cookie_tok)
    r = c.put(
        "/diagnosis/__x__",
        json={"checked": [], "decision": None},
        headers={"X-CSRF-Token": header_tok},
    )
    assert r.status_code == 403, (r.status_code, r.text)


def test_bad_signature_blocked(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    bad = _mint_bad_token()
    c.cookies.set("csrf", bad)
    r = c.put(
        "/diagnosis/__x__",
        json={"checked": [], "decision": None},
        headers={"X-CSRF-Token": bad},
    )
    assert r.status_code == 403, (r.status_code, r.text)


def test_valid_token_allows_init(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    token = _mint_valid_token()
    c.cookies.set("csrf", token)
    r = c.post(
        "/diagnosis/__csrf_ok__/init",
        headers={"X-CSRF-Token": token},
    )
    assert r.status_code == 200, (r.status_code, r.text)
    assert r.json()["created"] is True, r.text


def test_valid_token_allows_put(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    token = _mint_valid_token()
    c.cookies.set("csrf", token)
    # Seed first (init is also CSRF-protected; reuse the same token).
    r = c.post(
        "/diagnosis/__csrf_put__/init",
        headers={"X-CSRF-Token": token},
    )
    assert r.status_code == 200, r.text
    r = c.put(
        "/diagnosis/__csrf_put__",
        json={"checked": ["A1", "A5", "A6", "B1", "C1", "D1"], "decision": "confirmed"},
        headers={"X-CSRF-Token": token},
    )
    assert r.status_code == 200, (r.status_code, r.text)
    assert r.json()["evaluation"]["met"] is True, r.text


def test_csrf_route_sets_cookie_and_returns_token(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    r = c.get("/diagnosis/_csrf")
    assert r.status_code == 200, (r.status_code, r.text)
    token = r.json().get("token")
    assert token and "." in token, r.text
    # The cookie set on the response must equal the body token.
    assert "csrf=" in r.headers.get("set-cookie", ""), r.headers
    # And: that token must be usable for a subsequent write.
    c.cookies.set("csrf", token)
    r2 = c.post(
        "/diagnosis/__csrf_mint__/init",
        headers={"X-CSRF-Token": token},
    )
    assert r2.status_code == 200, r2.text


def test_html_page_carries_meta_token(port):
    diag_csrf.reset_secret_for_tests()
    c = _client(port)
    r = c.get("/")
    assert r.status_code == 200, (r.status_code, r.text)
    assert 'name="csrf-token"' in r.text, "page should inject csrf meta tag"
    # The cookie must accompany the page response.
    assert "csrf=" in r.headers.get("set-cookie", ""), r.headers


def test_bypass_env_skips_csrf(port):
    """DIAGNOSIS_AUTH_BYPASS=1 (self-check path) must skip CSRF too,
    or the in-process self-check would 403 on its first PUT. Mirrors
    how auth bypass already works."""
    diag_csrf.reset_secret_for_tests()
    os.environ["DIAGNOSIS_AUTH_BYPASS"] = "1"
    try:
        # Re-import-safe: the api module reads the env lazily through the
        # _require_csrf shim, so no reload needed.
        c = TestClient(app)
        # No token, no cookie — must still succeed under the bypass.
        r = c.get("/diagnosis/_meta")
        assert r.status_code == 200, r.text
        r = c.post("/diagnosis/__bypass__/init")
        assert r.status_code == 200, r.text
        r = c.put("/diagnosis/__bypass__", json={"checked": ["A1"], "decision": None})
        assert r.status_code == 200, r.text
    finally:
        os.environ.pop("DIAGNOSIS_AUTH_BYPASS", None)


def main() -> None:
    _global_httpd, _global_port = _start_fake_auth()

    failures = []
    cases = [
        ("test_missing_csrf_blocks_put",
         lambda: test_missing_csrf_blocks_put(_global_port)),
        ("test_missing_csrf_blocks_init",
         lambda: test_missing_csrf_blocks_init(_global_port)),
        ("test_header_only_blocked",
         lambda: test_header_only_blocked(_global_port)),
        ("test_cookie_only_blocked",
         lambda: test_cookie_only_blocked(_global_port)),
        ("test_cookie_header_mismatch_blocked",
         lambda: test_cookie_header_mismatch_blocked(_global_port)),
        ("test_bad_signature_blocked",
         lambda: test_bad_signature_blocked(_global_port)),
        ("test_valid_token_allows_init",
         lambda: test_valid_token_allows_init(_global_port)),
        ("test_valid_token_allows_put",
         lambda: test_valid_token_allows_put(_global_port)),
        ("test_csrf_route_sets_cookie_and_returns_token",
         lambda: test_csrf_route_sets_cookie_and_returns_token(_global_port)),
        ("test_html_page_carries_meta_token",
         lambda: test_html_page_carries_meta_token(_global_port)),
        ("test_bypass_env_skips_csrf",
         lambda: test_bypass_env_skips_csrf(_global_port)),
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
    print(f"\nOK: {len(cases)}/{len(cases)} CSRF tests passed")


if __name__ == "__main__":
    main()
