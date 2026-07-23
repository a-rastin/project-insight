from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import Body, Depends, FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from clinical_graph_models import (
    DECISION_IDS,
    ERROR_CODES,
    MODULE_ID,
    PERMISSIONS,
    ROLE_PERMISSIONS,
    XmlBifCompileError,
    compile_xmlbif,
    contract_payload,
    error_response,
    evaluate_posterior,
    ok_response,
    validate_model,
)
from clinical_graph_models.model import ClinicalGraphModel

from .auth_adapter import AuthenticationRestAdapter, CsrfError, SessionAdapter, SessionState, assert_csrf_token
from .config import BnManagerSettings, get_settings
from .evaluation_store import (
    EvaluationStore,
    IdempotencyConflict,
    SqliteEvaluationStore,
    build_canonical_evaluation,
)
from .evidence_schema import build_evidence_schema, model_content_hash
from .model_governance import (
    ClinicalStatus,
    MissingGovernanceKey,
    ModelGovernanceStore,
    ModelNotApproved,
    SignedApproval,
    clinical_status_for,
    sign_approval,
    verify_approval,
)
from .model_registry import (
    ModelRegistryEntry,
    get_registry_entry,
    list_registry_entries,
    read_registry_model,
    read_registry_schema,
)

ADMIN_ROLES = frozenset({"admin"})
DASHBOARD_DISCOVERY_PATH = "/internal/dashboard/module-routes/bn-manager"


