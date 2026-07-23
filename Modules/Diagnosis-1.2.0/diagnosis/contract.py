"""Common Insight contract and readiness adapter for the diagnosis module."""
from __future__ import annotations

from pathlib import Path
import sys

from .config import settings
from .criteria import supported_clinical_scope
from .readiness import check_readiness


def contract_payload() -> dict:
    return {
        "moduleId": settings.module_id,
        "moduleVersion": "1.2.0",
        "interfaceVersion": "1.0.0",
        "schemaVersion": "1.0.0",
        "basePath": settings.module_base_path,
        "capabilities": ["diagnosis.criteria", "diagnosis.session"],
        "dependencies": [
            {
                "moduleId": "authentication",
                "interfaceVersion": "1.0.0",
                "required": True,
                "capabilities": ["auth.session"],
            },
            {
                "moduleId": "add-new-patient",
                "interfaceVersion": "1.1.0",
                "required": False,
                "capabilities": ["patient.identity"],
            },
        ],
        "auth": {"required": True, "schemes": ["session", "csrf"]},
        "compatibilityRoutes": [],
        "supportedClinicalScope": supported_clinical_scope(),
    }


def common_readiness() -> dict[str, str]:
    """Map module-local checks onto the common readiness vocabulary."""
    state = check_readiness()
    checks = state["checks"]
    dependencies_ok = all(
        checks[name]["ok"] for name in ("db", "auth", "patient")
    )
    configuration_ok = checks["auth"]["configured"] and checks["patient"]["configured"]
    return {
        "migrations": "ok" if checks["db"]["ok"] else "blocked",
        "configuration": "ok" if configuration_ok else "blocked",
        "contractCompatibility": "ok" if checks["clinicalScope"]["ok"] else "blocked",
        "dependencies": "ok" if dependencies_ok else "blocked",
    }


def contract_registry():
    """Load the immutable common artifacts without importing domain code."""
    root = Path(__file__).resolve().parents[3] / "contracts"
    project_root = str(root.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from contracts.adapters.python.filesystem import FilesystemContractAdapter

    return FilesystemContractAdapter(root)


def install_common_routes(app) -> None:
    """Install the shared transport routes after the registry is resolvable."""
    registry = contract_registry()
    from contracts.adapters.python.fastapi import install_common_routes as install

    install(
        app,
        registry,
        contract=contract_payload(),
        readiness=common_readiness,
    )


__all__ = [
    "contract_payload",
    "common_readiness",
    "contract_registry",
    "install_common_routes",
]
