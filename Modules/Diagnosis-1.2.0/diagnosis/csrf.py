"""Signed double-submit CSRF for the diagnosis module's write routes.

PUT /diagnosis/{code} and POST /diagnosis/{code}/init mutate state. They
are wrapped with a ``Depends(require_csrf)`` guard that fails closed
(403) unless the request carries a matching signed token in both a
cookie and a header. Read routes are untouched.

Protocol
--------
1. The browser hits the HTML page (``GET /``) or the token endpoint
   ``GET /diagnosis/_csrf``. The server mints a fresh random value
   ``raw`` (32 random bytes, hex), binds it to nothing, signs it::

       token = f"{raw}.{hmac_sha256(secret, raw)}"

   The signed payload is returned in a JSON body ``{"token": token}``
   and set as the cookie ``csrf`` (``SameSite=Lax``, ``HttpOnly=False``
   so JS can read it back if needed; not ``Secure`` in dev — set
   ``DIAGNOSIS_CSRF_SECURE=1`` to flip it on for production behind TLS).
2. On every write request the browser sends BOTH::

       Cookie: csrf=<token>
       X-CSRF-Token: <token>

   The dependency reconstructs the signature, verifies the HMAC in
   constant time, and confirms that cookie value === header value.
   Cookie-only or header-only tokens fail closed (double-submit).
3. The HMAC secret is per-process random (``secrets.token_bytes(32)``).
   Tokens therefore do not survive a restart — clients must re-fetch
   after each server boot. Override with ``DIAGNOSIS_CSRF_SECRET`` so
   multiple workers in one deployment share the key.

Why HMAC and not raw bytes? The signature means an attacker cannot
mint a token from a value they read out of band — only the holder of
``secret`` can produce one the validator accepts. Combined with the
cookie===header check, this is the OWASP "signed double submit" pattern.

``DIAGNOSIS_AUTH_BYPASS=1`` (set by the in-process self-check) shorts
the dependency so boot-time self-checks don't need a token mint cycle.
"""
from __future__ import annotations

import os
import secrets
import hmac
import hashlib

from fastapi import HTTPException, Request

from .config import settings

COOKIE_NAME = "csrf"
HEADER_NAME = "X-CSRF-Token"

# ponytail: per-process random secret. Multiple workers / multi-process
# deployments MUST set DIAGNOSIS_CSRF_SECRET so a token minted by one
# worker validates on another. Same secret across workers, never shared
# across services. The settings adapter surfaces the pinned value (or
# ``None`` when unset); we fall back to a fresh random secret per import.
_SECRET = settings.csrf_secret if settings.csrf_secret is not None else secrets.token_bytes(32)

# Cookie flags. Flip to Secure behind TLS via env in production. Sourced
# from the settings adapter.
_SECURE_COOKIE = settings.csrf_secure


def _sign(raw: str) -> str:
    """Attach an HMAC-SHA256 signature to ``raw``. Returns ``raw.sig``."""
    sig = hmac.new(_SECRET, raw.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def _verify(token: str) -> bool:
    """Constant-time check that ``token`` was signed by this secret."""
    if not token or "." not in token:
        return False
    raw, _, sig = token.rpartition(".")
    if not raw or not sig:
        return False
    expected = hmac.new(_SECRET, raw.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)


def mint() -> str:
    """Mint a fresh signed token. Callers set it as the CSRF cookie and
    surface it to JS (meta tag / JSON body) on the same response."""
    raw = secrets.token_hex(16)  # 32 hex chars
    return _sign(raw)


def set_cookie(response, token: str) -> None:
    """Stamp the ``csrf`` cookie on ``response``. FastAPI's
    ``set_cookie`` is the portable seam."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=False,        # JS in the page may read it back
        secure=_SECURE_COOKIE,
        samesite="lax",
        path="/",
    )


def _read_cookie(request: Request) -> str | None:
    return request.cookies.get(COOKIE_NAME)


def _read_header(request: Request) -> str | None:
    return request.headers.get(HEADER_NAME)


def require_csrf(request: Request) -> None:
    """FastAPI dependency. Fail closed (403) on any mismatch.

    Mirrors ``auth.require_role``: route declares ``Depends(require_csrf)``
    in addition to the role dependency; the CSRF check runs first so a
    tokenless request never reaches the auth service.
    """
    # Self-check / in-process tests bypass with the same env flag auth uses.
    if os.environ.get("DIAGNOSIS_AUTH_BYPASS") == "1":
        return

    cookie = _read_cookie(request)
    header = _read_header(request)

    if not cookie or not header:
        raise HTTPException(status_code=403, detail="CSRF token missing")
    if not hmac.compare_digest(cookie, header):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    if not _verify(cookie) or not _verify(header):
        raise HTTPException(status_code=403, detail="CSRF token invalid")


def reset_secret_for_tests(secret: bytes | None = None) -> None:
    """Test-only hook (mirrors ``auth.reset_auth_for_tests``). Pin a
    known secret so tests can mint tokens for the duration of the run.
    Pass ``None`` to reset to a fresh random per-process secret.
    """
    global _SECRET
    if secret is None:
        _SECRET = os.environ.get("DIAGNOSIS_CSRF_SECRET") or secrets.token_bytes(32)
    else:
        _SECRET = secret


__all__ = [
    "COOKIE_NAME",
    "HEADER_NAME",
    "mint",
    "set_cookie",
    "require_csrf",
    "reset_secret_for_tests",
    "_sign",
    "_verify",
]
