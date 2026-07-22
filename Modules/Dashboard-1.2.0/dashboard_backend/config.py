from __future__ import annotations

import json
import os
from pathlib import Path

from .discovery import ModuleRegistration, ready_url_for

ROOT = Path(__file__).resolve().parent.parent


class Settings:
    def __init__(self) -> None:
        self.port = int(os.environ.get("PORT", "4173"))
        self.db_path = os.environ.get("DASHBOARD_DB_PATH", str(ROOT / "dashboard.sqlite3"))
        self.auth_session_url = os.environ.get("AUTH_SESSION_URL", "")
        self.auth_base_url = os.environ.get("AUTH_BASE_URL", "")
        self.auth_session_timeout_seconds = float(os.environ.get("AUTH_SESSION_TIMEOUT_MS", "2000")) / 1000
        self.module_discovery_timeout_seconds = float(os.environ.get("DASHBOARD_MODULE_TIMEOUT_MS", "2000")) / 1000
        config = json.loads((ROOT / "module-config.json").read_text(encoding="utf-8"))
        configured_registry = os.environ.get("DASHBOARD_MODULE_REGISTRY")
        raw_registry = json.loads(configured_registry) if configured_registry is not None else config.get("moduleRegistry", [])
        if not isinstance(raw_registry, list):
            raise ValueError("moduleRegistry must be a list")
        self.module_registry = tuple(self._module_registration(item) for item in raw_registry)
        self.use_mock_auth = os.environ.get("DASHBOARD_MOCK_AUTH") == "1" or (
            not self.auth_session_url
            and not self.auth_base_url
            and os.environ.get("DASHBOARD_MOCK_AUTH") != "0"
        )

    @staticmethod
    def _module_registration(item: object) -> ModuleRegistration:
        if not isinstance(item, dict):
            raise ValueError("each moduleRegistry entry must be an object")
        module_id = item.get("moduleId")
        title = item.get("title")
        roles = item.get("roles")
        contract_url = item.get("contractUrl")
        if not isinstance(module_id, str) or not module_id:
            raise ValueError("moduleRegistry moduleId must be a non-empty string")
        if not isinstance(title, str) or not title:
            raise ValueError(f"moduleRegistry title for {module_id} must be a non-empty string")
        if not isinstance(roles, list) or not roles or any(role not in ("PSYCHIATRIST", "ADMIN") for role in roles):
            raise ValueError(f"moduleRegistry roles for {module_id} must contain PSYCHIATRIST or ADMIN")
        if not isinstance(contract_url, str):
            raise ValueError(f"moduleRegistry contractUrl for {module_id} must be a string")
        ready_url_for(contract_url)
        return ModuleRegistration(module_id, title, tuple(roles), contract_url)


settings = Settings()