class BnManagerHttpError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def create_app(
    settings: BnManagerSettings | None = None,
    session_adapter: SessionAdapter | None = None,
    evaluation_store: EvaluationStore | None = None,
    governance_store: ModelGovernanceStore | None = None,
    governance_key: bytes | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=contract_payload()["contract_version"],
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    app.state.session_adapter = session_adapter or AuthenticationRestAdapter(
        settings.auth_session_url,
        settings.auth_timeout_seconds,
    )
    app.state.evaluation_store = evaluation_store or SqliteEvaluationStore(settings.database_path)
    app.state.governance_store = governance_store
    app.state.governance_key = governance_key

    @app.exception_handler(BnManagerHttpError)
    def bn_manager_error(request: Request, exc: BnManagerHttpError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                exc.code,
                exc.message,
                request_id=request.headers.get("x-request-id"),
                details=exc.details,
            ),
        )

    def require_verified_session(request: Request) -> SessionState:
        adapter: SessionAdapter = request.app.state.session_adapter
        session = adapter.fetch_session(request)
        if session.expired:
            raise BnManagerHttpError(401, ERROR_CODES["unauthorized"], "Authentication session expired.")
        if not session.active:
            details = {"reason": session.blocked_reason} if session.blocked_reason else {}
            code = ERROR_CODES["forbidden"] if session.blocked_reason else ERROR_CODES["unauthorized"]
            status = 403 if session.blocked_reason else 401
            message = "Authentication session is blocked." if session.blocked_reason else "Authentication session is missing or invalid."
            raise BnManagerHttpError(status, code, message, details)
        return session

    def require_roles(allowed_roles: frozenset[str]):
        def dependency(request: Request, session: SessionState = Depends(require_verified_session)) -> SessionState:
            try:
                assert_csrf_token(request, session, settings.csrf_header_name)
            except CsrfError as exc:
                raise BnManagerHttpError(403, ERROR_CODES["forbidden"], "CSRF token missing or invalid.") from exc
            if session.roles.isdisjoint(allowed_roles):
                raise BnManagerHttpError(
                    403,
                    ERROR_CODES["forbidden"],
                    "Authenticated user does not have a required BN Manager role.",
                    {"required_roles": sorted(allowed_roles), "roles": sorted(session.roles)},
                )
            return session

        return dependency

    def require_permission(permission: str):
        allowed_roles = frozenset(
            role.lower()
            for role, permissions in ROLE_PERMISSIONS.items()
            if permission in permissions
        )
        return require_roles(allowed_roles)

    @app.get(f"{settings.api_prefix}/health")
    def health() -> dict[str, Any]:
        return ok_response(
            {
                "status": "healthy",
                "module_id": MODULE_ID,
            }
        )

    @app.get(f"{settings.api_prefix}/ready")
    def ready() -> dict[str, Any]:
        static_index = settings.static_dir / "index.html"
        return ok_response(
            {
                "status": "ready",
                "module_id": MODULE_ID,
                "static_ui": static_index.exists(),
                "contract_loaded": contract_payload()["module_id"] == MODULE_ID,
            }
        )

    @app.get("/api/bn-manager/v1/contract")
    def contract() -> dict[str, Any]:
        return ok_response(contract_payload())

    @app.get("/api/bn-manager/v1/models")
    def model_registry_list() -> dict[str, Any]:
        return ok_response(
            {
                "models": list_registry_entries(),
                "schema": {
                    "format": "XML",
                    "version": "0.3",
                    "path": "schemas/XSD.xml",
                },
            }
        )

    @app.get("/api/bn-manager/v1/models/schema/xml-0.3")
    def model_registry_schema() -> dict[str, Any]:
        return ok_response(
            {
                "format": "XML",
                "version": "0.3",
                "mime_type": "application/xml",
                "text": read_registry_schema(),
            }
        )

    @app.get("/api/bn-manager/v1/models/{stable_id}/schema")
    def model_evidence_schema(
        stable_id: str,
        request: Request,
    ) -> dict[str, Any]:
        store: ModelGovernanceStore | None = request.app.state.governance_store
        return ok_response(_registry_evidence_schema(stable_id, governance_store=store))

    @app.get("/api/bn-manager/v1/models/{stable_id}")
    def model_registry_detail(
        stable_id: str,
        request: Request,
    ) -> dict[str, Any]:
        try:
            entry, text = read_registry_model(stable_id)
        except KeyError as exc:
            raise BnManagerHttpError(
                404,
                ERROR_CODES["model_not_found"],
                "BN Manager registry model not found.",
                {"stable_id": stable_id},
            ) from exc
        except ValueError as exc:
            raise BnManagerHttpError(404, ERROR_CODES["invalid_request"], "BN Manager registry file not found.") from exc
        store: ModelGovernanceStore | None = request.app.state.governance_store
        evidence_schema = _evidence_schema_for_registry(entry, text, governance_store=store)
        return ok_response(
            {
                "model": entry.payload(),
                "format": "XML",
                "version": "0.3",
                "mime_type": "application/xml",
                "text": text,
                "evidence_schema": evidence_schema,
                "model_version": evidence_schema["model_version"],
                "model_hash": evidence_schema["model_hash"],
                "target": evidence_schema["target"],
            }
        )

    @app.get(DASHBOARD_DISCOVERY_PATH)
    def dashboard_module_route_discovery() -> dict[str, Any]:
        return {
            "module_id": MODULE_ID,
            "name": settings.app_name,
            "routes": [
                {
                    "id": MODULE_ID,
                    "label": settings.app_name,
                    "path": settings.ui_mount_path,
                    "kind": "module-placeholder",
                    "embed": True,
                    "requires_verified_session": True,
                }
            ],
        }

    @app.post("/api/bn-manager/v1/dashboard/evaluate")
    def dashboard_evaluate(
        request: Request,
        payload: dict[str, Any] = Body(...),
        session: SessionState = Depends(require_permission(PERMISSIONS["evaluate_dashboard"])),
    ) -> dict[str, Any]:
        return evaluate_payload(payload, "Dashboard", session, request)

    @app.post("/api/bn-manager/v1/add-new-patient/evaluate")
    def add_new_patient_evaluate(
        request: Request,
        payload: dict[str, Any] = Body(...),
        session: SessionState = Depends(require_permission(PERMISSIONS["evaluate_add_new_patient"])),
    ) -> dict[str, Any]:
        return evaluate_payload(payload, "Add New Patient", session, request)

    @app.post("/api/bn-manager/v1/follow-up/evaluate")
    def follow_up_evaluate(
        request: Request,
        payload: dict[str, Any] = Body(...),
        session: SessionState = Depends(require_permission(PERMISSIONS["evaluate_follow_up"])),
    ) -> dict[str, Any]:
        return evaluate_payload(payload, "Follow-up", session, request)

    @app.post("/api/bn-manager/v1/treatment-plan/evaluate")
    def treatment_plan_evaluate(
        request: Request,
        payload: dict[str, Any] = Body(...),
        session: SessionState = Depends(require_permission(PERMISSIONS["evaluate_treatment_plan"])),
    ) -> dict[str, Any]:
        return evaluate_payload(payload, "Treatment Plan", session, request)

    @app.post("/api/bn-manager/v1/models/validate")
    def model_validate(
        payload: dict[str, Any] = Body(...),
        session: SessionState = Depends(require_roles(ADMIN_ROLES)),
    ) -> dict[str, Any]:
        model = _load_model(payload)
        target_node_ids = _validate_targets(payload)
        messages = [
            asdict(message)
            for message in validate_model(model, target_node_ids=target_node_ids)
        ]
        return ok_response(
            {
                "valid": not any(message["severity"] == "error" for message in messages),
                "messages": messages,
                "checked_by": session.subject,
            }
        )

    def _load_registry_entry_for_governance(stable_id: str) -> ModelRegistryEntry:
        try:
            entry, _text = read_registry_model(stable_id)
        except KeyError as exc:
            raise BnManagerHttpError(
                404,
                ERROR_CODES["model_not_found"],
                "BN Manager registry model not found.",
                {"stable_id": stable_id},
            ) from exc
        except ValueError as exc:
            raise BnManagerHttpError(404, ERROR_CODES["invalid_request"], "BN Manager registry file not found.") from exc
        return entry

    def _resolve_governance(request: Request) -> tuple[ModelGovernanceStore | None, bytes | None]:
        store: ModelGovernanceStore | None = request.app.state.governance_store
        key: bytes | None = request.app.state.governance_key
        return store, key

    @app.get("/api/bn-manager/v1/models/{stable_id}/governance")
    def model_governance_status(
        stable_id: str,
        request: Request,
        session: SessionState = Depends(require_permission(PERMISSIONS["validate_model"])),
    ) -> dict[str, Any]:
        _load_registry_entry_for_governance(stable_id)
        store, _key = _resolve_governance(request)
        clinical_status, signed_approval = clinical_status_for(stable_id, store)
        return ok_response(
            {
                "stable_id": stable_id,
                "clinical_status": clinical_status.value,
                "signed_approval": signed_approval.to_dict() if signed_approval is not None else None,
                "reviewed_by": session.subject,
            }
        )

    @app.post("/api/bn-manager/v1/models/{stable_id}/approve")
    def model_approve(
        stable_id: str,
        request: Request,
        payload: dict[str, Any] = Body(...),
        session: SessionState = Depends(require_permission(PERMISSIONS["govern_model"])),
    ) -> dict[str, Any]:
        entry = _load_registry_entry_for_governance(stable_id)
        store, key = _resolve_governance(request)
        if store is None or not key:
            raise BnManagerHttpError(
                503,
                ERROR_CODES["governance_key_unavailable"],
                "BN Manager governance signing key is not configured.",
                {"stable_id": stable_id},
            )
        _, text = read_registry_model(stable_id)
        approved_by = str(payload.get("approved_by") or session.subject or "")
        approved_at = str(payload.get("approved_at") or datetime.now(UTC).isoformat())
        rationale = str(payload.get("rationale") or "")
        try:
            signature = sign_approval(
                stable_id=stable_id,
                status=ClinicalStatus.APPROVED,
                model_hash=model_content_hash(text),
                approved_at=approved_at,
                approved_by=approved_by,
                secret_key=key,
            )
        except MissingGovernanceKey as exc:
            raise BnManagerHttpError(
                503,
                ERROR_CODES["governance_key_unavailable"],
                "BN Manager governance signing key is not configured.",
                {"stable_id": stable_id},
            ) from exc
        approval = SignedApproval(
            stable_id=stable_id,
            status=ClinicalStatus.APPROVED,
            model_hash=model_content_hash(text),
            approved_at=approved_at,
            approved_by=approved_by,
            signature=signature,
        )
        if not verify_approval(approval, key):
            raise BnManagerHttpError(
                503,
                ERROR_CODES["governance_key_unavailable"],
                "Signed approval failed verification against the configured governance key.",
                {"stable_id": stable_id},
            )
        store.put(approval)
        return JSONResponse(
            status_code=201,
            content=ok_response(
                {
                    "stable_id": stable_id,
                    "clinical_status": ClinicalStatus.APPROVED.value,
                    "signed_approval": approval.to_dict(),
                    "rationale": rationale,
                },
                request_id=request.headers.get("x-request-id"),
            ),
        )

    @app.post("/api/bn-manager/v1/models/{stable_id}/retire")
    def model_retire(
        stable_id: str,
        request: Request,
        payload: dict[str, Any] = Body(...),
        session: SessionState = Depends(require_permission(PERMISSIONS["govern_model"])),
    ) -> dict[str, Any]:
        _load_registry_entry_for_governance(stable_id)
        store, key = _resolve_governance(request)
        if store is None or not key:
            raise BnManagerHttpError(
                503,
                ERROR_CODES["governance_key_unavailable"],
                "BN Manager governance signing key is not configured.",
                {"stable_id": stable_id},
            )
        existing = store.get(stable_id)
        if existing is None or existing.status != ClinicalStatus.APPROVED:
            raise BnManagerHttpError(
                409,
                ERROR_CODES["model_not_approved"],
                "BN Manager model cannot be retired without a prior approved status.",
                {"stable_id": stable_id},
            )
        _, text = read_registry_model(stable_id)
        retired_by = str(payload.get("retired_by") or session.subject or "")
        retired_at = str(payload.get("retired_at") or datetime.now(UTC).isoformat())
        rationale = str(payload.get("rationale") or "")
        signature = sign_approval(
            stable_id=stable_id,
            status=ClinicalStatus.RETIRED,
            model_hash=model_content_hash(text),
            approved_at=retired_at,
            approved_by=retired_by,
            secret_key=key,
        )
        approval = SignedApproval(
            stable_id=stable_id,
            status=ClinicalStatus.RETIRED,
            model_hash=model_content_hash(text),
            approved_at=retired_at,
            approved_by=retired_by,
            signature=signature,
        )
        if not verify_approval(approval, key):
            raise BnManagerHttpError(
                503,
                ERROR_CODES["governance_key_unavailable"],
                "Signed approval failed verification against the configured governance key.",
                {"stable_id": stable_id},
            )
        store.put(approval)
        return ok_response(
            {
                "stable_id": stable_id,
                "clinical_status": ClinicalStatus.RETIRED.value,
                "signed_approval": approval.to_dict(),
                "rationale": rationale,
            },
            request_id=request.headers.get("x-request-id"),
        )

    @app.post("/api/bn-manager/v1/models/{stable_id}/revoke")
    def model_revoke(
        stable_id: str,
        request: Request,
        session: SessionState = Depends(require_permission(PERMISSIONS["govern_model"])),
    ) -> dict[str, Any]:
        _load_registry_entry_for_governance(stable_id)
        store, _key = _resolve_governance(request)
        if store is not None:
            store.delete(stable_id)
        return ok_response(
            {
                "stable_id": stable_id,
                "clinical_status": ClinicalStatus.UNVALIDATED.value,
                "signed_approval": None,
                "revoked_by": session.subject,
            },
            request_id=request.headers.get("x-request-id"),
        )

    index_path = settings.static_dir / "index.html"

    @app.get(settings.ui_mount_path, include_in_schema=False)
    def ui_index(session: SessionState = Depends(require_verified_session)) -> FileResponse:
        return FileResponse(index_path)

    @app.get(f"{settings.ui_mount_path}/{{asset_path:path}}", include_in_schema=False)
    def ui_asset(asset_path: str, session: SessionState = Depends(require_verified_session)) -> FileResponse:
        static_dir = Path(settings.static_dir).resolve()
        if not asset_path:
            return FileResponse(index_path)
        path = (static_dir / asset_path).resolve()
        if static_dir not in (path, *path.parents) or not path.is_file():
            raise BnManagerHttpError(404, ERROR_CODES["invalid_request"], "BN Manager UI asset not found.")
        return FileResponse(path)

    return app


