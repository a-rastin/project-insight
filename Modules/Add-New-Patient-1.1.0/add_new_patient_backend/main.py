from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from .auth import AuthSessionError, fetch_auth_identity
from .config import ROOT, settings
from .csrf import CSRF_COOKIE_NAME, CSRF_WRITE_METHODS, csrf_error, generate_csrf_token, request_has_valid_csrf, sign_csrf_token
from .db import SQLiteAdapter
from .models import (
    CanonicalEncounterCreate,
    CanonicalPatientCreate,
    PatientIntake,
    SCHEMA_VERSION,
    WorkflowPatientDetailsFinalize,
    generate_patient_code,
)
from .repository import (
    IdempotencyConflict,
    PatientAliasCollision,
    PatientCodeAlreadyExists,
    PatientRepository,
    WorkflowDraftNotReady,
)

repo = PatientRepository(SQLiteAdapter(settings.db_path))
repo.initialize()

app = FastAPI(title="Add New Patient Backend")

MODULE_ID = "add-new-patient"
MODULE_TITLE = "Add New Patient"
MODULE_HREF = f"/modules/{MODULE_ID}/"
MODULE_ROUTE = {"moduleId": MODULE_ID, "title": MODULE_TITLE, "href": MODULE_HREF}

PUBLIC_FILES = {"index.html", "styles.css", "app.js"}
EMBEDDED_ASSET_PATHS = {
    "styles.css": "styles.css",
    "app.js": "app.js",
    f"{MODULE_ID}/styles.css": "styles.css",
    f"{MODULE_ID}/app.js": "app.js",
}

# ponytail: in-memory mock â€” matches Dashboard. Persists only for the process.
MOCK_AUTH_USERS = {
    "psy-1": {"id": "psy-1", "username": "psychiatrist", "roles": ["psychiatrist"], "displayName": "Mina Rahimi"},
}
MOCK_AUTH_SESSIONS: dict[str, str] = {}
PATIENT_UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
PATIENT_CODE_PATTERN = re.compile(r"^[A-Z0-9]{6}$")


def canonical_response(**payload: Any) -> dict[str, Any]:
    return {"schemaVersion": SCHEMA_VERSION, **payload}


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
    internal_workflow_callback = request.url.path.startswith("/internal/workflow-drafts/")
    if request.method in CSRF_WRITE_METHODS and not internal_workflow_callback and not request_has_valid_csrf(request):
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
    if role not in ("PSYCHIATRIST", "ADMIN"):
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


@app.get("/modules/add-new-patient/contract")
async def dashboard_contract() -> dict[str, str]:
    return {
        "moduleId": MODULE_ID,
        "interfaceVersion": "1.0.0",
        "basePath": MODULE_HREF,
    }


@app.get("/modules/add-new-patient/ready")
async def dashboard_ready() -> JSONResponse:
    try:
        repo.ping()
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready"})
    return JSONResponse(content={"status": "ready"})


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
@app.get("/api/add-new-patient/v1/csrf")
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


def ensure_patient_code(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("patientCode"):
        return data
    existing = repo.existing_codes()
    code = generate_patient_code()
    while code in existing:
        code = generate_patient_code()
    return {**data, "patientCode": code}


def workflow_owner(identity: dict[str, Any]) -> tuple[str, str]:
    return identity["user"]["id"], identity["authSessionId"]


def workflow_signature(draft_id: str, patient_code: str, decision: str) -> str:
    return hmac.new(
        settings.workflow_service_secret.encode(),
        f"{draft_id}:{patient_code}:{decision}".encode(),
        hashlib.sha256,
    ).hexdigest()


@app.post("/api/add-new-patient/v1/workflow-drafts")
async def create_workflow_draft(
    identity: dict[str, Any] = Depends(require_psychiatrist_session),
) -> JSONResponse:
    owner_user_id, owner_session_id = workflow_owner(identity)
    draft = repo.create_workflow_draft(owner_user_id, owner_session_id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=canonical_response(workflowDraft=draft))


@app.get("/api/add-new-patient/v1/workflow-drafts/{draft_id}")
async def get_workflow_draft(
    draft_id: str,
    identity: dict[str, Any] = Depends(require_authenticated_session),
) -> JSONResponse:
    owner_user_id, owner_session_id = workflow_owner(identity)
    draft = repo.get_workflow_draft(draft_id, owner_user_id, owner_session_id)
    if not draft:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "workflow_draft_not_found"})
    return JSONResponse(content=canonical_response(workflowDraft=draft))


