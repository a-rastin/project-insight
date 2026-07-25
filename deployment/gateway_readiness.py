"""Loopback readiness aggregator for required unified modules."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


REQUIRED_MODULES = {
    "authentication": "http://127.0.0.1:8101/readyz",
    "dashboard": "http://127.0.0.1:8102/readyz",
    "add-new-patient": "http://127.0.0.1:8103/api/health",
    "diagnosis": "http://127.0.0.1:8104/ready",
    "severity": "http://127.0.0.1:8105/ready",
    "medical-history": "http://127.0.0.1:8106/ready",
    "ddi-checker": "http://127.0.0.1:8107/ready",
    "bn-manager": "http://127.0.0.1:8108/api/ready",
    "treatment-plan": "http://127.0.0.1:8109/ready",
}


def probe(module_id: str, url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            payload = json.loads(response.read())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return {"ok": False, "reason": "readiness_probe_failed"}
    if not isinstance(payload, dict):
        return {"ok": False, "reason": "invalid_readiness_response"}
    ok = payload.get("ok") is True or payload.get("status") in {"ready", "ok"}
    if not ok:
        return {"ok": False, "reason": "module_not_ready"}
    return {"ok": True}


def aggregate_readiness() -> tuple[int, dict[str, Any]]:
    modules = {module_id: probe(module_id, url) for module_id, url in REQUIRED_MODULES.items()}
    ok = all(result["ok"] for result in modules.values())
    return (200 if ok else 503), {
        "ok": ok,
        "service": "unified-gateway",
        "status": "ready" if ok else "not-ready",
        "modules": modules,
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._send(200, {"ok": True, "service": "unified-gateway", "status": "alive"})
        elif self.path == "/readyz":
            status, payload = aggregate_readiness()
            self._send(status, payload)
        else:
            self.send_error(404)

    def log_message(self, _format: str, *_args: Any) -> None:
        return

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    ThreadingHTTPServer(("127.0.0.1", 8110), Handler).serve_forever()


if __name__ == "__main__":
    main()
