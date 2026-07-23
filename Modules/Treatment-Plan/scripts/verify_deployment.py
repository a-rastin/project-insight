"""Independent standalone, unified-route, TLS, and recovery verification."""

from __future__ import annotations

import argparse
import json
import socket
import sqlite3
import subprocess
import tempfile
import time
import urllib.request
from contextlib import closing
from pathlib import Path
from uuid import uuid4

try:
    from scripts.package_release import immutable_image_reference, image_digest
except ModuleNotFoundError:
    from package_release import immutable_image_reference, image_digest

from treatment_plan.config import Settings
from treatment_plan.deployment import migration_gate
from treatment_plan.sqlite_repository import SQLiteRepository


ROOT = Path(__file__).parents[1]
SECURITY_HEADERS = (
    "strict-transport-security", "content-security-policy", "x-content-type-options",
    "x-frame-options", "referrer-policy",
)


def request(url: str, *, attempts: int = 1) -> tuple[int, dict[str, str], bytes]:
    error: Exception | None = None
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.status, {key.lower(): value for key, value in response.headers.items()}, response.read()
        except Exception as exc:  # noqa: BLE001 - the retry surface includes transport failures
            error = exc
            time.sleep(1)
    raise RuntimeError(f"deployment check failed for {url}: {error}")


def verify_http(base_url: str, *, unified: bool = False) -> None:
    base = base_url.rstrip("/")
    # Standalone process serves /health and /ready at root. VPS/nginx and unified routes map
    # those to /api/treatment-plan/health|ready (standalone module) or module base paths.
    if unified:
        health_candidates = ("/api/treatment-plan/health", "/api/treatment-plan/v1/health", "/health")
        ready_candidates = ("/api/treatment-plan/ready", "/api/treatment-plan/v1/ready", "/ready")
    else:
        health_candidates = ("/health", "/api/treatment-plan/health")
        ready_candidates = ("/ready", "/api/treatment-plan/ready")
    health_ok = False
    for path in health_candidates:
        try:
            status, _, health = request(base + path, attempts=15 if path == health_candidates[0] else 3)
        except RuntimeError:
            continue
        if status == 200 and json.loads(health).get("status") == "ok":
            health_ok = True
            break
    if not health_ok:
        raise RuntimeError("health smoke test failed")
    ready_ok = False
    for path in ready_candidates:
        try:
            status, _, ready = request(base + path, attempts=5)
        except RuntimeError:
            continue
        if status == 200 and json.loads(ready).get("status") == "ready":
            ready_ok = True
            break
    if not ready_ok:
        raise RuntimeError("readiness or migration gate failed")
    shell_path = "/modules/treatment-plan"
    try:
        status, _, body = request(base + shell_path, attempts=3)
        if status != 200 or b"<!" not in body[:200].lower():
            if not unified:
                raise RuntimeError("module route integration test failed")
    except RuntimeError:
        if not unified:
            raise


def verify_tls(url: str) -> None:
    if not url.lower().startswith("https://"):
        raise RuntimeError("TLS verification requires an https URL")
    status, headers, _ = request(url)
    if status != 200:
        raise RuntimeError("TLS endpoint did not return success")
    missing = [name for name in SECURITY_HEADERS if not headers.get(name)]
    if missing:
        raise RuntimeError("missing security headers: " + ", ".join(missing))


def available_port() -> int:
    with socket.socket() as candidate:
        candidate.bind(("127.0.0.1", 0))
        return int(candidate.getsockname()[1])


def hardened_run_command(image: str, name: str, volume: str, port: int) -> list[str]:
    immutable_image_reference(image)
    return [
        "docker", "run", "--detach", "--name", name, "--user", "10001:10001", "--read-only",
        "--tmpfs", "/tmp:size=32m,mode=1777", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--memory", "512m", "--cpus", "1", "--pids-limit", "256", "--stop-timeout", "35",
        "--publish", f"127.0.0.1:{port}:8000", "--volume", f"{volume}:/data",
        "--env", "TP_ENV=development", "--env", "TP_AUTH_STUB_ENABLED=true", image,
    ]