app = create_app()


def _registry_evidence_schema(
    stable_id: str,
    *,
    governance_store: ModelGovernanceStore | None = None,
) -> dict[str, Any]:
    try:
        entry, text = read_registry_model(stable_id)
    except KeyError as exc:
        raise BnManagerHttpError(
            404,
            ERROR_CODES["model_not_found"],
            "BN Manager registry model not found.",
            {"stable_id": stable_id},
        ) from exc
    except ValueError as exc:
        raise BnManagerHttpError(404, ERROR_CODES["invalid_request"], "BN Manager registry file not found.") from exc
    return _evidence_schema_for_registry(entry, text, governance_store=governance_store)


def _evidence_schema_for_registry(
    entry: ModelRegistryEntry,
    text: str,
    *,
    governance_store: ModelGovernanceStore | None = None,
) -> dict[str, Any]:
    try:
        model = compile_xmlbif(text, schema_text=read_registry_schema())
        return build_evidence_schema(entry, model, text, governance_store=governance_store)
    except XmlBifCompileError as exc:
        raise BnManagerHttpError(
            400,
            ERROR_CODES["model_parse_failed"],
            str(exc),
            exc.details(),
        ) from exc
    except KeyError as exc:
        raise BnManagerHttpError(
            404,
            ERROR_CODES["unknown_target_node"],
            f"Registry target node missing from model: {exc}",
            {"stable_id": entry.stable_id, "target": entry.target_node},
        ) from exc


