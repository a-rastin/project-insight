from __future__ import annotations
import json,secrets
from dataclasses import dataclass
from datetime import UTC,datetime
from http.cookies import SimpleCookie
from typing import Any,Protocol
from urllib.error import HTTPError,URLError
from urllib.request import Request as UrlRequest,urlopen
from fastapi import Request
@dataclass(frozen=True,slots=True)
class SessionState:
    active:bool
    subject:str|None=None
    roles:frozenset[str]=frozenset()
    csrf_token:str|None=None
    blocked_reason:str|None=None
    expired:bool=False
class SessionAdapter(Protocol):
    def fetch_session(self,request:Request)->SessionState:...
class AuthenticationRestAdapter:
    def __init__(self,session_url:str,timeout_seconds:float=2.0)->None:self.session_url,self.timeout_seconds=session_url,timeout_seconds
    def fetch_session(self,request:Request)->SessionState:
        outbound=UrlRequest(self.session_url,method="GET");cookie=request.headers.get("cookie")
        if cookie:outbound.add_header("Cookie",cookie)
        try:
            with urlopen(outbound,timeout=self.timeout_seconds) as response:payload=json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:return SessionState(active=False,expired=exc.code==401)
        except (OSError,URLError,ValueError):return SessionState(active=False)
        return session_from_payload(payload)
def session_from_payload(payload:dict[str,Any])->SessionState:
    if payload.get("schemaVersion")!="1.0.0" or payload.get("authenticated") is not True:return SessionState(active=False)
    user,session,gates=payload.get("user"),payload.get("session"),payload.get("gates")
    if not all(isinstance(value,dict) for value in (user,session,gates)):return SessionState(active=False)
    if gates.get("disclaimerAccepted") is not True:return SessionState(active=False,blocked_reason="disclaimer_required")
    if gates.get("passwordChangeRequired") is not False:return SessionState(active=False,blocked_reason="forced_password_change")
    subject,sid,roles=user.get("id"),session.get("id"),user.get("roles")
    if not isinstance(subject,str) or not subject or not isinstance(sid,str) or not sid or not isinstance(roles,list) or any(not isinstance(role,str) or role!=role.lower() for role in roles):return SessionState(active=False)
    expires=session.get("expiresAt")
    if not isinstance(expires,str):return SessionState(active=False)
    try:parsed=datetime.fromisoformat(expires.replace("Z","+00:00"))
    except ValueError:return SessionState(active=False)
    parsed=parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC);expired=parsed.astimezone(UTC)<=datetime.now(UTC)
    return SessionState(not expired,subject,frozenset(roles),expired=expired)
def assert_csrf_token(request:Request,session:SessionState,header_name:str)->None:
    supplied=request.headers.get(header_name);expected=session.csrf_token
    if not expected:
        cookies=SimpleCookie();cookies.load(request.headers.get("cookie",""));expected=cookies.get("csrf_token").value if cookies.get("csrf_token") else None
    if not supplied or not expected or not secrets.compare_digest(supplied,expected):raise CsrfError
class CsrfError(Exception):pass
