"""Machine-checkable deployment and browser URL contract."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class DeploymentContractError(ValueError):
    pass


_LOCALHOST_URL = re.compile(r"https?://(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?(?:[/?#]|$)", re.IGNORECASE)
_SKIP_PARTS = {".git", "__pycache__", "node_modules", "graphify-out", ".understand-anything", "dist"}
_BROWSER_PARTS = {"frontend", "public", "src"}


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DeploymentContractError(f"cannot load deployment manifest: {error}") from error
    if not isinstance(manifest, dict):
        raise DeploymentContractError("deployment manifest must be an object")
    return manifest


def _required(mapping: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if field not in mapping]
    if missing:
        raise DeploymentContractError(f"{label} missing fields: {', '.join(missing)}")


def _unique(modules: list[dict[str, Any]], field: str) -> None:
    values = [module.get(field) for module in modules]
    if len(values) != len(set(values)):
        raise DeploymentContractError(f"module {field} values must be unique")


def _check_component(module: dict[str, Any], name: str, fields: tuple[str, ...]) -> None:
    component = module.get(name)
    if not isinstance(component, dict):
        raise DeploymentContractError(f"{module.get('moduleId')}.{name} must be an object")
    _required(component, fields, f"{module.get('moduleId')}.{name}")
    if component.get("configured") is False:
        raise DeploymentContractError(f"{module.get('moduleId')}.{name} must be configured")
    if component.get("owner") != module.get("moduleId"):
        raise DeploymentContractError(f"{module.get('moduleId')}.{name} owner mismatch")


def _browser_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".mjs", ".ts", ".tsx"}:
            continue
        relative = path.relative_to(root)
        if any(part in _SKIP_PARTS for part in relative.parts):
            continue
        if not _BROWSER_PARTS.intersection(relative.parts):
            continue
        if any("test" in part.casefold() for part in relative.parts):
            continue
        yield path


def _check_browser_urls(root: Path, manifest: dict[str, Any]) -> None:
    for path in _browser_files(root):
        text = path.read_text(encoding="utf-8")
        if _LOCALHOST_URL.search(text):
            raise DeploymentContractError(f"browser source contains hard-coded localhost URL: {path}")
    overrides = manifest.get("browserSourceOverrides", {})
    if not isinstance(overrides, dict):
        raise DeploymentContractError("browserSourceOverrides must be an object")
    for path, text in overrides.items():
        if isinstance(text, str) and _LOCALHOST_URL.search(text):
            raise DeploymentContractError(f"browser source contains hard-coded localhost URL: {path}")


def _check_module_configs(root: Path, module_ids: set[str]) -> None:
    configs = sorted(root.glob("Modules/*/module-config.json"))
    configured_ids = set()
    for path in configs:
        config = load_manifest(path)
        _required(config, ("moduleId", "dataDirectory", "databasePath"), str(path))
        if config["moduleId"] in configured_ids:
            raise DeploymentContractError(f"duplicate module config: {config['moduleId']}")
        configured_ids.add(config["moduleId"])
        for field in ("dataDirectory", "databasePath"):
            value = config[field]
            if not isinstance(value, str) or not value or value.startswith("/") or ".." in Path(value).parts:
                raise DeploymentContractError(f"{path}: {field} must be module-local relative path")
    if configured_ids != module_ids:
        raise DeploymentContractError("module-config.json IDs must match deployment manifest IDs")


def check_deployment(root: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("manifestId") != "deployment-manifest-1.0.0":
        raise DeploymentContractError("unsupported deployment manifest")
    if manifest.get("schema") != "deployment/manifest.schema.json":
        raise DeploymentContractError("deployment manifest must reference deployment schema")
    image = manifest.get("image")
    if not isinstance(image, dict) or image.get("dockerfile") != "deployment/Dockerfile" or image.get("context") != ".":
        raise DeploymentContractError("unified image must be rooted at deployment/Dockerfile")
    gateway = manifest.get("gateway")
    if gateway != {"port": 8080, "exposed": True}:
        raise DeploymentContractError("unified gateway must expose port 8080")
    supervisor = manifest.get("supervisor")
    if not isinstance(supervisor, dict) or supervisor.get("pid1") != "tini":
        raise DeploymentContractError("unified image must use tini as PID 1")
    modules = manifest.get("modules")
    if not isinstance(modules, list) or not modules:
        raise DeploymentContractError("deployment manifest modules must be a non-empty list")
    for module in modules:
        if not isinstance(module, dict):
            raise DeploymentContractError("each deployment module must be an object")
        _required(module, ("moduleId", "internalPort", "basePath", "proxyPrefix", "volume", "migration", "backup", "restore", "retention", "shutdown", "workingDirectory", "command", "environment", "databasePath"), "module")
        if not isinstance(module["moduleId"], str) or not re.fullmatch(r"[a-z][a-z0-9-]*", module["moduleId"]):
            raise DeploymentContractError("module IDs must be stable kebab-case identifiers")
        if not isinstance(module["internalPort"], int) or not 1024 <= module["internalPort"] <= 65535:
            raise DeploymentContractError(f"invalid internal port for {module['moduleId']}")
        for field in ("basePath", "proxyPrefix"):
            if not isinstance(module[field], str) or not module[field].startswith("/") or "localhost" in module[field].casefold():
                raise DeploymentContractError(f"invalid {field} for {module['moduleId']}")
        volume = module["volume"]
        if not isinstance(volume, dict) or volume.get("writable") is not True or not str(volume.get("mountPath", "")).startswith("/"):
            raise DeploymentContractError(f"invalid writable volume for {module['moduleId']}")
        mount_path = volume["mountPath"]
        database_path = module["databasePath"]
        if not database_path.startswith(mount_path + "/"):
            raise DeploymentContractError(f"database must stay inside module volume for {module['moduleId']}")
        if not isinstance(module["command"], list) or not module["command"]:
            raise DeploymentContractError(f"module command missing for {module['moduleId']}")
        if not isinstance(module["environment"], dict):
            raise DeploymentContractError(f"module environment missing for {module['moduleId']}")
        migration = module["migration"]
        if not isinstance(migration, dict) or migration.get("mode") != "startup" or migration.get("readinessGate") is not True or migration.get("owner") != module["moduleId"]:
            raise DeploymentContractError(f"startup migration gate missing for {module['moduleId']}")
        _check_component(module, "backup", ("configured", "owner"))
        _check_component(module, "restore", ("configured", "owner"))
        _check_component(module, "retention", ("configured", "policyReference", "owner"))
        shutdown = module["shutdown"]
        if not isinstance(shutdown, dict) or shutdown.get("signal") != "SIGTERM" or not isinstance(shutdown.get("timeoutSeconds"), int) or not 1 <= shutdown["timeoutSeconds"] <= 300:
            raise DeploymentContractError(f"invalid graceful shutdown contract for {module['moduleId']}")
    _unique(modules, "moduleId")
    _unique(modules, "internalPort")
    _unique(modules, "basePath")
    _unique(modules, "proxyPrefix")
    _unique([{"volume": module["volume"]["name"]} for module in modules], "volume")
    _check_module_configs(root, {module["moduleId"] for module in modules})
    _check_browser_urls(root, manifest)


def main() -> int:
    root = Path(__file__).parents[1]
    check_deployment(root, load_manifest(root / "deployment" / "manifest.json"))
    print("deployment contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
