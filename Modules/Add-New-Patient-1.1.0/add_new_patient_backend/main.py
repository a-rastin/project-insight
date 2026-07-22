from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from .auth import AuthSessionError, fetch_auth_identity, PSYCHIATRIST_ROLE
from .config import ROOT, settings
from .csrf import CSRF_COOKIE_NAME, CSRF_WRITE_METHODS, csrf_error, generate_csrf_token, request_has_valid_csrf, sign_csrf_token
from .db import SQLiteAdapter
from .models import PatientIntake, generate_patient_code
from .repository import PatientRepository

repo = PatientRepository(SQLiteAdapter(settings.db_path))
repo.initialize()

app = FastAPI(title="Add New Patient Backend")

MODULE_ID = "add-new-patient"
MODULE_TITLE = "Add New Patient"
MODULE_HREF = f"/modules/{MODULE_ID}"
MODULE_ROUTE = {"moduleId": MODULE_ID, "title": MODULE_TITLE, "href": MODULE_HREF}

PUBLIC_FILES = {"index.html", "styles.css", "app.js"}
EMBEDDED_ASSET_PATHS = {
    "styles.css": "styles.css",
    "app.js": "app.js",
    f"{MODULE_ID}/styles.css": "styles.css",
    f"{MODULE_ID}/app.js": "app.js",
}

# ponytail: in-memory mock — matches Dashboard. Persists only for the process.
MOCK_AUTH_USERS = {
    "psy-1": {"id": "psy-1", "username": "psychiatrist", "roles": ["psychiatrist"], "displayName": "Mina Rahimi"},
}
MOCK_AUTH_SESSIONS: dict[str, str] = {}


def public_file_response(filename: str) -> FileResponse:
    if filename not in PUBLIC_FILES:
        raise HTTPException(status_code=404, detail={"message": "Not found."})
    full = ROOT / filename
    if not full.is_file():
        raise HTTPException(status_code=404, detail={"message": "Not found."})
    return FileResponse(full)


def json_error(status_code: int, error: str, detail: str | None = None) -> HTTPException:
    payload: dict[str, Any] = {"error": error}
    if detail:
        payload["detail"] = detail
    return HTTPException(status_code=status_code, detail=payload)


def validation_error_key(loc: tuple[Any, ...]) -> str:
    parts = [str(part) for part in loc if part != "body" and isinstance(part, (str, int))]
    return ".".join(parts)


@app.middleware("http")
async def csrf_middleware(request: Request, call_next: Any) -> JSONResponse:
    if request.method in CSRF_WRITE_METHODS and not request_has_valid_csrf(request):
        return csrf_error()
    return await call_next(request)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"message": str(exc.detail)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors: dict[str, str] = {}
    for err in exc.errors():
        loc = err.get("loc") or ()
        field = validation_error_key(tuple(loc))
        if field:
            msg = err.get("msg", "Invalid value.")
            msg = msg.replace("Value error, ", "")
            errors[field] = msg
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Patient data failed validation.", "errors": errors},
    )


async def require_authenticated_session(request: Request) -> dict[str, Any]:
    try:
        identity = await fetch_auth_identity(request)
    except AuthSessionError as error:
        raise json_error(502, "authentication_session_unavailable", str(error)) from error
    if not identity:
        raise json_error(401, "authentication_session_required")
    return identity


async def require_psychiatrist_or_admin_session(request: Request) -> dict[str, Any]:
    try:
        identity = await fetch_auth_identity(request)
    except AuthSessionError as error:
        raise json_error(502, "authentication_session_unavailable", str(error)) from error
    if not identity:
        raise json_error(401, "authentication_session_required")
    role = (identity.get("user") or {}).get("role")
    if role not in (PSYCHIATRIST_ROLE, "ADMIN"):
        raise json_error(403, "psychiatrist_or_admin_required")
    return identity


async def require_psychiatrist_session(request: Request) -> dict[str, Any]:
    try:
        identity = await fetch_auth_identity(request, require_psychiatrist=True)
    except AuthSessionError as error:
        raise json_error(502, "authentication_session_unavailable", str(error)) from error
    if not identity:
        raise json_error(401, "authentication_session_required")
    return identity


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"module": "Add New Patient", "status": "ok"}


