from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen

from fastapi import Request

from .config import settings


class AuthSessionError(Exception):
    pass


BLOCKED_AUTH_STATUSES = {
    "expired",
    "force_password_change",
    "forced_password_change",
    "forced_password_reset",
    "password_change_required",
    "password_reset_required",
    "disclaimer_blocked",
    "disclaimer_required",
    "disclaimer_acceptance_required",
    "blocked_by_disclaimer",
}

EXPIRED_FLAGS = ["expired", "isExpired"]
PASSWORD_BLOCK_FLAGS = [
    "forcePasswordChange",
    "forcePasswordChangeRequired",
    "forcedPasswordChange",
    "forcedPasswordChangeRequired",
    "forcedPasswordResetRequired",
    "mustChangePassword",
    "mustResetPassword",
    "passwordChangeRequired",
    "passwordResetRequired",
    "requiresPasswordChange",
]
DISCLAIMER_BLOCK_FLAGS = [
    "blockedByDisclaimer",
    "disclaimerBlocked",
    "disclaimerRequired",
    "disclaimerAcceptanceRequired",
    "requiresDisclaimer",
    "requiresDisclaimerAcceptance",
]


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
    for name in ["authorization", "cookie", "x-auth-session", "x-auth-session-id"]:
        value = request.headers.get(name)
        if value:
            headers[name] = value
    demo_user = request.headers.get("x-demo-auth-user")
    if settings.use_mock_auth and demo_user:
        headers["x-demo-auth-user"] = demo_user
    if session and session.get("authSessionId") and "x-auth-session" not in headers:
        headers["x-auth-session"] = session["authSessionId"]
    return headers


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ["1", "true", "yes"]
    return False


def _is_falsey(value: Any) -> bool:
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        return value.strip().lower() in ["0", "false", "no"]
    return False


def _status_key(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _has_blocked_status(*parts: dict[str, Any]) -> bool:
    return any(_status_key(part.get("status")) in BLOCKED_AUTH_STATUSES for part in parts)


def _has_truthy_flag(parts: list[dict[str, Any]], fields: list[str]) -> bool:
    return any(_is_truthy(part.get(field)) for part in parts for field in fields)


def _parse_expiry(value: Any) -> datetime | None:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, UTC)
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _is_expired(*parts: dict[str, Any]) -> bool:
    for part in parts:
        for field in ["expiresAt", "expires_at", "expires"]:
            expiry = _parse_expiry(part.get(field))
            if expiry and expiry <= datetime.now(UTC):
                return True
    return False


def _blocked_auth_session(data: dict[str, Any], session: dict[str, Any], user: dict[str, Any]) -> bool:
    parts = [data, session, user]
    return (
        ("authenticated" in data and _is_falsey(data.get("authenticated")))
        or _is_falsey(session.get("active"))
        or _has_blocked_status(data, session, user)
        or _has_truthy_flag(parts, EXPIRED_FLAGS)
        or _is_expired(data, session)
        or _has_truthy_flag(parts, PASSWORD_BLOCK_FLAGS)
        or _has_truthy_flag(parts, DISCLAIMER_BLOCK_FLAGS)
    )


def normalize_auth_identity(data: dict[str, Any]) -> dict[str, Any] | None:
    session = data.get("session") or {}
    if not isinstance(session, dict):
        return None
    user = data.get("user") or data
    if not isinstance(user, dict):
        return None
    auth_session_id = session.get("id") or data.get("sessionId") or data.get("authSessionId")
    if not auth_session_id or _blocked_auth_session(data, session, user):
        return None
    user_id = user.get("id") or user.get("userId")
    role = user.get("role")
    if not user_id or role not in ["ADMIN", "PSYCHIATRIST"]:
        return None
    return {
        "authSessionId": auth_session_id,
        "user": {
            "id": user_id,
            "role": role,
            "fullName": user.get("fullName") or user.get("name") or "Authenticated User",
            "title": user.get("title") or ("Dr." if role == "PSYCHIATRIST" else ""),
        },
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
        try:
            if error.code in [401, 403]:
                return None
            raise AuthSessionError(f"Authentication session check failed with {error.code}") from error
        finally:
            if error.fp:
                error.fp.close()
            error.close()
    except URLError as error:
        raise AuthSessionError(str(error.reason)) from error


async def fetch_auth_identity(request: Request, session: dict[str, Any] | None = None) -> dict[str, Any] | None:
    endpoint = auth_session_url(request)
    if not endpoint:
        raise AuthSessionError("Authentication session endpoint is not configured")
    data = await asyncio.to_thread(_fetch_json, endpoint, forwarded_auth_headers(request, session))
    return normalize_auth_identity(data or {}) if data else None