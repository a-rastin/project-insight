from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field

try:
    from . import security
except ImportError:  # Keeps `python main.py` working from this directory.
    import security

# Deep module: the interface of the Authentication module. Five endpoints,
# all the complexity (bcrypt, sqlite, jwt, cookie config, role gate, disclaimer
# gate) lives in security.py. Callers (other INSIGHT modules) hit this router.

router = APIRouter(prefix="/api/auth", tags=["auth"])
GENERIC_LOGIN_FAILURE = "Wrong username or password"


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)
    role: str = Field(pattern="^(?i:admin|psychiatrist|user)$")


class LoginResponse(BaseModel):
    ok: bool
    next: str | None = None
    disclaimer_required: bool = False
    password_change_required: bool = False


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)
    role: str = Field(pattern="^(?i:admin|psychiatrist|user)$")


class RegisterResponse(BaseModel):
    ok: bool
    user_uuid: str


class AccountResponse(BaseModel):
    user_uuid: str
    username: str
    role: str
    disabled: bool
    must_change_password: bool
    disclaimer_signed: bool
    created_at: str


class AccountListResponse(BaseModel):
    ok: bool
    users: list[AccountResponse]


class ResetPasswordRequest(BaseModel):
    temporary_password: str | None = Field(default=None, min_length=1, max_length=256)


class ResetPasswordResponse(BaseModel):
    ok: bool
    user_uuid: str
    temporary_password: str


class UpdateRoleRequest(BaseModel):
    role: str = Field(pattern="^(?i:admin|psychiatrist|user)$")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=8, max_length=256)


class MessageResponse(BaseModel):
    ok: bool
    message: str | None = None


class DisclaimerResponse(BaseModel):
    ok: bool
    version: str
    title: str
    content_html: str
    acknowledgement: str
    accepted: bool
    accepted_version: str | None = None
    accepted_at: str | None = None
    message: str


class CsrfResponse(BaseModel):
    ok: bool
    csrf_token: str


class CanonicalUser(BaseModel):
    id: str
    username: str
    roles: list[str]
    displayName: str


class CanonicalSession(BaseModel):
    id: str
    expiresAt: str


class CanonicalGates(BaseModel):
    disclaimerAccepted: bool
    passwordChangeRequired: bool


class SessionResponse(BaseModel):
    schemaVersion: str
    authenticated: bool
    user: CanonicalUser | None
    session: CanonicalSession | None
    gates: CanonicalGates


class LegacySessionResponse(BaseModel):
    ok: bool
    user_id: int
    username: str
    role: str
    display_role: str
    disclaimer_status: str
    expires_at: int
    message: str
    clinical_role: str | None = None
    legacy_role: str | None = None


class AuditEntry(BaseModel):
    id: int
    actor_id: int | None = None
    actor_name: str
    target_id: int | None = None
    target_name: str | None = None
    action: str
    status: str
    metadata: str | None = None
    client_ip: str | None = None
    created_at: str


class AuditListResponse(BaseModel):
    ok: bool
    entries: list[AuditEntry]
    count: int


class HealthResponse(BaseModel):
    ok: bool
    service: str
    status: str


class ReadinessCheck(BaseModel):
    ok: bool
    status: str


class ReadinessResponse(BaseModel):
    ok: bool
    service: str
    status: str
    checks: dict[str, ReadinessCheck]


def _current_user(
    request: Request,
    require_disclaimer: bool = False,
    require_password_change: bool = False,
):
    # single place every endpoint routes through to resolve the session.
    token = request.cookies.get(security.cfg("AUTH_COOKIE_NAME"))
    if not token:
        return None
    return security.resolve_session(
        token,
        require_disclaimer=require_disclaimer,
        require_password_change=require_password_change,
    )