def evaluate_payload(
    payload: dict[str, Any],
    surface: str,
    session: SessionState,
    request: Request,
) -> dict[str, Any]:
    model_payload = payload.get("model") if isinstance(payload.get("model"), dict) else payload
    stable_id = str(model_payload.get("stable_id") or model_payload.get("model_id") or "").strip()
    model, model_text, registry_entry = _load_model_with_provenance(payload)
    messages = [asdict(message) for message in validate_model(model)]
    if any(message["severity"] == "error" for message in messages):
        raise BnManagerHttpError(
            422,
            ERROR_CODES["model_validation_failed"],
            "Model parsed but failed validation.",
            {"messages": messages},
        )

    target = _target_node(payload)
    supplied_evidence = payload.get("evidence") or {}
    if not isinstance(supplied_evidence, dict):
        raise BnManagerHttpError(400, ERROR_CODES["invalid_request"], "evidence must be an object.")

    try:
        result = evaluate_posterior(model, target, supplied_evidence)
    except KeyError as exc:
        raise BnManagerHttpError(
            404,
            ERROR_CODES["unknown_target_node"],
            str(exc),
            {"target": target},
        ) from exc
    except ValueError as exc:
        raise BnManagerHttpError(
            422,
            ERROR_CODES["evaluation_failed"],
            str(exc),
            {"target": target},
        ) from exc

    model_id = stable_id or (registry_entry.stable_id if registry_entry is not None else "inline")
    model_version = registry_entry.active_version if registry_entry is not None else "inline"
    model_hash = model_content_hash(model_text)
    allowed_evidence = {
        node.name: frozenset(node.states)
        for node in model.nodes
        if node.kind == "chance" and node.name != target
    }
    request_id = request.headers.get("x-request-id")
    idempotency_key = _idempotency_key(request, payload, request_id)
    caller = {
        "subject": session.subject,
        "surface": surface,
        "roles": sorted(session.roles),
    }
    request_metadata = {
        "request_id": request_id,
        "decision_id": payload.get("decision_id") or payload.get("target_decision_id"),
        "model_id": model_id,
    }
    record = build_canonical_evaluation(
        model_id=model_id,
        model_version=model_version,
        model_hash=model_hash,
        target=result.target,
        posterior=result.values,
        supplied_evidence=supplied_evidence,
        allowed_evidence=allowed_evidence,
        warnings=messages,
        caller=caller,
        request_metadata=request_metadata,
        idempotency_key=idempotency_key,
    )
    store: EvaluationStore = request.app.state.evaluation_store
    try:
        stored = store.put(record)
    except IdempotencyConflict as exc:
        raise BnManagerHttpError(
            409,
            ERROR_CODES["idempotency_conflict"],
            str(exc),
            {"idempotency_key": idempotency_key},
        ) from exc

    return ok_response(
        {
            "surface": surface,
            "target": stored.target,
            "values": stored.posterior,
            "rankings": [
                {"state": state, "probability": value}
                for state, value in sorted(stored.posterior.items(), key=lambda item: item[1], reverse=True)
            ],
            "warnings": list(stored.warnings) if stored.warnings else messages,
            "evaluated_by": session.subject,
            "evaluation": stored.to_dict(),
        },
        request_id=request_id,
    )