@app.delete("/api/add-new-patient/v1/workflow-drafts/{draft_id}")
async def cancel_workflow_draft(
    draft_id: str,
    identity: dict[str, Any] = Depends(require_psychiatrist_session),
) -> JSONResponse:
    owner_user_id, owner_session_id = workflow_owner(identity)
    draft = repo.cancel_workflow_draft(draft_id, owner_user_id, owner_session_id)
    if not draft:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "workflow_draft_not_found"})
    return JSONResponse(content=canonical_response(workflowDraft=draft))


@app.get("/api/patients/lookup")
async def lookup_patient_for_diagnosis(
    code: str,
    identity: dict[str, Any] = Depends(require_authenticated_session),
) -> JSONResponse:
    normalized = code.strip().upper()
    if not PATIENT_CODE_PATTERN.fullmatch(normalized):
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "patient_alias_not_found"})
    owner_user_id, owner_session_id = workflow_owner(identity)
    workflow_patient = repo.resolve_workflow_patient(normalized, owner_user_id, owner_session_id)
    if workflow_patient:
        return JSONResponse(content=workflow_patient)
    try:
        patient = repo.resolve_patient(normalized)
    except PatientAliasCollision:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": "patient_alias_collision"})
    if not patient:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "patient_alias_not_found"})
    return JSONResponse(content={
        "id": patient["patientId"],
        "patient_code": patient["patientCode"],
        "display_name": None,
    })


@app.post("/internal/workflow-drafts/{draft_id}/diagnosis-complete")
async def complete_workflow_diagnosis(draft_id: str, request: Request) -> JSONResponse:
    if not settings.workflow_service_secret:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"error": "workflow_service_unavailable"})
    body = await request.json()
    patient_code = str(body.get("patientCode") or "").strip().upper()
    decision = str(body.get("decision") or "")
    signature = request.headers.get("X-Workflow-Signature", "")
    if decision not in {"confirmed", "definite"} or not hmac.compare_digest(
        signature, workflow_signature(draft_id, patient_code, decision)
    ):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"error": "workflow_signature_invalid"})
    draft = repo.complete_workflow_diagnosis(draft_id, patient_code, decision)
    if not draft:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": "workflow_draft_not_ready"})
    return JSONResponse(content=canonical_response(workflowDraft=draft))


@app.post("/api/add-new-patient/v1/workflow-drafts/{draft_id}/finalize")
async def finalize_workflow_draft(
    draft_id: str,
    payload: WorkflowPatientDetailsFinalize,
    identity: dict[str, Any] = Depends(require_psychiatrist_session),
) -> JSONResponse:
    owner_user_id, owner_session_id = workflow_owner(identity)
    try:
        result = repo.finalize_workflow_draft(
            draft_id, owner_user_id, owner_session_id, payload.to_patient_record()
        )
    except WorkflowDraftNotReady:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": "workflow_draft_not_ready"})
    if result is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "workflow_draft_not_found"})
    response_status, response = result
    return JSONResponse(status_code=response_status, content=response)


@app.post("/api/add-new-patient/v1/patients")
async def create_canonical_patient(
    payload: CanonicalPatientCreate,
    identity: dict[str, Any] = Depends(require_psychiatrist_session),
) -> JSONResponse:
    data = ensure_patient_code(payload.to_patient_record())
    try:
        record = repo.create_patient_identity({"id": str(uuid4()), **data}, identity["user"]["id"])
    except PatientCodeAlreadyExists:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": "patient_alias_already_exists", "errors": {"patientCode": "Patient code already exists."}},
        )
    except Exception:
        if repo.get_patient(data["patientCode"]):
            errors = {"patientCode": "Patient code already exists."}
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": "patient_alias_already_exists", "errors": errors})
        raise
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=canonical_response(patient=record))