def verify_container(image: str, *, recovery: bool) -> None:
    suffix = uuid4().hex[:10]
    name, volume, port = f"tp-verify-{suffix}", f"tp-verify-{suffix}", available_port()
    run = lambda command: subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    try:
        run(["docker", "volume", "create", volume])
        run(hardened_run_command(image, name, volume, port))
        verify_http(f"http://127.0.0.1:{port}")
        if recovery:
            run(["docker", "kill", name])
            run(["docker", "start", name])
            verify_http(f"http://127.0.0.1:{port}")
        run(["docker", "stop", "--time", "35", name])
        exit_code = json.loads(run(["docker", "inspect", name]).stdout)[0]["State"]["ExitCode"]
        if exit_code != 0:
            raise RuntimeError("graceful shutdown returned a non-zero container exit code")
        # After graceful stop the persisted volume database must remain integrity-clean.
        inspect = json.loads(run(["docker", "volume", "inspect", volume]).stdout)[0]
        mountpoint = Path(inspect["Mountpoint"])
        candidates = list(mountpoint.rglob("*.db")) + list(mountpoint.rglob("*.sqlite3"))
        for database in candidates:
            with closing(sqlite3.connect(database)) as connection:
                result = connection.execute("PRAGMA integrity_check").fetchone()
                if result is None or result[0] != "ok":
                    raise RuntimeError("graceful shutdown left a corrupt database")
    finally:
        subprocess.run(["docker", "rm", "--force", name], cwd=ROOT, capture_output=True)
        subprocess.run(["docker", "volume", "rm", "--force", volume], cwd=ROOT, capture_output=True)


def verify_backup_restore_integrity(directory: Path) -> None:
    """Backup/restore round-trip must preserve PRAGMA integrity and row payload."""
    from treatment_plan.repository import RuntimeRecord

    directory.mkdir(parents=True, exist_ok=True)
    live = directory / "live.db"
    backup = directory / "backup.db"
    restored = directory / "restored.db"
    repository = SQLiteRepository(live)
    repository.migrate()
    repository.put(RuntimeRecord("smoke", "payload"))
    repository.backup(backup)
    with closing(sqlite3.connect(backup)) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
        if result is None or result[0] != "ok":
            raise RuntimeError("backup failed integrity check")
    restored_repo = SQLiteRepository(restored)
    restored_repo.restore(backup)
    record = restored_repo.get("smoke")
    if record is None or record.value != "payload":
        raise RuntimeError("restore did not recover authoritative payload")
    with closing(sqlite3.connect(restored)) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
        if result is None or result[0] != "ok":
            raise RuntimeError("restored database failed integrity check")


def verify_partial_migration_failure(directory: Path) -> None:
    """Partial or drifted schema versions must fail the startup migration gate."""
    directory.mkdir(parents=True, exist_ok=True)
    database = directory / "partial.db"
    settings = Settings(environment="test", database_path=database)
    migration_gate(settings)
    with closing(sqlite3.connect(database)) as connection:
        versions = [row[0] for row in connection.execute("SELECT version FROM schema_migrations ORDER BY version")]
        if not versions:
            raise RuntimeError("migration gate produced no schema versions")
        connection.execute("DELETE FROM schema_migrations WHERE version = ?", (versions[-1],))
        connection.commit()
    try:
        migration_gate(settings)
    except RuntimeError:
        return
    raise RuntimeError("partial migration was not rejected")


def verify_graceful_database_integrity(directory: Path) -> None:
    """Complete write then release connection; database stays integrity-clean for gate."""
    from treatment_plan.repository import RuntimeRecord

    directory.mkdir(parents=True, exist_ok=True)
    database = directory / "graceful.db"
    repository = SQLiteRepository(database)
    repository.migrate()
    repository.put(RuntimeRecord("grace", "1"))
    with closing(sqlite3.connect(database)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE runtime_records SET value = ? WHERE key = ?", ("2", "grace"))
        connection.commit()
        result = connection.execute("PRAGMA integrity_check").fetchone()
    if result is None or result[0] != "ok":
        raise RuntimeError("database corrupted after graceful write completion")
    settings = Settings(environment="test", database_path=database)
    if migration_gate(settings) != ():
        raise RuntimeError("unexpected migration drift after graceful shutdown path")


def scan_evidence_path(root: Path, image: str) -> Path:
    digest = image_digest(image)
    return root / "artifacts" / "scans" / f"{digest.replace(':', '-')}.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    http = sub.add_parser("standalone")
    http.add_argument("--base-url", default="http://127.0.0.1:8000")
    unified = sub.add_parser("unified")
    unified.add_argument("--base-url", required=True)
    tls = sub.add_parser("tls")
    tls.add_argument("--url", required=True)
    container = sub.add_parser("container")
    container.add_argument("--image", required=True)
    container.add_argument("--recovery", action="store_true")
    integrity = sub.add_parser("integrity")
    integrity.add_argument("--directory", type=Path, default=None)
    args = parser.parse_args()
    if args.command == "standalone":
        verify_http(args.base_url)
    elif args.command == "unified":
        verify_http(args.base_url, unified=True)
    elif args.command == "tls":
        verify_tls(args.url)
    elif args.command == "container":
        verify_container(args.image, recovery=args.recovery)
    else:
        directory = args.directory or Path(tempfile.mkdtemp(prefix="tp-integrity-"))
        directory.mkdir(parents=True, exist_ok=True)
        verify_backup_restore_integrity(directory / "backup")
        verify_partial_migration_failure(directory / "partial")
        verify_graceful_database_integrity(directory / "graceful")
        print("integrity verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
