from __future__ import annotations

import json
import os
import socket
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from contextlib import ExitStack
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen


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
                cookie = self.headers.get("Cookie") or self.headers.get("cookie") or ""
                token = next((part.split("=", 1)[1] for part in cookie.split(";") if part.strip().startswith("insight_session=")), "")
                owner.requests.append(
                    {
                        "path": self.path,
                        "cookie": cookie,
                        "correlationId": self.headers.get("X-Correlation-ID") or "",
                        "unexpected": self.headers.get("X-Dashboard-User") or "",
                    }
                )
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


class MockModuleServer:
    def __init__(self, module_id: str, interface_version: str = "1.0.0", ready_status: int = 200, contract_status: int = 200) -> None:
        self.module_id = module_id
        self.interface_version = interface_version
        self.ready_status = ready_status
        self.contract_status = contract_status
        self.requests: list[str] = []

    def __enter__(self) -> "MockModuleServer":
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                owner.requests.append(self.path)
                if self.path == "/contract":
                    status = owner.contract_status
                    payload = {
                        "moduleId": owner.module_id,
                        "moduleVersion": "1.0.0",
                        "interfaceVersion": owner.interface_version,
                        "schemaVersion": "1.0.0",
                        "basePath": f"/modules/{owner.module_id}",
                        "capabilities": [],
                        "dependencies": [],
                        "auth": {"required": True, "schemes": ["session"]},
                        "compatibilityRoutes": [],
                        "supportedClinicalScope": {"declaration": "module-owned", "populations": [], "workflows": []},
                    }
                elif self.path == "/ready":
                    status = owner.ready_status
                    payload = {"status": "ready" if status == 200 else "not-ready"}
                else:
                    status = 404
                    payload = {"error": "not_found"}
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
        self.contract_url = f"http://127.0.0.1:{self.port}/contract"
        return self

    def __exit__(self, *_: object) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


class DashboardServer:
    def __init__(self, auth_session_url: str | None = None, module_registry: list[dict] | None = None) -> None:
        self.auth_session_url = auth_session_url
        self.module_registry = module_registry

    def __enter__(self) -> str:
        self.tempdir = tempfile.TemporaryDirectory()
        self.auth_server = None
        if not self.auth_session_url:
            self.auth_server = MockAuthenticationServer().__enter__()
            self.auth_server.set_payload(
                "psy-1",
                auth_payload(session={"id": "psy-1"}, user={"displayName": "Mina Rahimi"}),
            )
            self.auth_server.set_payload(
                "admin-1",
                auth_payload(
                    session={"id": "admin-1"},
                    user={"id": "admin-1", "username": "admin", "roles": ["admin"], "displayName": "Ari Morgan"},
                ),
            )
            self.auth_session_url = self.auth_server.url
        self.db_path = os.path.join(self.tempdir.name, "dashboard.sqlite3")
        os.environ["DASHBOARD_DB_PATH"] = self.db_path
        if self.module_registry is None:
            os.environ.pop("DASHBOARD_MODULE_REGISTRY", None)
        else:
            os.environ["DASHBOARD_MODULE_REGISTRY"] = json.dumps(self.module_registry)
        os.environ["AUTH_SESSION_URL"] = self.auth_session_url
        os.environ["DASHBOARD_MOCK_AUTH"] = "0"
        os.environ.pop("AUTH_BASE_URL", None)
        for name in list(sys.modules):
            if name == "dashboard_backend" or name.startswith("dashboard_backend."):
                del sys.modules[name]

        import uvicorn
        from dashboard_backend.main import app

        self.port = free_port()
        self.config = uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="error")
        self.server = uvicorn.Server(self.config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()

        base = f"http://127.0.0.1:{self.port}"
        deadline = time.time() + 5
        while time.time() < deadline:
            try:
                request_json(base, "/healthz")
                return base
            except Exception:
                time.sleep(0.05)
        raise RuntimeError("server did not start")

    def __exit__(self, *_: object) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)
        self.tempdir.cleanup()
        if self.auth_server:
            self.auth_server.__exit__()