@app.get("/api/add-new-patient/v1/patient-resolutions/{alias}", response_model=None)
async def resolve_patient_alias(
    alias: str,
    request: Request,
    if_match: str | None = Header(default=None, alias="If-Match"),
    _: dict[str, Any] = Depends(require_authenticated_session),
) -> JSONResponse:
    normalized = alias.strip()
    if PATIENT_CODE_PATTERN.fullmatch(normalized.upper()):
        normalized = normalized.upper()
    elif not PATIENT_UUID_PATTERN.fullmatch(normalized):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "invalid_patient_code"})
    try:
        resolution = repo.resolve_patient(normalized)
    except PatientAliasCollision:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": "patient_alias_collision"})
    if not resolution:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "patient_alias_not_found"})
    if if_match is not None and if_match != resolution["etag"]:
        return JSONResponse(status_code=status.HTTP_412_PRECONDITION_FAILED, content={"error": "etag_mismatch"})
    return JSONResponse(content=canonical_response(**resolution), headers={"ETag": resolution["etag"]})


@app.get("/api/add-new-patient/v1/patients/{patient_id}", response_model=None)
async def get_canonical_patient(
    patient_id: str,
    _: dict[str, Any] = Depends(require_authenticated_session),
) -> dict[str, Any] | JSONResponse:
    patient = repo.get_patient_identity(patient_id)
    if not patient:
        resolved = repo.get_patient(patient_id)
        patient = repo.get_patient_identity(resolved["id"]) if resolved else None
    if not patient:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Patient was not found."})
    return canonical_response(patient=patient)


@app.post("/api/add-new-patient/v1/encounters")
async def create_canonical_encounter(
    payload: CanonicalEncounterCreate,
    identity: dict[str, Any] = Depends(require_psychiatrist_session),
) -> JSONResponse:
    record = repo.create_encounter(payload.to_encounter_record(), identity["user"]["id"])
    if not record:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Patient was not found."})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=canonical_response(encounter=record))


@app.get("/api/add-new-patient/v1/encounters/{encounter_id}", response_model=None)
async def get_canonical_encounter(
    encounter_id: str,
    _: dict[str, Any] = Depends(require_authenticated_session),
) -> dict[str, Any] | JSONResponse:
    encounter = repo.get_encounter(encounter_id)
    if not encounter:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Encounter was not found."})
    return canonical_response(encounter=encounter)


@app.get("/api/patients")
@app.get("/api/add-new-patient/v1/patients")
async def list_patients(_: dict[str, Any] = Depends(require_authenticated_session)) -> dict[str, Any]:
    return {"schemaVersion": SCHEMA_VERSION, "patients": repo.list_patients()}


@app.post("/api/patients")
@app.post("/api/add-new-patient/v1/intakes")
async def create_patient(
    payload: PatientIntake,
    identity: dict[str, Any] = Depends(require_psychiatrist_session),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> JSONResponse:
    data = payload.to_patient_record()
    request_hash = hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    try:
        response_status, response = repo.create_patient_with_encounter(
            {"id": str(uuid4()), **data},
            identity["user"]["id"],
            idempotency_key=idempotency_key.strip() if idempotency_key else None,
            request_hash=request_hash,
        )
    except IdempotencyConflict:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": "idempotency_key_reused"})
    except PatientCodeAlreadyExists:
        errors = {"demographics.patientCode": "Patient code already exists. Generate a new code and submit again."}
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "Patient data failed validation.", "errors": errors},
        )
    except Exception:
        if data.get("patientCode") and repo.get_patient(data["patientCode"]):
            errors = {"demographics.patientCode": "Patient code already exists. Generate a new code and submit again."}
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"message": "Patient data failed validation.", "errors": errors},
            )
        raise
    return JSONResponse(status_code=response_status, content=response)

@app.get("/api/patients/{id_or_code}/intake", response_model=None)
async def get_patient_intake(
    id_or_code: str,
    _: dict[str, Any] = Depends(require_psychiatrist_or_admin_session),
) -> dict[str, Any] | JSONResponse:
    result = repo.list_intake_records(id_or_code)
    if not result:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Patient was not found."})
    patient, intake_records = result
    return {"schemaVersion": SCHEMA_VERSION, "patient": patient, "intakeRecords": intake_records}


@app.get("/api/patients/{id_or_code}", response_model=None)
async def get_patient(
    id_or_code: str,
    _: dict[str, Any] = Depends(require_authenticated_session),
) -> dict[str, Any] | JSONResponse:
    patient = repo.get_patient(id_or_code)
    if not patient:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Patient was not found."})
    return canonical_response(patient=patient)


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
    # ponytail: allowlist not directory-walk â€” preserve privacy invariant from old server.
    return public_file_response(path)


# # ponytail: catch-all above handles static allowlist, so no StaticFiles mount.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)
