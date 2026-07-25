import os

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

try:
    from . import security
    from .contract import contract_payload, openapi_document, schema
    from .router import HealthResponse, ReadinessResponse, _require_admin, liveness, readiness, router
except ImportError:  # Keeps `python main.py` working from this directory.
    import security
    from contract import contract_payload, openapi_document, schema
    from router import HealthResponse, ReadinessResponse, _require_admin, liveness, readiness, router

# Stays standalone-runnable: `uvicorn modules.auth.main:app` from the repo
# root, OR `python main.py` from inside modules/auth/. Either works.

_dir = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="INSIGHT Authentication", docs_url="/api/auth/docs")
app.include_router(router)
app.mount("/static", StaticFiles(directory=os.path.join(_dir, "static")), name="static")


@app.get("/contract")
def contract():
    return JSONResponse(contract_payload())


@app.get("/schemas/{version}/{name}")
def published_schema(version: str, name: str):
    try:
        payload = schema(version, name)
    except (KeyError, ValueError):
        return JSONResponse(
            {"code": "SCHEMA_NOT_FOUND", "message": "Requested schema is not published."},
            status_code=404,
            media_type="application/problem+json",
        )
    return JSONResponse(payload, media_type="application/schema+json")


# FastAPI built-in openapi route delegates to this callable.
app.openapi = openapi_document


@app.get("/")
def index():
    return FileResponse(os.path.join(_dir, "static", "index.html"))


@app.get("/healthz", response_model=HealthResponse, tags=["ops"])
def healthz():
    return liveness()


@app.get("/readyz", response_model=ReadinessResponse, tags=["ops"])
def readyz(response: Response):
    return readiness(response)


@app.get("/modules/user-management/contract")
def user_management_contract():
    return {
        "moduleId": "user-management",
        "interfaceVersion": "1.0.0",
        "basePath": "/modules/user-management",
    }


@app.get("/modules/user-management/ready")
def user_management_ready():
    report = security.readiness_report()
    if report["ok"]:
        return {"status": "ready"}
    return JSONResponse(status_code=503, content={"status": "not-ready"})


@app.get("/modules/user-management")
def user_management(request: Request):
    _require_admin(request)
    return FileResponse(os.path.join(_dir, "static", "user-management.html"))


@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    """
    SPA-like fallback so deep links on the login surface resolve to the same
    page. Login/disclaimer screens are single-file; deeper dashboard routes
    belong to other modules hosted at /dashboard/*.

    ponytail: no actual SPA routing — justFiles the HTML; relevant only for
    human navigators. Real API routes are mount-prefixed (/api/auth/*).
    """
    if full_path.startswith("api/"):
        # Let FastAPI's 404 handler take over for unknown API routes.
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not Found")
    return index()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("AUTH_PORT", "8000")))
