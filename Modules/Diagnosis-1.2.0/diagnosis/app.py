"""Standalone FastAPI app for the diagnosis module.

Usage:
    python -m diagnosis                # boots uvicorn on :8000
    uvicorn diagnosis.app:app --reload

Mount inside the larger Insight app instead:
    from diagnosis import router
    app.include_router(router, prefix="/diagnosis")
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import router
from .config import settings
from .readiness import check_readiness


app = FastAPI(
    title="Insight - Diagnosis",
    version="0.1.0",
    description="DSM-5-TR schizophrenia criteria checklist. Clinician-controlled diagnostic support.",
)

# CORS origins sourced from the settings adapter (`DIAGNOSIS_CORS_ORIGINS`
# comma list, default `*` for localdev — ponytail: tighten via env when
# deployed). Only affects standalone mode; when mounted in Insight the
# parent app owns CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_methods=["GET", "PUT", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {"ok": True, "module": "diagnosis"}


# ponytail: readiness answers "are this module's dependencies up?" —
# live DB probe + auth / patient config shape (never the secret).
# 503 when any check fails so a load balancer holds traffic; the body
# carries which check went False so the operator sees the cause without
# a stack trace and without leaking infra details (no URLs, no paths).
@app.get("/ready")
def ready():
    state = check_readiness()
    if not state["ok"]:
        return JSONResponse(status_code=503, content=state)
    return state
