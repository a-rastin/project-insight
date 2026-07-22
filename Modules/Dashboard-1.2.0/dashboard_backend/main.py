from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .auth import AuthSessionError, fetch_auth_identity
from .config import ROOT, settings
from .db import SQLiteAdapter
from .discovery import ModuleRegistration, discover_module
from .repository import DashboardRepository, now_iso

repo = DashboardRepository(SQLiteAdapter(settings.db_path))
repo.initialize()

app = FastAPI(title="Dashboard Backend")

def json_error(status_code: int, error: str, detail: str | None = None) -> HTTPException:
    payload: dict[str, Any] = {"error": error}
    if detail:
        payload["detail"] = detail
    return HTTPException(status_code=status_code, detail=payload)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


async def parse_json_body(request: Request) -> dict[str, Any]:
    if request.headers.get("content-length") in [None, "0"]:
        return {}
    try:
        return await request.json()
    except Exception:
        return {}


async def require_auth_identity(request: Request, session: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        identity = await fetch_auth_identity(request, session)
    except AuthSessionError as error:
        raise json_error(502, "authentication_session_unavailable", str(error)) from error
    if not identity:
        raise json_error(401, "authentication_session_required")
    return identity


async def require_session(request: Request) -> dict[str, Any]:
    session_id = request.headers.get("x-dashboard-session") or request.cookies.get("insight_dashboard_session")
    session = repo.get_session(session_id)
    if not session:
        raise json_error(401, "dashboard_session_required")

    identity = await require_auth_identity(request, session)
    user = identity["user"]
    if user["id"] != session["userId"]:
        raise json_error(401, "authentication_session_mismatch")

    repo.update_session_auth(
        session["id"], user["id"], user["role"], identity["authSessionId"], identity["authExpiresAt"]
    )
    session["userId"] = user["id"]
    session["role"] = user["role"]
    session["authSessionId"] = identity["authSessionId"]
    session["authExpiresAt"] = identity["authExpiresAt"]
    session["authUser"] = with_dashboard_fields(user, session)
    return session


def with_dashboard_fields(user: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    return {**user, "disclaimerAcceptedAt": session.get("disclaimerAcceptedAt")}


def display_name_for(user: dict[str, Any]) -> str:
    if user["role"] == "PSYCHIATRIST":
        full_name = user["fullName"]
        return full_name if full_name.startswith("Dr. ") else f"Dr. {full_name}"
    return user["fullName"]


def module_route_discovery(module_id: str) -> dict[str, str]:
    return {"method": "GET", "href": f"/internal/dashboard/module-routes/{module_id}"}


def modules_for_role(role: str) -> list[ModuleRegistration]:
    return [module for module in settings.module_registry if role in module.roles]


async def discover_registered_module(module: ModuleRegistration) -> dict[str, Any]:
    discovered = await asyncio.to_thread(discover_module, module, settings.module_discovery_timeout_seconds)
    discovered["id"] = discovered["moduleId"]
    discovered["routeDiscovery"] = module_route_discovery(module.module_id)
    return discovered


async def workspace_for(session: dict[str, Any]) -> dict[str, Any]:
    user = session.get("authUser")
    if not user:
        raise json_error(401, "authentication_session_required")

    modules = modules_for_role(user["role"])
    buttons = list(await asyncio.gather(*(discover_registered_module(module) for module in modules)))
    model: dict[str, Any] = {
        "user": {**user, "displayName": display_name_for(user)},
        "displayName": display_name_for(user),
        "currentDateTime": now_iso(),
        "workspace": {
            "kind": user["role"],
            "title": "Workspace",
            "buttons": buttons,
        },
    }

    if user["role"] == "PSYCHIATRIST":
        model["requiresDisclaimer"] = not user.get("disclaimerAcceptedAt")
        model["disclaimer"] = {
            "acceptedAt": user.get("disclaimerAcceptedAt"),
            "text": "This workspace is a research prototype. It is not a substitute for clinical judgment, emergency care, or licensed guideline review.",
        }

    return model


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"ok": True}


@app.get("/readyz")
async def readyz() -> Any:
    try:
        repo.ping()
    except Exception as error:
        return JSONResponse(status_code=503, content={"ok": False, "error": str(error)})
    return {"ok": True}


@app.post("/internal/dashboard/session")
async def create_dashboard_session(request: Request) -> JSONResponse:
    await parse_json_body(request)
    identity = await require_auth_identity(request)
    user = identity["user"]
    session = repo.create_session(
        str(uuid4()), user["id"], user["role"], identity["authSessionId"], identity["authExpiresAt"]
    )
    session["authUser"] = with_dashboard_fields(user, session)
    repo.record_event(session, "session_created")
    response = JSONResponse(
        status_code=201,
        content={
            "sessionId": session["id"],
            "dashboardUrl": "/dashboard/",
            "user": session["authUser"],
        },
    )
    response.set_cookie("insight_dashboard_session", session["id"], httponly=True, samesite="lax", path="/")
    return response


@app.delete("/internal/dashboard/session")
async def delete_dashboard_session(session: dict[str, Any] = Depends(require_session)) -> dict[str, Any]:
    repo.deactivate_session(session["id"])
    repo.record_event(session, "session_deleted")
    return {"ok": True}


def canonical_uuid(value: Any) -> str | None:
    try:
        return str(UUID(value)) if isinstance(value, str) else None
    except ValueError:
        return None


@app.post("/internal/dashboard/workflow-context")
async def create_workflow_context(request: Request, session: dict[str, Any] = Depends(require_session)) -> JSONResponse:
    body = await parse_json_body(request)
    patient_uuid = canonical_uuid(body.get("patientUuid"))
    encounter_uuid = canonical_uuid(body.get("encounterUuid"))
    if not patient_uuid or not encounter_uuid:
        raise json_error(422, "workflow_context_invalid")
    context_id = str(uuid4())
    repo.create_workflow_context(context_id, session["id"], patient_uuid, encounter_uuid, session["authExpiresAt"])
    repo.record_event(session, "workflow_context_created")
    return JSONResponse(status_code=201, content={"workflowContextId": context_id})


@app.get("/internal/dashboard/workflow-context")
async def workflow_context(request: Request, session: dict[str, Any] = Depends(require_session)) -> dict[str, str]:
    context_id = request.headers.get("x-workflow-context") or request.cookies.get("insight_workflow_context")
    context = repo.get_workflow_context(context_id, session["id"])
    if not context:
        raise json_error(404, "workflow_context_not_available")
    return context


@app.get("/internal/dashboard/workflow-status")
async def workflow_status(request: Request, session: dict[str, Any] = Depends(require_session)) -> dict[str, Any]:
    context_id = request.headers.get("x-workflow-context")
    if not repo.get_workflow_context(context_id, session["id"]):
        raise json_error(404, "workflow_context_not_available")
    modules = await asyncio.gather(*(discover_registered_module(module) for module in modules_for_role(session["role"])))
    return {
        "modules": [
            {"moduleId": module["moduleId"], "status": module["status"], "summary": module["reason"]}
            for module in modules
        ]
    }


@app.get("/internal/dashboard/workspace")
@app.get("/internal/dashboard/summary")
async def workspace(session: dict[str, Any] = Depends(require_session)) -> dict[str, Any]:
    return await workspace_for(session)


@app.get("/internal/dashboard/module-routes/{module_id}")
async def module_route(module_id: str, request: Request, session: dict[str, Any] = Depends(require_session)) -> JSONResponse:
    module = next((item for item in modules_for_role(session["role"]) if item.module_id == module_id), None)
    if not module:
        raise json_error(404, "module_route_not_available")
    discovered = await discover_registered_module(module)
    discovered.pop("id")
    discovered.pop("routeDiscovery")
    context_id = request.headers.get("x-workflow-context")
    if context_id:
        if not repo.get_workflow_context(context_id, session["id"]):
            raise json_error(404, "workflow_context_not_available")
        discovered["workflowContextId"] = context_id
    response = JSONResponse(content=discovered)
    if context_id:
        response.set_cookie("insight_workflow_context", context_id, httponly=True, samesite="lax", path="/modules")
    return response


@app.post("/internal/dashboard/disclaimer/accept")
async def accept_disclaimer(session: dict[str, Any] = Depends(require_session)) -> dict[str, Any]:
    user = session["authUser"]
    if user["role"] != "PSYCHIATRIST":
        raise json_error(403, "psychiatrist_only")
    accepted_at = repo.accept_disclaimer(session["id"])
    session["disclaimerAcceptedAt"] = accepted_at
    session["authUser"] = with_dashboard_fields(user, session)
    repo.record_event(session, "disclaimer_accepted")
    return await workspace_for(session)


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/dashboard/")
async def dashboard_index() -> FileResponse:
    return FileResponse(ROOT / "index.html")


app.mount("/dashboard", StaticFiles(directory=Path(ROOT), html=True), name="dashboard-static")
