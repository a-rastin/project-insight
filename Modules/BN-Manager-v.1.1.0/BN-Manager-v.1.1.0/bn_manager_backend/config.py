from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_AUTH_SESSION_URL = "http://127.0.0.1:8000/api/auth/session"
DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "bn-manager.sqlite3"


@dataclass(frozen=True, slots=True)
class BnManagerSettings:
    module_id: str = "bn-manager"
    app_name: str = "BN Manager"
    api_prefix: str = "/api"
    ui_mount_path: str = "/modules/bn-manager"
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    static_dir: Path = Path(__file__).resolve().parent / "static"
    auth_session_url: str = DEFAULT_AUTH_SESSION_URL
    auth_timeout_seconds: float = 2.0
    csrf_header_name: str = "x-csrf-token"
    database_path: Path = DEFAULT_DATABASE_PATH

    @classmethod
    def from_env(cls) -> "BnManagerSettings":
        database_raw = os.getenv("BN_MANAGER_DATABASE_PATH")
        return cls(
            host=os.getenv("BN_MANAGER_HOST", DEFAULT_HOST),
            port=int(os.getenv("BN_MANAGER_PORT", str(DEFAULT_PORT))),
            auth_session_url=os.getenv("BN_MANAGER_AUTH_SESSION_URL", DEFAULT_AUTH_SESSION_URL),
            auth_timeout_seconds=float(os.getenv("BN_MANAGER_AUTH_TIMEOUT_SECONDS", "2.0")),
            csrf_header_name=os.getenv("BN_MANAGER_CSRF_HEADER_NAME", "x-csrf-token"),
            database_path=Path(database_raw) if database_raw else DEFAULT_DATABASE_PATH,
        )


@lru_cache(maxsize=1)
def get_settings() -> BnManagerSettings:
    return BnManagerSettings.from_env()
