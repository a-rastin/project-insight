"""Reusable FastAPI transport adapter for the common module routes."""
from __future__ import annotations

import hashlib
import inspect
import json
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse, Response


_READINESS_KEYS = ("migrations", "configuration", "contractCompatibility", "dependencies")


def _etag(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return f'"sha256:{hashlib.sha256(payload).hexdigest()}"'


def _problem(request: Request, status: int, code: str, detail: str):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
    return {
        "type": f"https://insight.example/problems/{code.lower()}",
        "title": code.replace("_", " ").title(),
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "code": code,
        "requestId": request_id,
        "correlationId": correlation_id,
    }


def install_common_routes(app, registry, *, contract: dict, readiness=None, module_id: str | None = None):
    """Mount common routes on an app; module handlers remain outside this adapter."""

    @app.middleware("http")
    async def common_request_headers(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        causation_id = request.headers.get("X-Causation-ID")
        if causation_id:
            response.headers["X-Causation-ID"] = causation_id
        return response

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/ready")
    async def ready():
        result = readiness() if readiness else {key: "unknown" for key in _READINESS_KEYS}
        checks = await result if inspect.isawaitable(result) else result
        checks = {key: checks.get(key, "unknown") for key in _READINESS_KEYS}
        is_ready = all(value in ("ok", True) for value in checks.values())
        payload = {"status": "ready" if is_ready else "not_ready", "checks": checks}
        if module_id is not None:
            payload["module"] = module_id
        return JSONResponse(payload, status_code=200 if is_ready else 503)

    @app.get("/contract")
    async def module_contract():
        return JSONResponse(contract, headers={"ETag": _etag(contract)})

    @app.get("/openapi.json")
    async def common_openapi():
        document = registry.get_openapi()
        return JSONResponse(document, headers={"ETag": _etag(document)})

    @app.get("/schemas/{version}/{name}")
    async def versioned_schema(version: str, name: str, request: Request):
        try:
            schema = registry.get_schema(version, name)
        except (KeyError, ValueError):
            return JSONResponse(_problem(request, 404, "SCHEMA_NOT_FOUND", "Requested schema is not published."), status_code=404, media_type="application/problem+json")
        return JSONResponse(schema, headers={"ETag": _etag(schema)}, media_type="application/schema+json")

    return app