def request_json(base: str, path: str, method: str = "GET", headers: dict[str, str] | None = None, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = Request(
        f"{base}{path}",
        data=data,
        method=method,
        headers={"content-type": "application/json", **(headers or {})},
    )
    try:
        with urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        try:
            payload = json.loads(error.read().decode("utf-8"))
        finally:
            if error.fp:
                error.fp.close()
            error.close()
        return error.code, payload


def create_session(base: str, user_id: str) -> dict:
    status, data = request_json(
        base,
        "/internal/dashboard/session",
        method="POST",
        headers={"Cookie": f"insight_session={user_id}"},
        body={"device": "Test"},
    )
    assert status == 201
    data["_authHeaders"] = {"Cookie": f"insight_session={user_id}"}
    return data


def session_headers(session: dict) -> dict[str, str]:
    return {"x-dashboard-session": session["sessionId"], **session["_authHeaders"]}


def future_iso() -> str:
    return (datetime.now(UTC) + timedelta(hours=1)).isoformat().replace("+00:00", "Z")


def auth_payload(**overrides: dict) -> dict:
    payload = {
        "schemaVersion": "1.0.0",
        "authenticated": True,
        "session": {"id": "auth-1", "expiresAt": future_iso()},
        "user": {"id": "psy-1", "username": "clinician", "roles": ["psychiatrist"], "displayName": "Verified Clinician"},
        "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(payload.get(key), dict):
            payload[key] = {**payload[key], **value}
        else:
            payload[key] = value
    return payload


class AuthSessionNormalizationTest(unittest.TestCase):
    def test_auth_identity_requires_verified_session_and_derives_profile(self) -> None:
        from dashboard_backend.auth import normalize_auth_identity

        identity = normalize_auth_identity(auth_payload())

        self.assertIsNotNone(identity)
        assert identity is not None
        self.assertEqual(identity["authSessionId"], "auth-1")
        self.assertEqual(identity["user"]["id"], "psy-1")
        self.assertEqual(identity["user"]["role"], "PSYCHIATRIST")
        self.assertEqual(identity["user"]["fullName"], "Verified Clinician")

    def test_auth_identity_rejects_missing_and_blocked_sessions(self) -> None:
        from dashboard_backend.auth import normalize_auth_identity

        blocked_payloads = [
            auth_payload(session=None),
            auth_payload(authenticated=False),
            auth_payload(session={"expiresAt": "2000-01-01T00:00:00Z"}),
            auth_payload(session={"expiresAt": "2000-01-01T00:00:00Z"}),
            auth_payload(gates={"disclaimerAccepted": False, "passwordChangeRequired": False}),
            auth_payload(gates={"disclaimerAccepted": True, "passwordChangeRequired": True}),
            {"ok": True, "user_id": "psy-1", "session_id": "auth-1", "role": "PSYCHIATRIST"},
            auth_payload(gates={"disclaimerAccepted": False, "passwordChangeRequired": False}),
        ]
        for payload in blocked_payloads:
            with self.subTest(payload=payload):
                self.assertIsNone(normalize_auth_identity(payload))

    def test_auth_identity_rejects_legacy_identity_shapes(self) -> None:
        from dashboard_backend.auth import normalize_auth_identity

        legacy_payloads = [
            {"ok": True, "user_id": "psy-1", "session_id": "auth-1", "role": "PSYCHIATRIST"},
            {"authenticated": True, "userId": "psy-1", "sessionId": "auth-1", "role": "PSYCHIATRIST"},
            {"schemaVersion": "0.9.0", "authenticated": True, "identity": {"id": "psy-1"}},
        ]

        for payload in legacy_payloads:
            with self.subTest(payload=payload):
                self.assertIsNone(normalize_auth_identity(payload))


class DashboardBackendTest(unittest.TestCase):
    def test_health_and_readiness(self) -> None:
        with DashboardServer() as base:
            self.assertEqual(request_json(base, "/healthz")[0], 200)
            self.assertEqual(request_json(base, "/readyz")[0], 200)

    def test_dataset_schema_keeps_only_dashboard_owned_tables(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = os.path.join(tempdir, "dashboard.sqlite3")
            from dashboard_backend.db import SQLiteAdapter
            from dashboard_backend.repository import DashboardRepository

            DashboardRepository(SQLiteAdapter(db_path)).initialize()
            conn = sqlite3.connect(db_path)
            try:
                tables = {
                    row[0]
                    for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
                }
            finally:
                conn.close()

        self.assertEqual(tables, {"dashboard_sessions", "workflow_contexts", "workspace_events"})

    def test_dashboard_creates_sessions_from_authentication_identity_not_body_identity(self) -> None:
        with DashboardServer() as base:
            status, created = request_json(
                base,
                "/internal/dashboard/session",
                method="POST",
                headers={"Cookie": "insight_session=psy-1"},
                body={"userId": "admin-1", "role": "ADMIN", "fullName": "Spoofed Admin"},
            )

            self.assertEqual(status, 201)
            self.assertEqual(created["user"]["id"], "psy-1")
            self.assertEqual(created["user"]["role"], "PSYCHIATRIST")
            self.assertEqual(created["user"]["fullName"], "Mina Rahimi")

            status, workspace = request_json(
                base,
                "/internal/dashboard/workspace",
                headers={"Cookie": "insight_session=psy-1", "x-dashboard-session": created["sessionId"]},
            )
            self.assertEqual(status, 200)
            self.assertEqual(workspace["workspace"]["kind"], "PSYCHIATRIST")
            self.assertEqual(workspace["workspace"]["title"], "Workspace")

    def test_dashboard_refuses_activation_without_authentication_session(self) -> None:
        with DashboardServer() as base:
            status, data = request_json(
                base,
                "/internal/dashboard/session",
                method="POST",
                body={"userId": "psy-1", "role": "PSYCHIATRIST"},
            )

            self.assertEqual(status, 401)
            self.assertEqual(data["error"], "authentication_session_required")

    def test_psychiatrist_workspace_model_has_exact_buttons_and_route_discovery(self) -> None:
        with DashboardServer() as base:
            created = create_session(base, "psy-1")
            status, workspace = request_json(base, "/internal/dashboard/workspace", headers=session_headers(created))

            self.assertEqual(status, 200)
            self.assertEqual(workspace["displayName"], "Dr. Mina Rahimi")
            self.assertEqual(workspace["user"]["displayName"], "Dr. Mina Rahimi")
            datetime.fromisoformat(workspace["currentDateTime"].replace("Z", "+00:00"))
            self.assertEqual(workspace["workspace"]["title"], "Workspace")
            self.assertEqual(
                [button["title"] for button in workspace["workspace"]["buttons"]],
                [],
            )
            self.assertNotIn("cards", workspace["workspace"])
            self.assertNotIn("patients", workspace)
            self.assertNotIn("drafts", workspace)
            self.assertNotIn("followUps", workspace)

    def test_admin_workspace_model_has_exact_buttons_only(self) -> None:
        with DashboardServer() as base:
            created = create_session(base, "admin-1")
            status, workspace = request_json(base, "/internal/dashboard/workspace", headers=session_headers(created))

            self.assertEqual(status, 200)
            self.assertEqual(workspace["displayName"], "Ari Morgan")
            datetime.fromisoformat(workspace["currentDateTime"].replace("Z", "+00:00"))
            self.assertEqual(workspace["workspace"]["title"], "Workspace")
            self.assertEqual(
                [button["title"] for button in workspace["workspace"]["buttons"]],
                [],
            )
            self.assertNotIn("cards", workspace["workspace"])
            self.assertNotIn("oversight", workspace)
            self.assertNotIn("guidelineRevisions", json.dumps(workspace))
            self.assertNotIn("Bayesian", json.dumps(workspace))
            self.assertNotIn("Admin oversight", json.dumps(workspace))

    def test_runtime_discovery_reports_every_configured_module_state(self) -> None:
        with ExitStack() as stack:
            available = stack.enter_context(MockModuleServer("available"))
            degraded = stack.enter_context(MockModuleServer("degraded", ready_status=503))
            incompatible = stack.enter_context(MockModuleServer("incompatible", interface_version="2.0.0"))
            unavailable = stack.enter_context(MockModuleServer("unavailable", contract_status=503))
            modules = [
                {"moduleId": server.module_id, "title": server.module_id.title(), "roles": ["PSYCHIATRIST"], "contractUrl": server.contract_url}
                for server in (available, degraded, incompatible, unavailable)
            ]
            base = stack.enter_context(DashboardServer(module_registry=modules))
            created = create_session(base, "psy-1")
            status, workspace = request_json(base, "/internal/dashboard/workspace", headers=session_headers(created))

            self.assertEqual(status, 200)
            buttons = workspace["workspace"]["buttons"]
            self.assertEqual([button["id"] for button in buttons], ["available", "degraded", "incompatible", "unavailable"])
            self.assertEqual([button["status"] for button in buttons], ["available", "degraded", "incompatible", "unavailable"])
            self.assertTrue(all(button["reason"] for button in buttons))
            self.assertNotIn("placeholder", json.dumps(buttons))
            for server in (available, degraded, incompatible, unavailable):
                self.assertEqual(server.requests, ["/contract", "/ready"])

            status, route = request_json(
                base,
                "/internal/dashboard/module-routes/available",
                headers=session_headers(created),
            )
            self.assertEqual(status, 200)
            self.assertEqual(route["status"], "available")
            self.assertEqual(route["href"], "/modules/available")
            self.assertNotIn("placeholder", route)

    def test_module_routes_remain_role_scoped(self) -> None:
        with MockModuleServer("logs") as module:
            registry = [{"moduleId": "logs", "title": "Logs", "roles": ["ADMIN"], "contractUrl": module.contract_url}]
            with DashboardServer(module_registry=registry) as base:
                psychiatrist = create_session(base, "psy-1")
                status, data = request_json(base, "/internal/dashboard/module-routes/logs", headers=session_headers(psychiatrist))
                self.assertEqual(status, 404)
                self.assertEqual(data["error"], "module_route_not_available")

    def test_workflow_contexts_are_server_owned_and_independent_across_tabs(self) -> None:
        patient_one = "00000000-0000-4000-8000-000000000101"
        encounter_one = "00000000-0000-4000-8000-000000000201"
        patient_two = "00000000-0000-4000-8000-000000000102"
        encounter_two = "00000000-0000-4000-8000-000000000202"
        with MockModuleServer("available") as module:
            registry = [{"moduleId": "available", "title": "Available", "roles": ["PSYCHIATRIST"], "contractUrl": module.contract_url}]
            with DashboardServer(module_registry=registry) as base:
                session = create_session(base, "psy-1")
                contexts = []
                for patient_uuid, encounter_uuid in ((patient_one, encounter_one), (patient_two, encounter_two)):
                    status, context = request_json(
                        base,
                        "/internal/dashboard/workflow-context",
                        method="POST",
                        headers=session_headers(session),
                        body={"patientUuid": patient_uuid, "encounterUuid": encounter_uuid},
                    )
                    self.assertEqual(status, 201)
                    contexts.append(context["workflowContextId"])

                self.assertNotEqual(*contexts)
                for context_id, patient_uuid, encounter_uuid in zip(contexts, (patient_one, patient_two), (encounter_one, encounter_two)):
                    status, resolved = request_json(
                        base,
                        "/internal/dashboard/workflow-context",
                        headers={**session_headers(session), "x-workflow-context": context_id},
                    )
                    self.assertEqual(status, 200)
                    self.assertEqual(resolved, {"patientUuid": patient_uuid, "encounterUuid": encounter_uuid})

                status, route = request_json(
                    base,
                    "/internal/dashboard/module-routes/available",
                    headers={**session_headers(session), "x-workflow-context": contexts[0]},
                )
                self.assertEqual(status, 200)
                self.assertEqual(route["href"], "/modules/available")
                self.assertEqual(route["workflowContextId"], contexts[0])
                self.assertNotIn(patient_one, json.dumps(route))
                self.assertNotIn(encounter_one, json.dumps(route))

                status, summary = request_json(
                    base,
                    "/internal/dashboard/workflow-status",
                    headers={**session_headers(session), "x-workflow-context": contexts[0]},
                )
                self.assertEqual(status, 200)
                self.assertEqual(summary, {"modules": [{"moduleId": "available", "status": "available", "summary": "contract and readiness checks passed"}]})

    def test_dashboard_session_cookie_supports_refresh_without_url_state(self) -> None:
        with DashboardServer() as base:
            session = create_session(base, "psy-1")
            status, workspace = request_json(
                base,
                "/internal/dashboard/workspace",
                headers={
                    "Cookie": f"insight_session=psy-1; insight_dashboard_session={session['sessionId']}"
                },
            )
            self.assertEqual(status, 200)
            self.assertEqual(workspace["user"]["id"], "psy-1")

    def test_workflow_context_expires_when_authentication_is_revoked(self) -> None:
        with MockAuthenticationServer() as auth:
            auth.set_payload("auth-psy", auth_payload(session={"id": "auth-psy"}))
            with DashboardServer(auth.url) as base:
                headers = {"Cookie": "insight_session=auth-psy"}
                status, session = request_json(base, "/internal/dashboard/session", method="POST", headers=headers)
                self.assertEqual(status, 201)
                status, context = request_json(
                    base,
                    "/internal/dashboard/workflow-context",
                    method="POST",
                    headers={**headers, "x-dashboard-session": session["sessionId"]},
                    body={
                        "patientUuid": "00000000-0000-4000-8000-000000000101",
                        "encounterUuid": "00000000-0000-4000-8000-000000000201",
                    },
                )
                self.assertEqual(status, 201)

                auth.set_payload("auth-psy", {"authenticated": False}, status=401)
                status, data = request_json(
                    base,
                    "/internal/dashboard/workflow-context",
                    headers={
                        **headers,
                        "x-dashboard-session": session["sessionId"],
                        "x-workflow-context": context["workflowContextId"],
                    },
                )
                self.assertEqual(status, 401)
                self.assertEqual(data["error"], "authentication_session_required")

    def test_browser_source_does_not_persist_identifiers_or_put_them_in_history(self) -> None:
        source = (os.path.dirname(__file__) + "/dashboard.js")
        with open(source, encoding="utf-8") as handle:
            javascript = handle.read()
        self.assertNotIn("localStorage", javascript)
        self.assertNotIn("?session=", javascript)
        self.assertNotIn("patientUuid", javascript)
        self.assertNotIn("encounterUuid", javascript)

    def test_dashboard_does_not_own_patient_mutation_endpoint(self) -> None:
        with DashboardServer() as base:
            created = create_session(base, "psy-1")
            status, _ = request_json(
                base,
                "/internal/dashboard/patients",
                method="POST",
                headers=session_headers(created),
                body={"name": "Boundary Patient"},
            )

            self.assertEqual(status, 404)

    def test_signed_out_dashboard_sessions_stop_workspace_access(self) -> None:
        with DashboardServer() as base:
            created = create_session(base, "admin-1")
            status, _ = request_json(
                base,
                "/internal/dashboard/session",
                method="DELETE",
                headers=session_headers(created),
            )
            self.assertEqual(status, 200)

            status, data = request_json(base, "/internal/dashboard/workspace", headers=session_headers(created))
            self.assertEqual(status, 401)
            self.assertEqual(data["error"], "dashboard_session_required")

    def test_contract_uses_mocked_authentication_session_endpoint(self) -> None:
        with MockAuthenticationServer() as auth:
            auth.set_payload(
                "auth-psy",
                auth_payload(session={"id": "auth-psy"}, user={"id": "psy-ext", "displayName": "Verified Clinician"}),
            )
            with DashboardServer(auth.url) as base:
                cookie = {"Cookie": "insight_session=auth-psy"}
                status, created = request_json(
                    base,
                    "/internal/dashboard/session",
                    method="POST",
                    headers=cookie,
                    body={"userId": "admin-1", "role": "ADMIN", "fullName": "Spoofed Admin"},
                )
                self.assertEqual(status, 201)
                self.assertEqual(created["user"]["id"], "psy-ext")
                self.assertEqual(created["user"]["role"], "PSYCHIATRIST")

                status, workspace = request_json(
                    base,
                    "/internal/dashboard/workspace",
                    headers={**cookie, "x-dashboard-session": created["sessionId"]},
                )
                self.assertEqual(status, 200)
                self.assertEqual(workspace["displayName"], "Dr. Verified Clinician")

        self.assertTrue(auth.requests)
        self.assertEqual({request["path"] for request in auth.requests}, {"/api/auth/session"})
        self.assertTrue(any("insight_session=auth-psy" in request["cookie"] for request in auth.requests))

    def test_auth_adapter_forwards_only_session_cookie_and_correlation_metadata(self) -> None:
        with MockAuthenticationServer() as auth:
            auth.set_payload("auth-psy", auth_payload(session={"id": "auth-psy"}))
            with DashboardServer(auth.url) as base:
                status, _ = request_json(
                    base,
                    "/internal/dashboard/session",
                    method="POST",
                    headers={
                        "Cookie": "theme=dark; insight_csrf=secret; insight_session=auth-psy; patient=patient-1",
                        "X-Correlation-ID": "00000000-0000-4000-8000-000000000042",
                        "X-Dashboard-User": "spoofed-user",
                    },
                )

        self.assertEqual(status, 201)
        self.assertEqual(len(auth.requests), 1)
        self.assertEqual(auth.requests[0]["cookie"], "insight_session=auth-psy")
        self.assertEqual(auth.requests[0]["correlationId"], "00000000-0000-4000-8000-000000000042")
        self.assertEqual(auth.requests[0]["unexpected"], "")

    def test_invalid_auth_session_returns_401(self) -> None:
        with MockAuthenticationServer() as auth:
            with DashboardServer(auth.url) as base:
                status, data = request_json(
                    base,
                    "/internal/dashboard/session",
                    method="POST",
                    headers={"Cookie": "insight_session=missing"},
                )

            self.assertEqual(status, 401)
            self.assertEqual(data["error"], "authentication_session_required")

    def test_session_expiry_is_enforced_after_dashboard_session_creation(self) -> None:
        with MockAuthenticationServer() as auth:
            auth.set_payload("auth-psy", auth_payload(session={"id": "auth-psy", "expiresAt": future_iso()}))
            with DashboardServer(auth.url) as base:
                cookie = {"Cookie": "insight_session=auth-psy"}
                status, created = request_json(
                    base,
                    "/internal/dashboard/session",
                    method="POST",
                    headers=cookie,
                )
                self.assertEqual(status, 201)

                auth.set_payload("auth-psy", auth_payload(session={"id": "auth-psy", "expiresAt": "2000-01-01T00:00:00Z"}))
                status, data = request_json(
                    base,
                    "/internal/dashboard/workspace",
                    headers={**cookie, "x-dashboard-session": created["sessionId"]},
                )

            self.assertEqual(status, 401)
            self.assertEqual(data["error"], "authentication_session_required")

    def test_auth_role_change_is_not_spoofable_by_request_body(self) -> None:
        with MockAuthenticationServer() as auth:
            auth.set_payload(
                "auth-admin",
                auth_payload(
                    session={"id": "auth-admin"},
                    user={"id": "admin-ext", "username": "admin", "roles": ["admin"], "displayName": "Verified Admin"},
                ),
            )
            with DashboardServer(auth.url) as base:
                cookie = {"Cookie": "insight_session=auth-admin"}
                status, created = request_json(
                    base,
                    "/internal/dashboard/session",
                    method="POST",
                    headers=cookie,
                    body={"role": "PSYCHIATRIST", "fullName": "Spoofed Doctor"},
                )
                self.assertEqual(status, 201)
                self.assertEqual(created["user"]["role"], "ADMIN")

                status, workspace = request_json(
                    base,
                    "/internal/dashboard/workspace",
                    headers={**cookie, "x-dashboard-session": created["sessionId"]},
                )
                self.assertEqual(status, 200)
                self.assertEqual(workspace["workspace"]["kind"], "ADMIN")
                self.assertEqual(
                    [button["title"] for button in workspace["workspace"]["buttons"]],
                    [],
                )


if __name__ == "__main__":
    unittest.main()
