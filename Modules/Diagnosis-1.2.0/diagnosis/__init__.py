"""diagnosis module — DSM-5-TR schizophrenia criteria checklist for Insight.

Deep module: small REST interface (GET/PUT by patient code) hides the
DSM-5-TR evaluation logic. Standalone web app via `python -m diagnosis`.
Mountable as an APIRouter inside the larger Insight app.

ponytail: SQLite-backed repository adapter (`store.DiagnosisStore`) replaces
the prior in-memory dict; single-process, WAL journal, route contract stable.

Authentication: every protected route calls the Insight auth service at
``AUTH_BASE_URL/api/auth/session`` and enforces role membership there —
this module never decodes JWTs and never reads the auth DB. Writes
require ``psychiatrist``; reads accept ``psychiatrist`` or ``admin``.
See ``auth.py`` for the contract and ``api.py`` for the wire-up.

Patient identity: write routes bind ``sessions.patient_id`` to the
canonical INSIGHT ``patient.id`` via internal REST lookup against the
"Add New Patient" registry (``patient.py``). No DB imports, no
primitives-app imports — the adapter forwards the incoming ``Cookie``
and reads the JSON back, mirroring ``auth.py``. Opt-in via
``DIAGNOSIS_PATIENT_LOOKUP=1``; default disabled preserves the prior
diagnosis-local identity for the self-check and offline tests.
"""
# Keep the package boundary light: the criteria engine and readiness function
# are pure imports, while the router pulls in FastAPI, storage, and auth.
def get_app():
    from .app import app
    return app


def __getattr__(name: str):
    if name == "router":
        from .api import router
        return router
    if name in {
        "UnsupportedDiagnosis",
        "evaluate",
        "get_criteria",
        "meta_contract",
        "supported_clinical_scope",
    }:
        from . import criteria
        return getattr(criteria, name)
    if name == "check_readiness":
        from .readiness import check_readiness
        return check_readiness
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "router",
    "evaluate",
    "get_criteria",
    "meta_contract",
    "supported_clinical_scope",
    "UnsupportedDiagnosis",
    "get_app",
    "check_readiness",
]
