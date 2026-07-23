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

from .api import router
from .config import settings
from .contract import install_common_routes


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

# The shared adapter owns common health, readiness, contract, schema, request
# ID, and correlation ID behavior. Module-local readiness remains available via
# ``diagnosis.readiness.check_readiness`` for detailed operator diagnostics.
install_common_routes(app)
