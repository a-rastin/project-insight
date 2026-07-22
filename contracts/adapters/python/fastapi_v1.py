"""FastAPI common route installer with built-in OpenAPI route disabled."""
from .fastapi import install_common_routes as _install_common_routes


def install_common_routes(app, registry, *, contract: dict, readiness=None):
    app.router.routes[:] = [route for route in app.router.routes if getattr(route, "path", None) != "/openapi.json"]
    return _install_common_routes(app, registry, contract=contract, readiness=readiness)