def _require_csrf(request: Request):
    cookie_token = request.cookies.get(security.cfg("AUTH_CSRF_COOKIE_NAME"))
    header_token = request.headers.get(security.cfg("AUTH_CSRF_HEADER_NAME"))
    if not security.verify_csrf_token(cookie_token, header_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")


def _require_admin(request: Request):
    payload = _current_user(request)
    if payload is None or payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return payload


def _account_response(row) -> AccountResponse:
    return AccountResponse(
        user_uuid=row["user_uuid"],
        username=row["username"],
        role=security.normalize_role(row["role"]),
        disabled=bool(row["disabled"]),
        must_change_password=bool(row["must_change_password"]),
        disclaimer_signed=bool(row["disclaimer_signed"]),
        created_at=row["created_at"],
    )


def _map_account_management_error(exc: Exception) -> HTTPException:
    if isinstance(exc, security.UserNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if isinstance(exc, security.SelfManagementError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, security.LastActiveAdminError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, security.InvalidRoleError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _post_auth_response(user) -> LoginResponse:
    role = security.normalize_role(user["role"])
    return LoginResponse(ok=True, next="/dashboard/admin" if role == "admin" else "/dashboard/user")


def _safe_redirect(next_path: str | None) -> str | None:
    """Only return paths we whitelisted. Never pass-through user-controlled."""
    if not next_path:
        return None
    allowed = {p.strip() for p in security.cfg("AUTH_ALLOWED_REDIRECTS").split(",") if p.strip()}
    if next_path in allowed:
        return next_path
    return None


def _display_role(role: str) -> str:
    return {
        "admin": "Administrator",
        "psychiatrist": "Psychiatrist",
    }[role]


def _disclaimer_status(role: str, disclaimer_signed: bool) -> str:
    if role == "psychiatrist":
        return "accepted" if disclaimer_signed else "pending"
    return "not_required"


def _login_client_id(request: Request) -> str:
    return request.client.host if request.client and request.client.host else "unknown"


def _audit(
    request: Request,
    action: str,
    actor: dict | None = None,
    target: dict | None = None,
    metadata: dict | None = None,
    status: str = "success",
) -> None:
    # ponytail: fire-and-forget — audit must never break an auth flow. The
    # storage layer also swallows nothing; if SQLite dies we surface elsewhere.
    # Calling sites use resolved-session dicts as actor/target shapes.
    try:
        security.record_audit(
            action=action,
            actor=actor,
            target=target,
            metadata=metadata,
            client_ip=_login_client_id(request),
            status=status,
        )
    except Exception:
        pass


def _generic_login_error(status_code: int = status.HTTP_401_UNAUTHORIZED) -> HTTPException:
    return HTTPException(status_code=status_code, detail=GENERIC_LOGIN_FAILURE)


@router.get("/health", response_model=HealthResponse)
def liveness():
    return HealthResponse(ok=True, service=security.SERVICE_NAME, status="alive")


@router.get("/ready", response_model=ReadinessResponse)
def readiness(response: Response):
    report = security.readiness_report()
    if not report["ok"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(**report)


@router.get("/csrf", response_model=CsrfResponse)
def csrf(response: Response):
    token = security.issue_csrf_token()
    kwargs = security.csrf_cookie_kwargs()
    kwargs["value"] = token
    response.set_cookie(**kwargs)
    return CsrfResponse(ok=True, csrf_token=token)


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, request: Request, response: Response):
    _require_csrf(request)
    client_id = _login_client_id(request)
    if not security.login_attempt_allowed(body.username, client_id):
        _audit(
            request,
            "login_failed",
            actor={"id": None, "username": body.username},
            metadata={"reason": "rate_limited"},
            status="failure",
        )
        raise _generic_login_error()

    user = security.get_user(body.username)
    # ponytail: blanket error message — never reveal which field failed, per
    # the spec. Generic message returned to UI; HTTP 401 only.
    if user is None or user["disabled"] or not security.verify_password(body.password, user["password_hash"]):
        security.record_login_failure(body.username, client_id)
        _audit(
            request,
            "login_failed",
            actor={"id": None, "username": body.username},
            metadata={"reason": "invalid_credentials"},
            status="failure",
        )
        raise _generic_login_error()

    # Defence in depth: role selected at login must match the stored role.
    # Lets an admin choose the wrong radio button; reject explicitly.
    try:
        selected_role = security.normalize_role(body.role)
        stored_role = security.normalize_role(user["role"])
    except security.InvalidRoleError:
        security.record_login_failure(body.username, client_id)
        _audit(
            request,
            "login_failed",
            actor={"id": user["id"], "username": body.username},
            metadata={"reason": "invalid_role", "selected_role": body.role},
            status="failure",
        )
        raise _generic_login_error(status.HTTP_403_FORBIDDEN)
    if stored_role != selected_role:
        security.record_login_failure(body.username, client_id)
        _audit(
            request,
            "login_failed",
            actor={"id": user["id"], "username": body.username},
            metadata={"reason": "role_mismatch", "selected_role": selected_role, "stored_role": stored_role},
            status="failure",
        )
        raise _generic_login_error(status.HTTP_403_FORBIDDEN)

    security.record_login_success(body.username, client_id)
    # ponytail: account state available right now, handiness cached; only public
    # facts used as metadata — disabled flag stored separately, no password/JWT.
    _audit(
        request,
        "login",
        actor={"id": user["id"], "username": body.username},
        target={"id": user["id"], "username": body.username},
        metadata={"role": stored_role},
    )

    token = security.issue_token(user["id"], stored_role)
    kwargs = security.cookie_kwargs()
    kwargs["value"] = token
    response.set_cookie(**kwargs)

    return _post_auth_response(user)


@router.post("/password/change", response_model=LoginResponse)
def change_password(body: ChangePasswordRequest, request: Request, response: Response):
    _require_csrf(request)
    payload = _current_user(
        request,
        require_disclaimer=False,
        require_password_change=False,
    )
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if body.current_password == body.new_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="New password must be different.")
    try:
        security.change_user_password(int(payload["sub"]), body.current_password, body.new_password)
    except security.PasswordVerificationError:
        _audit(
            request,
            "password_change",
            actor={"id": int(payload["sub"]), "username": payload.get("username")},
            target={"id": int(payload["sub"]), "username": payload.get("username")},
            status="failure",
        )
        raise _generic_login_error()
    except security.UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    _audit(
        request,
        "password_change",
        actor={"id": int(payload["sub"]), "username": payload.get("username")},
        target={"id": int(payload["sub"]), "username": payload.get("username")},
    )

    user = security.get_user(payload["username"])
    if user is None or user["disabled"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = security.issue_token(user["id"], user["role"])
    kwargs = security.cookie_kwargs()
    kwargs["value"] = token
    response.set_cookie(**kwargs)
    return _post_auth_response(user)


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(body: RegisterRequest, request: Request):
    """
    Admin-only. The spec says "ask admin to register". An already-signed-in
    admin POSTs the new account. We never expose account creation to
    anonymous callers; we never expose it to non-admins.
    """
    _require_csrf(request)
    payload = _require_admin(request)
    try:
        uid = security.register_user(body.username, body.role, body.password)
    except security.DuplicateUsernameError:
        _audit(
            request,
            "register",
            actor={"id": int(payload["sub"]), "username": payload.get("username")},
            target={"id": None, "username": body.username},
            metadata={"role": body.role},
            status="failure",
        )
        raise HTTPException(status_code=409, detail="Username already exists")
    _audit(
        request,
        "register",
        actor={"id": int(payload["sub"]), "username": payload.get("username")},
        target={"id": uid, "username": body.username},
        metadata={"role": body.role},
    )
    return RegisterResponse(ok=True, user_uuid=security.get_user_by_id(uid)["user_uuid"])


@router.get("/admin/users", response_model=AccountListResponse)
def list_accounts(request: Request):
    _require_admin(request)
    return AccountListResponse(ok=True, users=[_account_response(row) for row in security.list_users()])


@router.get("/admin/audit", response_model=AuditListResponse)
def list_audit(request: Request, limit: int = Query(default=200, ge=1, le=1000), offset: int = Query(default=0, ge=0)):
    """Return auth-owned security events to accepted administrators only."""
    payload = _require_admin(request)
    entries = security.list_audit_entries(limit=limit, offset=offset)
    _audit(
        request,
        "audit_retrieve",
        actor={"id": int(payload["sub"]), "username": payload.get("username")},
        metadata={"limit": limit, "offset": offset},
    )
    return AuditListResponse(
        ok=True,
        entries=[AuditEntry(**{**entry, "client_ip": None}) for entry in entries],
        count=len(entries),
    )


@router.post("/admin/users/{user_id}/disable", response_model=MessageResponse)
def disable_account(user_id: str, request: Request):
    _require_csrf(request)
    payload = _require_admin(request)
    target_user = security.get_user_by_uuid(user_id)
    try:
        security.set_user_disabled(user_id, True, actor_user_id=int(payload["sub"]))
    except (
        security.UserNotFoundError,
        security.SelfManagementError,
        security.LastActiveAdminError,
    ) as exc:
        _audit(
            request,
            "disable",
            actor={"id": int(payload["sub"]), "username": payload.get("username")},
            target={"id": user_id, "username": target_user["username"] if target_user else None},
            status="failure",
            metadata={"reason": type(exc).__name__},
        )
        raise _map_account_management_error(exc)
    _audit(
        request,
        "disable",
        actor={"id": int(payload["sub"]), "username": payload.get("username")},
        target={"id": user_id, "username": target_user["username"] if target_user else None},
    )
    return MessageResponse(ok=True, message="Account disabled.")


@router.post("/admin/users/{user_id}/enable", response_model=MessageResponse)
def enable_account(user_id: str, request: Request):
    _require_csrf(request)
    payload = _require_admin(request)
    target_user = security.get_user_by_uuid(user_id)
    try:
        security.set_user_disabled(user_id, False)
    except security.UserNotFoundError as exc:
        _audit(
            request,
            "enable",
            actor={"id": int(payload["sub"]), "username": payload.get("username")},
            target={"id": user_id, "username": None},
            status="failure",
            metadata={"reason": type(exc).__name__},
        )
        raise _map_account_management_error(exc)
    _audit(
        request,
        "enable",
        actor={"id": int(payload["sub"]), "username": payload.get("username")},
        target={"id": user_id, "username": target_user["username"] if target_user else None},
    )
    return MessageResponse(ok=True, message="Account enabled.")


@router.post("/admin/users/{user_id}/reset-password", response_model=ResetPasswordResponse)
def reset_account_password(user_id: str, body: ResetPasswordRequest, request: Request):
    _require_csrf(request)
    payload = _require_admin(request)
    target_user = security.get_user_by_uuid(user_id)
    try:
        temporary_password = security.reset_user_password(user_id, body.temporary_password)
    except security.UserNotFoundError as exc:
        _audit(
            request,
            "password_reset",
            actor={"id": int(payload["sub"]), "username": payload.get("username")},
            target={"id": user_id, "username": None},
            status="failure",
            metadata={"reason": type(exc).__name__},
        )
        raise _map_account_management_error(exc)
    _audit(
        request,
        "password_reset",
        actor={"id": int(payload["sub"]), "username": payload.get("username")},
        target={"id": user_id, "username": target_user["username"] if target_user else None},
    )
    return ResetPasswordResponse(ok=True, user_uuid=target_user["user_uuid"], temporary_password=temporary_password)


@router.patch("/admin/users/{user_id}/role", response_model=MessageResponse)
def update_account_role(user_id: str, body: UpdateRoleRequest, request: Request):
    _require_csrf(request)
    payload = _require_admin(request)
    target_user = security.get_user_by_uuid(user_id)
    try:
        security.update_user_role(user_id, body.role, actor_user_id=int(payload["sub"]))
    except (
        security.UserNotFoundError,
        security.SelfManagementError,
        security.LastActiveAdminError,
        security.InvalidRoleError,
    ) as exc:
        _audit(
            request,
            "role_update",
            actor={"id": int(payload["sub"]), "username": payload.get("username")},
            target={"id": user_id, "username": target_user["username"] if target_user else None},
            status="failure",
            metadata={"reason": type(exc).__name__, "requested_role": body.role},
        )
        raise _map_account_management_error(exc)
    _audit(
        request,
        "role_update",
        actor={"id": int(payload["sub"]), "username": payload.get("username")},
        target={"id": user_id, "username": target_user["username"] if target_user else None},
        metadata={"requested_role": body.role},
    )
    return MessageResponse(ok=True, message="Role updated.")


@router.get("/disclaimer", response_model=DisclaimerResponse)
def get_disclaimer(request: Request):
    payload = _current_user(request, require_disclaimer=False)
    if payload is None or not security.is_psychiatrist_role(payload.get("role")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    disclaimer = security.current_disclaimer()
    accepted = bool(payload.get("disclaimer_signed"))
    return DisclaimerResponse(
        ok=True,
        version=disclaimer["version"],
        title=disclaimer["title"],
        content_html=disclaimer["content_html"],
        acknowledgement=disclaimer["acknowledgement"],
        accepted=accepted,
        accepted_version=payload.get("disclaimer_version") if accepted else None,
        accepted_at=payload.get("disclaimer_accepted_at") if accepted else None,
        message="Disclaimer already accepted." if accepted else "Disclaimer pending acceptance.",
    )


@router.post("/disclaimer/accept", response_model=LoginResponse)
def accept_disclaimer(request: Request):
    _require_csrf(request)
    payload = _current_user(request, require_disclaimer=False)
    if payload is None or not security.is_psychiatrist_role(payload.get("role")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    security.set_disclaimer_signed(int(payload["sub"]))
    _audit(
        request,
        "disclaimer_accept",
        actor={"id": int(payload["sub"]), "username": payload.get("username")},
        target={"id": int(payload["sub"]), "username": payload.get("username")},
        metadata={"version": security.active_disclaimer_version()},
    )
    return LoginResponse(ok=True, next="/dashboard/user")


def _canonical_session_response(payload: dict) -> SessionResponse:
    expires_at = datetime.fromtimestamp(int(payload["expires_at"]), UTC).isoformat().replace("+00:00", "Z")
    return SessionResponse(
        schemaVersion="1.0.0",
        authenticated=True,
        user=CanonicalUser(
            id=payload["user_uuid"],
            username=payload["username"],
            roles=[security.normalize_role(role) for role in payload.get("roles", [payload["role"]])],
            displayName=payload["username"],
        ),
        session=CanonicalSession(id=payload["session_uuid"], expiresAt=expires_at),
        gates=CanonicalGates(
            disclaimerAccepted=True,
            passwordChangeRequired=False,
        ),
    )


def _legacy_session_response(payload: dict) -> LegacySessionResponse:
    role = security.normalize_role(payload["role"])
    return LegacySessionResponse(
        ok=True,
        user_id=int(payload["sub"]),
        username=payload["username"],
        role=role,
        display_role=_display_role(role),
        disclaimer_status=_disclaimer_status(role, bool(payload["disclaimer_signed"])),
        expires_at=int(payload["expires_at"]),
        message=role,
        clinical_role="psychiatrist" if role == "psychiatrist" else None,
        legacy_role="user" if role == "psychiatrist" else None,
    )


@router.get("/session", response_model=SessionResponse)
def session(request: Request):
    """Canonical UUID session contract for downstream modules."""
    payload = _current_user(request)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return _canonical_session_response(payload)


@router.get("/session/legacy", response_model=LegacySessionResponse)
def legacy_session(request: Request):
    """Compatibility adapter for the pre-UUID flat response."""
    payload = _current_user(request)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return _legacy_session_response(payload)


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, response: Response):
    _require_csrf(request)
    payload = _current_user(request, require_disclaimer=False, require_password_change=False)
    token = request.cookies.get(security.cfg("AUTH_COOKIE_NAME"))
    security.revoke_session(token)
    if payload is not None:
        _audit(
            request,
            "logout",
            actor={"id": int(payload["sub"]), "username": payload.get("username")},
            target={"id": int(payload["sub"]), "username": payload.get("username")},
        )
    kwargs = security.cookie_kwargs()
    # expire cookie by setting max_age=0; starlette handles the rest.
    response.set_cookie(value="", **{**kwargs, "max_age": 0})
    return MessageResponse(ok=True, message="Signed out.")
