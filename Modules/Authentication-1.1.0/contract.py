"""Authentication discovery artifacts and runtime security metadata."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

try:
    from . import security
except ImportError:
    import security


_ROOT = Path(__file__).parent / "contracts"
_VERSION = "1.0.0"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _schema_path(version: str, name: str) -> Path:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", name):
        raise ValueError("invalid schema coordinates")
    path = _ROOT / "schemas" / version / f"{name}.schema.json"
    if not path.is_file():
        raise KeyError(name)
    return path


def schema(version: str, name: str) -> dict:
    return _load_json(_schema_path(version, name))


def contract_payload() -> dict:
    payload = _load_json(_ROOT / "examples" / _VERSION / "contract.json")
    session = security.cookie_kwargs()
    csrf = security.csrf_cookie_kwargs()
    payload["securityPolicy"]["sessionCookie"] = {
        "name": session["key"],
        "httpOnly": session["httponly"],
        "sameSite": session["samesite"].title(),
        "secure": session["secure"],
        "path": session["path"],
        "maxAgeSeconds": session["max_age"],
    }
    payload["securityPolicy"]["csrf"].update({
        "cookieName": csrf["key"],
        "headerName": security.cfg("AUTH_CSRF_HEADER_NAME"),
        "httpOnly": csrf["httponly"],
        "sameSite": csrf["samesite"].title(),
        "secure": csrf["secure"],
        "path": csrf["path"],
        "maxAgeSeconds": csrf["max_age"],
    })
    return payload


def openapi_document() -> dict:
    document = copy.deepcopy(_load_json(_ROOT / "openapi" / _VERSION / "authentication.openapi.json"))
    document["components"]["securitySchemes"]["SessionCookie"]["name"] = security.cfg("AUTH_COOKIE_NAME")
    document["components"]["parameters"]["CsrfHeader"]["name"] = security.cfg("AUTH_CSRF_HEADER_NAME")
    return document
