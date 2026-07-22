from __future__ import annotations
import asyncio,json
from datetime import UTC,datetime
from typing import Any
from urllib.error import HTTPError,URLError
from urllib.request import Request as UrlRequest,urlopen
from fastapi import Request
from .config import settings
class AuthSessionError(Exception): pass
def auth_session_url(request: Request)->str:
    if settings.auth_session_url:return settings.auth_session_url
    if settings.auth_base_url:return f"{settings.auth_base_url.rstrip('/')}/api/auth/session"
    if settings.use_mock_auth:return f"{request.url.scheme}://{request.headers.get('host')}/api/auth/session"
    return ""
def forwarded_auth_headers(request: Request, session: dict[str, Any] | None = None)->dict[str,str]:
    headers={"accept":"application/json"}; cookie=request.headers.get("cookie")
    if cookie: headers["cookie"]=cookie
    demo=request.headers.get("x-demo-auth-user")
    if settings.use_mock_auth and not demo and session: demo=session.get("userId")
    if settings.use_mock_auth and demo: headers["x-demo-auth-user"]=demo
    return headers
def _expiry(value:Any)->datetime|None:
    if not isinstance(value,str) or not value.strip(): return None
    try: parsed=datetime.fromisoformat(value.strip().replace("Z","+00:00"))
    except ValueError: return None
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)).astimezone(UTC)
def normalize_authenticated_session(data:dict[str,Any])->dict[str,Any]|None:
    if data.get("schemaVersion")!="1.0.0" or data.get("authenticated") is not True:return None
    user,session,gates=data.get("user"),data.get("session"),data.get("gates")
    if not all(isinstance(value,dict) for value in (user,session,gates)):return None
    if gates.get("disclaimerAccepted") is not True or gates.get("passwordChangeRequired") is not False:return None
    sid=session.get("id"); uid=user.get("id"); roles=user.get("roles"); expires=_expiry(session.get("expiresAt"))
    if not isinstance(sid,str) or not sid or not isinstance(uid,str) or not uid or not expires or expires<=datetime.now(UTC):return None
    if not isinstance(roles,list) or any(not isinstance(role,str) for role in roles):return None
    normalized=[role.strip().upper() for role in roles if role.strip()]
    if not normalized:return None
    role="PSYCHIATRIST" if "PSYCHIATRIST" in normalized else normalized[0]
    return {"authSessionId":sid,"user":{"id":uid,"role":role,"roles":normalized,"fullName":user.get("displayName") or user.get("username") or "Authenticated User","title":"Dr." if role=="PSYCHIATRIST" else ""}}
def normalize_psychiatrist_session(data:dict[str,Any])->dict[str,Any]|None:
    identity=normalize_authenticated_session(data)
    return identity if identity and "PSYCHIATRIST" in identity["user"]["roles"] else None
def _fetch_json(endpoint:str,headers:dict[str,str])->dict[str,Any]|None:
    try:
        with urlopen(UrlRequest(endpoint,headers=headers,method="GET"),timeout=settings.auth_session_timeout_seconds) as response:
            if response.status in (401,403):return None
            if response.status<200 or response.status>=300:raise AuthSessionError("Authentication session check failed")
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code in (401,403):return None
        raise AuthSessionError("Authentication session check failed") from error
    except URLError as error:raise AuthSessionError(str(error.reason)) from error
async def fetch_auth_identity(request:Request,session:dict[str,Any]|None=None,*,require_psychiatrist:bool=False)->dict[str,Any]|None:
    endpoint=auth_session_url(request)
    if not endpoint:raise AuthSessionError("Authentication session endpoint is not configured")
    data=await asyncio.to_thread(_fetch_json,endpoint,forwarded_auth_headers(request, session))
    if not data:return None
    return normalize_psychiatrist_session(data) if require_psychiatrist else normalize_authenticated_session(data)
normalize_auth_identity=normalize_psychiatrist_session