def _idempotency_key(request: Request, payload: dict[str, Any], request_id: str | None) -> str:
    header = request.headers.get("idempotency-key") or request.headers.get("x-idempotency-key")
    if header and str(header).strip():
        return str(header).strip()
    body_key = payload.get("idempotency_key") or payload.get("idempotencyKey")
    if body_key and str(body_key).strip():
        return str(body_key).strip()
    if request_id and str(request_id).strip():
        return f"request:{request_id.strip()}"
    return f"auto:{uuid4()}"


def _load_model_with_provenance(
    payload: dict[str, Any],
) -> tuple[ClinicalGraphModel, str, ModelRegistryEntry | None]:
    model_payload = payload.get("model") if isinstance(payload.get("model"), dict) else payload
    text = str(model_payload.get("text") or model_payload.get("model_text") or "").strip()
    stable_id = str(model_payload.get("stable_id") or model_payload.get("model_id") or "").strip()
    registry_entry: ModelRegistryEntry | None = None
    if not text and stable_id:
        try:
            registry_entry, text = read_registry_model(stable_id)
        except KeyError as exc:
            raise BnManagerHttpError(
                404,
                ERROR_CODES["model_not_found"],
                "BN Manager registry model not found.",
                {"stable_id": stable_id},
            ) from exc
    elif stable_id:
        registry_entry = get_registry_entry(stable_id)
    if not text:
        raise BnManagerHttpError(400, ERROR_CODES["invalid_request"], "XML model text or model_id is required.")

    format_name = str(model_payload.get("format") or model_payload.get("model_format") or "XML").strip().lower()
    if format_name not in {"xml", ".xml", "bif-0.3", "application/xml"}:
        raise BnManagerHttpError(
            415,
            ERROR_CODES["unsupported_format"],
            "Model format must be XML using the module XSD.xml schema.",
            {"format": format_name},
        )
    try:
        model = compile_xmlbif(text, schema_text=read_registry_schema())
    except XmlBifCompileError as exc:
        raise BnManagerHttpError(
            400,
            ERROR_CODES["model_parse_failed"],
            str(exc),
            exc.details(),
        ) from exc
    return model, text, registry_entry