@app.get("/internal/dashboard/module-routes/add-new-patient")
async def dashboard_module_route() -> dict[str, str]:
    return MODULE_ROUTE


@app.get("/api/auth/session")
async def mock_auth_session(request: Request) -> JSONResponse:
    if not settings.use_mock_auth:
        return JSONResponse(status_code=404, content={"error": "not_found"})

    requested_user = request.headers.get("x-demo-auth-user")
    if requested_user:
        user = MOCK_AUTH_USERS.get(requested_user)
        if not user:
            return JSONResponse(status_code=401, content={"authenticated": False})
        session_id = f"mock-auth-{user['id']}"
        MOCK_AUTH_SESSIONS[session_id] = user["id"]
        return JSONResponse(content={"schemaVersion": "1.0.0", "authenticated": True, "session": {"id": session_id, "expiresAt": "2099-01-01T00:00:00Z"}, "user": user, "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False}})

    session_id = request.headers.get("x-auth-session") or request.headers.get("x-auth-session-id")
    user_id = MOCK_AUTH_SESSIONS.get(session_id or "")
    user = MOCK_AUTH_USERS.get(user_id or "")
    if not user:
        return JSONResponse(status_code=401, content={"authenticated": False})
    return JSONResponse(content={"schemaVersion": "1.0.0", "authenticated": True, "session": {"id": session_id, "expiresAt": "2099-01-01T00:00:00Z"}, "user": user, "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False}})


@app.get("/api/add-new-patient/csrf")
async def csrf() -> JSONResponse:
    token = generate_csrf_token()
    response = JSONResponse(content={"csrfToken": token})
    response.set_cookie(
        CSRF_COOKIE_NAME,
        sign_csrf_token(token),
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return response


@app.get("/api/patients")
async def list_patients(_: dict[str, Any] = Depends(require_authenticated_session)) -> dict[str, Any]:
    return {"patients": repo.list_patients()}


@app.post("/api/patients")
async def create_patient(
    payload: PatientIntake,
    identity: dict[str, Any] = Depends(require_psychiatrist_session),
) -> JSONResponse:
    data = payload.to_patient_record()

    if not data.get("patientCode"):
        existing = repo.existing_codes()
        code = generate_patient_code()
        while code in existing:
            code = generate_patient_code()
        data["patientCode"] = code

    try:
        record = repo.create_patient({"id": str(uuid4()), **data}, identity["user"]["id"])
    except Exception:
        if repo.get_patient(data["patientCode"]):
            errors = {"demographics.patientCode": "Patient code already exists. Generate a new code and submit again."}
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"message": "Patient data failed validation.", "errors": errors},
            )
        raise

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"patient": record})


@app.get("/api/patients/{id_or_code}/intake", response_model=None)
async def get_patient_intake(
    id_or_code: str,
    _: dict[str, Any] = Depends(require_psychiatrist_or_admin_session),
) -> dict[str, Any] | JSONResponse:
    result = repo.list_intake_records(id_or_code)
    if not result:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Patient was not found."})
    patient, intake_records = result
    return {"patient": patient, "intakeRecords": intake_records}


@app.get("/api/patients/{id_or_code}", response_model=None)
async def get_patient(
    id_or_code: str,
    _: dict[str, Any] = Depends(require_authenticated_session),
) -> dict[str, Any] | JSONResponse:
    patient = repo.get_patient(id_or_code)
    if not patient:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Patient was not found."})
    return {"patient": patient}


@app.get("/")
async def root() -> FileResponse:
    return public_file_response("index.html")


@app.get("/modules/add-new-patient")
@app.get("/modules/add-new-patient/")
async def embedded_module_shell() -> FileResponse:
    return public_file_response("index.html")


@app.get("/modules/{path:path}")
async def serve_embedded_asset(path: str) -> FileResponse:
    asset = EMBEDDED_ASSET_PATHS.get(path)
    if not asset:
        raise HTTPException(status_code=404, detail={"message": "Not found."})
    return public_file_response(asset)


@app.get("/{path:path}")
async def serve_static(path: str) -> FileResponse:
    # ponytail: allowlist not directory-walk — preserve privacy invariant from old server.
    return public_file_response(path)


# # ponytail: catch-all above handles static allowlist, so no StaticFiles mount.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)
