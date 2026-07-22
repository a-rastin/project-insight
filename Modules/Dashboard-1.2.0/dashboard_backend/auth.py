from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from http.cookies import SimpleCookie
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen

from fastapi import Request

from .config import settings


class AuthSessionError(Exception):
    pass


def auth_session_url(request: Request) -> str:
    if settings.auth_session_url:
        return settings.auth_session_url
    if settings.auth_base_url:
        return f"{settings.auth_base_url.rstrip('/')}/api/auth/session"
    if settings.use_mock_auth:
        return f"{request.url.scheme}://{request.headers.get('host')}/api/auth/session"
    return ""


def forwarded_auth_headers(request: Request, session: dict[str, Any] | None = None) -> dict[str, str]:
    headers = {"accept": "application/json"}
    cookies = SimpleCookie()
    cookies.load(request.headers.get("cookie", ""))
    auth_cookie = cookies.get("insight_session")
    if auth_cookie:
        headers["cookie"] = f"insight_session={auth_cookie.value}"
    correlation_id = request.headers.get("x-correlation-id")
    if correlation_id:
        headers["x-correlation-id"] = correlation_id
    return headers


def _parse_expiry(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)).astimezone(UTC)


def normalize_auth_identity(data: dict[str, Any]) -> dict[str, Any] | None:
    if data.get("schemaVersion") != "1.0.0" or data.get("authenticated") is not True:
        return None
    user, session, gates = data.get("user"), data.get("session"), data.get("gates")
    if not isinstance(user, dict) or not isinstance(session, dict) or not isinstance(gates, dict):
        return None
    if gates.get("disclaimerAccepted") is not True or gates.get("passwordChangeRequired") is not False:
        return None
    session_id, expires_at, roles = session.get("id"), _parse_expiry(session.get("expiresAt")), user.get("roles")
    if not isinstance(session_id, str) or not session_id or not expires_at or expires_at <= datetime.now(UTC):
        return None
    if not isinstance(user.get("id"), str) or not user["id"] or not isinstance(user.get("displayName"), str):
        return None
    if not isinstance(roles, list) or any(not isinstance(role, str) or role != role.lower() for role in roles):
        return None
    role = next((value for value in ("psychiatrist", "admin") if value in roles), None)
    if not role:
        return None
    return {
        "authSessionId": session_id,
        "authExpiresAt": expires_at.isoformat().replace("+00:00", "Z"),
        "user": {"id": user["id"], "role": role.upper(), "fullName": user["displayName"], "title": "Dr." if role == "psychiatrist" else ""},
    }


def _fetch_json(endpoint: str, headers: dict[str, str]) -> dict[str, Any] | None:
    req = UrlRequest(endpoint, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=settings.auth_session_timeout_seconds) as response:
            if response.status in [401, 403]:
                return None
            if response.status < 200 or response.status >= 300:
                raise AuthSessionError(f"Authentication session check failed with {response.status}")
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code in [401, 403]:
            return None
        raise AuthSessionError(f"Authentication session check failed with {error.code}") from error
    except URLError as error:
        raise AuthSessionError(str(error.reason)) from error


async def fetch_auth_identity(request: Request, session: dict[str, Any] | None = None) -> dict[str, Any] | None:
    endpoint = auth_session_url(request)
    if not endpoint:
        raise AuthSessionError("Authentication session endpoint is not configured")
    data = await asyncio.to_thread(_fetch_json, endpoint, forwarded_auth_headers(request, session))
    return normalize_auth_identity(data or {}) if data else None
