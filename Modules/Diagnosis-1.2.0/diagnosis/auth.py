"""Canonical Authentication session adapter for Diagnosis."""
from __future__ import annotations
import json,urllib.error,urllib.request
from dataclasses import dataclass
from typing import Iterable
from fastapi import HTTPException,Request
from .config import settings
AUTH_BASE_URL=settings.auth_url
AUTH_TIMEOUT_S=settings.auth_timeout_s
@dataclass(frozen=True)
class Session:
    user_id:str
    roles:frozenset[str]
    session_id:str|None
    def has_any(self,allowed:Iterable[str])->bool:return any(role in self.roles for role in allowed)
class _AuthUnavailable(Exception):pass
def _fetch_session(cookie_header:str|None)->dict:
    request=urllib.request.Request(f"{AUTH_BASE_URL.rstrip('/')}/api/auth/session",method="GET")
    if cookie_header:request.add_header("Cookie",cookie_header)
    try:
        with urllib.request.urlopen(request,timeout=AUTH_TIMEOUT_S) as response:
            if response.status<200 or response.status>=300:raise _AuthUnavailable("Authentication session request failed")
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError,TimeoutError,OSError,_AuthUnavailable) as error:raise _AuthUnavailable(str(error)) from error
    except json.JSONDecodeError as error:raise _AuthUnavailable("Authentication session response was not JSON") from error
def _build_session(payload:dict)->Session:
    if payload.get("schemaVersion")!="1.0.0" or payload.get("authenticated") is not True:raise HTTPException(401,"Not authenticated")
    user,session,gates=payload.get("user"),payload.get("session"),payload.get("gates")
    if not all(isinstance(value,dict) for value in (user,session,gates)):raise HTTPException(401,"Not authenticated")
    if gates.get("disclaimerAccepted") is not True or gates.get("passwordChangeRequired") is not False:raise HTTPException(401,"Not authenticated")
    uid,sid,roles=user.get("id"),session.get("id"),user.get("roles")
    if not isinstance(uid,str) or not uid or not isinstance(sid,str) or not sid or not isinstance(roles,list) or any(not isinstance(role,str) or role!=role.lower() for role in roles):raise HTTPException(401,"Not authenticated")
    return Session(uid,frozenset(roles),sid)
def require_role(*allowed:str):
    allowed_set=frozenset(allowed)
    def _dep(request:Request)->Session:
        try:payload=_fetch_session(request.headers.get("cookie"))
        except _AuthUnavailable:raise HTTPException(401,"Not authenticated")
        session=_build_session(payload)
        if not session.has_any(allowed_set):raise HTTPException(403,"Forbidden")
        return session
    return _dep
def reset_auth_for_tests(base_url:str|None=None)->None:
    global AUTH_BASE_URL
    AUTH_BASE_URL=base_url if base_url is not None else settings.auth_url
__all__=["Session","require_role","reset_auth_for_tests","AUTH_BASE_URL"]
