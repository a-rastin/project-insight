"""Authentication adapter for the diagnosis module.

Delegates trust to the central Insight auth service. We do NOT decode JWTs
or read the auth database — every protected request calls
``GET {AUTH_BASE_URL}/api/auth/session`` with the incoming ``Cookie`` header
and reads only the JSON response. The auth service is the source of truth
for who the user is and what role they hold.

The response shape we rely on (audit-friendly contract):

    {
        "authenticated": bool,
        "user_id":       str | null,
        "roles":         list[str],        # e.g. ["psychiatrist"], ["admin"]
        "session_id":    str | null
    }

Anything missing or non-authenticated -> 401. ``roles`` lacking the
required role for a route -> 403.

Configuration (env):
    AUTH_BASE_URL    default "http://localhost:9000" — Insight auth service.
    AUTH_TIMEOUT_S   default 2.0 — fail fast on a slow auth service.

Wire the dependency from ``api.py`` via ``require_role("psychiatrist")``.
The dependency enforces the call; routes never see raw cookies.
"""
from __future__ import annotations

import os
import urllib.error
import urllib.request
import json
from dataclasses import dataclass
from typing import Iterable

from fastapi import Depends, HTTPException, Request

from .config import settings

# Mutable module globals initialised from the settings adapter. Tests that
# mount a fake auth server rebind ``AUTH_BASE_URL`` via
# ``reset_auth_for_tests``; production code reads the import-time snapshot
# and never writes. Sourced here (not inlined into ``_fetch_session``) so
# ``readiness._check_auth`` can inspect the live value the next request
# will use without re-parsing the env.
AUTH_BASE_URL = settings.auth_url
AUTH_TIMEOUT_S = settings.auth_timeout_s


@dataclass(frozen=True)
class Session:
    """The slice of an Insight auth session this module consumes.

    Never holds a token. The auth service is the only thing that can mint
    or decode JWTs; this struct is built from the auth service's own JSON.
    """
    user_id: str
    roles: frozenset[str]
    session_id: str | None

    def has_any(self, allowed: Iterable[str]) -> bool:
        return any(r in self.roles for r in allowed)


class _AuthUnavailable(Exception):
    """The auth service is unreachable or returned a non-JSON body."""


def _fetch_session(cookie_header: str | None) -> dict:
    """Call the Insight auth service. Returns the parsed JSON.

    Raises ``_AuthUnavailable`` on transport / parse failure so the
    dependency can map that to a clean 401 (do not leak auth infra details).
    """
    url = f"{AUTH_BASE_URL.rstrip('/')}/api/auth/session"
    req = urllib.request.Request(url, method="GET")
    if cookie_header:
        req.add_header("Cookie", cookie_header)
    try:
        with urllib.request.urlopen(req, timeout=AUTH_TIMEOUT_S) as resp:
            body = resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise _AuthUnavailable(str(e)) from e
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise _AuthUnavailable(f"non-JSON auth response: {e}") from e


def _build_session(payload: dict) -> Session:
    """Normalize the auth-service payload. Never raises on missing fields —
    a partially populated response should fail closed (no session).
    """
    if not payload.get("authenticated"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = payload.get("user_id")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    raw_roles = payload.get("roles") or []
    if not isinstance(raw_roles, list):
        raw_roles = []
    roles = frozenset(r for r in raw_roles if isinstance(r, str))
    session_id = payload.get("session_id")
    if session_id is not None and not isinstance(session_id, str):
        session_id = None
    return Session(user_id=user_id, roles=roles, session_id=session_id)


def require_role(*allowed: str):
    """FastAPI dependency factory. Returns a dependency that enforces
    membership in ``allowed`` for the caller's session.

    Read routes use ``require_role("psychiatrist", "admin")``.
    Write routes use ``require_role("psychiatrist")`` — only clinicians
    may create or update diagnosis records; admins audit but do not edit.
    """
    allowed_set = frozenset(allowed)

    def _dep(request: Request) -> Session:
        try:
            payload = _fetch_session(request.headers.get("cookie"))
        except _AuthUnavailable:
            # Auth service is down / uncooperative. Fail closed: do not
            # silently treat the user as authenticated, do not leak the
            # transport error to the caller.
            raise HTTPException(status_code=401, detail="Not authenticated")
        session = _build_session(payload)
        if not session.has_any(allowed_set):
            raise HTTPException(status_code=403, detail="Forbidden")
        return session

    return _dep


def reset_auth_for_tests(base_url: str | None = None) -> None:
    """Test-only hook: rebind the auth base URL for the lifetime of the
    current process. Production code never needs this — it reads
    ``AUTH_BASE_URL`` at import time.

    Exposed because we deliberately avoid global mutable state in
    production. Tests that mount a fake auth server call this once in
    setup, then restore by passing ``None`` (which falls back to the
    settings-adapter value captured at import).
    """
    global AUTH_BASE_URL
    if base_url is not None:
        AUTH_BASE_URL = base_url
    else:
        AUTH_BASE_URL = settings.auth_url


__all__ = ["Session", "require_role", "reset_auth_for_tests", "AUTH_BASE_URL"]