def _load_model(payload: dict[str, Any]) -> ClinicalGraphModel:
    model, _text, _entry = _load_model_with_provenance(payload)
    return model


def _target_node(payload: dict[str, Any]) -> str:
    explicit = payload.get("target_node_id") or payload.get("target")
    if explicit:
        return str(explicit)
    model_payload = payload.get("model") if isinstance(payload.get("model"), dict) else payload
    stable_id = str(model_payload.get("stable_id") or model_payload.get("model_id") or "").strip()
    if stable_id:
        entry = get_registry_entry(stable_id)
        if entry is not None:
            return entry.target_node
    decision_id = str(payload.get("target_decision_id") or payload.get("decision_id") or "pharmacotherapy")
    target = DECISION_IDS.get(decision_id)
    if target is None:
        raise BnManagerHttpError(
            404,
            ERROR_CODES["unknown_target_node"],
            "Unknown BN Manager decision id.",
            {"decision_id": decision_id},
        )
    return target


def _validate_targets(payload: dict[str, Any]) -> list[str] | None:
    """Resolve caller-supplied target nodes for the validate endpoint.

    Returns ``None`` when the caller did not name any target so the semantic
    validator skips the target-node existence check (a caller may be auditing a
    model that is not tied to a known decision). Explicit node ids win; declared
    decision ids resolve through the frozen contract.
    """
    explicit_nodes: list[str] = []
    raw_node = payload.get("target_node_id") or payload.get("target")
    raw_nodes = payload.get("target_node_ids")
    if isinstance(raw_nodes, list):
        explicit_nodes.extend(str(item) for item in raw_nodes if item)
    elif raw_node:
        explicit_nodes.append(str(raw_node))

    decision_ids: list[str] = []
    raw_decision = payload.get("target_decision_id") or payload.get("decision_id")
    raw_decisions = payload.get("target_decision_ids")
    if isinstance(raw_decisions, list):
        decision_ids.extend(str(item) for item in raw_decisions if item)
    elif raw_decision:
        decision_ids.append(str(raw_decision))

    if not explicit_nodes and not decision_ids:
        return None

    targets: list[str] = list(explicit_nodes)
    for decision_id in decision_ids:
        resolved = DECISION_IDS.get(decision_id)
        if resolved is None:
            raise BnManagerHttpError(
                404,
                ERROR_CODES["unknown_target_node"],
                "Unknown BN Manager decision id.",
                {"decision_id": decision_id},
            )
        if resolved not in targets:
            targets.append(resolved)
    return targets or None
