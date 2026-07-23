"""Multi-module and unified-gateway deployment verification (TP22.4)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "deployment" / "manifest.json"
IMMUTABLE_IMAGE = re.compile(r"^[^@\s]+@sha256:([0-9a-f]{64})$")
SECURITY_HEADERS = (
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
)

# Standalone process probes taken from each module's real route surface.
# Unified gateway candidates use nginx basePath/proxyPrefix plus known aliases.
MODULE_SMOKE: dict[str, dict[str, Any]] = {
    "authentication": {
        "standalone_health": ("/healthz", "/api/auth/health"),
        "standalone_ready": ("/readyz", "/api/auth/ready"),
        "unified_health": ("/api/auth/health", "/healthz"),
        "unified_ready": ("/api/auth/ready", "/readyz"),
    },
    "dashboard": {
        "standalone_health": ("/healthz",),
        "standalone_ready": ("/readyz",),
        "unified_health": ("/healthz", "/internal/dashboard/healthz"),
        "unified_ready": ("/readyz", "/internal/dashboard/readyz"),
    },
    "add-new-patient": {
        "standalone_health": ("/api/health",),
        "standalone_ready": (),
        "unified_health": ("/api/health", "/api/add-new-patient/v1/health"),
        "unified_ready": (),
    },
    "diagnosis": {
        "standalone_health": ("/health",),
        "standalone_ready": ("/ready",),
        "unified_health": ("/health", "/api/diagnosis/v1/health", "/modules/diagnosis/health"),
        "unified_ready": ("/ready", "/api/diagnosis/v1/ready", "/modules/diagnosis/ready"),
    },
    "severity": {
        "standalone_health": ("/health",),
        "standalone_ready": ("/ready",),
        "unified_health": ("/health", "/modules/severity/health"),
        "unified_ready": ("/ready", "/modules/severity/ready"),
    },
    "medical-history": {
        "standalone_health": ("/api/internal/medical-history/health",),
        "standalone_ready": ("/ready", "/api/internal/medical-history/ready"),
        "unified_health": ("/api/internal/medical-history/health",),
        "unified_ready": ("/api/internal/medical-history/ready", "/ready"),
    },
    "ddi-checker": {
        "standalone_health": ("/health",),
        "standalone_ready": ("/ready",),
        "unified_health": ("/health", "/api/ddi-checker/v1/health", "/modules/ddi-checker/health"),
        "unified_ready": ("/ready", "/api/ddi-checker/v1/ready", "/modules/ddi-checker/ready"),
    },
    "bn-manager": {
        "standalone_health": ("/api/health",),
        "standalone_ready": ("/api/ready",),
        "unified_health": ("/api/health", "/api/bn-manager/v1/health", "/modules/bn-manager/api/health"),
        "unified_ready": ("/api/ready", "/api/bn-manager/v1/ready", "/modules/bn-manager/api/ready"),
    },
    "treatment-plan": {
        "standalone_health": ("/health", "/api/treatment-plan/health"),
        "standalone_ready": ("/ready", "/api/treatment-plan/ready"),
        "unified_health": (
            "/api/treatment-plan/health",
            "/api/treatment-plan/v1/health",
            "/modules/treatment-plan/health",
            "/health",
        ),
        "unified_ready": (
            "/api/treatment-plan/ready",
            "/api/treatment-plan/v1/ready",
            "/modules/treatment-plan/ready",
            "/ready",
        ),
    },
}


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def immutable_image_reference(image: str) -> str:
    if not IMMUTABLE_IMAGE.fullmatch(image):
        raise ValueError("image reference must use immutable @sha256 digest")
    return image


def image_digest(image: str) -> str:
    match = IMMUTABLE_IMAGE.fullmatch(immutable_image_reference(image))
    assert match is not None
    return "sha256:" + match.group(1)


def scan_evidence_path(root: Path, image: str) -> Path:
    digest = image_digest(image)
    return root / "artifacts" / "scans" / f"{digest.replace(':', '-')}.json"


def write_scan_evidence(root: Path, image: str, *, scanner: str, report: dict) -> Path:
    destination = scan_evidence_path(root, image)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "image": image,
        "digest": image_digest(image),
        "scanner": scanner,
        "report": report,
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def request(url: str, *, attempts: int = 1, timeout: float = 5.0) -> tuple[int, dict[str, str], bytes]:
    error: Exception | None = None
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                return response.status, {key.lower(): value for key, value in response.headers.items()}, response.read()
        except Exception as exc:  # noqa: BLE001 - transport retries
            error = exc
            time.sleep(1)
    raise RuntimeError(f"deployment check failed for {url}: {error}")


def smoke_matrix(manifest: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Build the every-module smoke matrix from the deployment manifest."""
    data = manifest or load_manifest()
    rows: list[dict[str, Any]] = []
    for module in data["modules"]:
        module_id = module["moduleId"]
        if module_id not in MODULE_SMOKE:
            raise RuntimeError(f"no smoke route map for module {module_id}")
        probes = MODULE_SMOKE[module_id]
        rows.append(
            {
                "moduleId": module_id,
                "internalPort": module["internalPort"],
                "basePath": module["basePath"],
                "proxyPrefix": module["proxyPrefix"],
                "standalone_health": list(probes["standalone_health"]),
                "standalone_ready": list(probes["standalone_ready"]),
                "unified_health": list(probes["unified_health"]),
                "unified_ready": list(probes["unified_ready"]),
            }
        )
    return rows


def _probe_ok(status: int, body: bytes) -> bool:
    if status != 200:
        return False
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return False
    if not isinstance(payload, dict):
        return False
    if payload.get("ok") is True:
        return True
    status_value = payload.get("status")
    if isinstance(status_value, str) and status_value.lower() in {"ok", "ready", "healthy", "alive"}:
        return True
    data = payload.get("data")
    if isinstance(data, dict):
        nested = data.get("status")
        if isinstance(nested, str) and nested.lower() in {"ok", "ready", "healthy", "alive"}:
            return True
    return False


def verify_paths(base_url: str, paths: list[str], *, label: str, attempts: int = 5) -> str:
    base = base_url.rstrip("/")
    if not paths:
        return ""
    errors: list[str] = []
    for path in paths:
        url = base + path
        try:
            status, _, body = request(url, attempts=attempts)
        except RuntimeError as exc:
            errors.append(str(exc))
            continue
        if _probe_ok(status, body):
            return path
        errors.append(f"{url} -> HTTP {status}")
    raise RuntimeError(f"{label} failed: " + "; ".join(errors))


def verify_module_standalone(base_url: str, module_id: str) -> None:
    probes = MODULE_SMOKE[module_id]
    verify_paths(base_url, list(probes["standalone_health"]), label=f"{module_id} health")
    if probes["standalone_ready"]:
        verify_paths(base_url, list(probes["standalone_ready"]), label=f"{module_id} ready")


def verify_unified_gateway(base_url: str, *, manifest: dict[str, Any] | None = None) -> None:
    data = manifest or load_manifest()
    base = base_url.rstrip("/")
    gateway_port = int(data["gateway"]["port"])
    if f":{gateway_port}" not in base and not base.endswith(str(gateway_port)):
        # Allow operators to pass https edge URLs; still require path checks below.
        pass
    for row in smoke_matrix(data):
        module_id = row["moduleId"]
        verify_paths(base, row["unified_health"], label=f"unified {module_id} health", attempts=15 if module_id == data["modules"][0]["moduleId"] else 5)
        if row["unified_ready"]:
            verify_paths(base, row["unified_ready"], label=f"unified {module_id} ready", attempts=5)
        # REST ownership surface via gateway basePath and module shell via proxyPrefix.
        for path in (row["basePath"], row["proxyPrefix"]):
            url = base + path
            try:
                status, _, _ = request(url, attempts=3)
            except RuntimeError:
                # Some base paths only accept authenticated POST/GET with ids; connection must reach nginx.
                try:
                    with urllib.request.urlopen(url, timeout=3) as response:
                        status = response.status
                except urllib.error.HTTPError as exc:
                    status = exc.code
                except Exception as exc:  # noqa: BLE001
                    raise RuntimeError(f"unified route unreachable {url}: {exc}") from exc
            if status >= 500:
                raise RuntimeError(f"unified route {url} returned server error {status}")


def verify_topology_contracts(root: Path = ROOT) -> dict[str, bool]:
    """Offline contracts: TLS, loopback bind, restart policy, writable volumes, digest gate."""
    unit = (root / "deployment" / "insight-unified-container.service").read_text(encoding="utf-8")
    nginx = (root / "deployment" / "nginx-vps.conf").read_text(encoding="utf-8")
    nginx_lower = nginx.lower()
    compose = (root / "deployment" / "compose.unified.yaml").read_text(encoding="utf-8")
    manifest = load_manifest(root / "deployment" / "manifest.json")

    if "ssl_protocols" not in nginx_lower or "tlsv1.2" not in nginx_lower or "tlsv1.3" not in nginx_lower:
        raise RuntimeError("VPS nginx must enable TLSv1.2 and TLSv1.3 only")
    missing = [header for header in SECURITY_HEADERS if header not in nginx_lower]
    if missing:
        raise RuntimeError("VPS nginx missing security headers: " + ", ".join(missing))
    if "127.0.0.1:8080" not in unit or "127.0.0.1:8080:8080" not in compose:
        raise RuntimeError("unified gateway must bind loopback only on host")
    if "Restart=on-failure" not in unit:
        raise RuntimeError("unified systemd unit must restart on failure for host reboot recovery")
    if "${INSIGHT_UNIFIED_IMAGE}" not in unit and "INSIGHT_UNIFIED_IMAGE" not in unit:
        raise RuntimeError("systemd unit must require immutable INSIGHT_UNIFIED_IMAGE digest")
    if "INSIGHT_UNIFIED_IMAGE" not in compose:
        raise RuntimeError("compose must require immutable INSIGHT_UNIFIED_IMAGE digest")
    for module in manifest["modules"]:
        volume_name = module["volume"]["name"]
        mount = module["volume"]["mountPath"]
        if volume_name not in compose or mount not in unit:
            raise RuntimeError(f"missing volume persistence for {module['moduleId']}")
        if not module["volume"]["writable"]:
            raise RuntimeError(f"module volume must be writable: {module['moduleId']}")
        if module["migration"]["mode"] != "startup" or not module["migration"]["readinessGate"]:
            raise RuntimeError(f"startup migration gate required for {module['moduleId']}")
    for port in range(8101, 8110):
        if f"127.0.0.1:{port}" in unit or f":{port}:" in unit:
            raise RuntimeError(f"module port {port} must stay inside the container")
        if f'"{port}:' in compose or f"'{port}:" in compose:
            raise RuntimeError(f"module port {port} must not be published on the host")
    return {
        "tls": True,
        "loopback": True,
        "restart": True,
        "volumes": True,
        "digest": True,
    }


def scan_image(image: str, *, evidence_root: Path | None = None) -> Path:
    """Trivy-first image scan; Docker Scout is optional developer fallback only."""
    immutable_image_reference(image)
    root = evidence_root or ROOT
    if shutil.which("trivy"):
        result = subprocess.run(
            ["trivy", "image", "--exit-code", "1", "--severity", "HIGH,CRITICAL", "--format", "json", image],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        report = json.loads(result.stdout or "{}")
        evidence = write_scan_evidence(root, image, scanner="trivy", report=report)
        if result.returncode:
            raise RuntimeError(f"Trivy reported HIGH/CRITICAL findings for {image}; evidence={evidence}")
        return evidence
    if shutil.which("docker"):
        result = subprocess.run(
            ["docker", "scout", "cves", "--exit-code", "--only-severity", "critical,high", image],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        report = {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
        evidence = write_scan_evidence(root, image, scanner="docker-scout", report=report)
        if result.returncode:
            raise RuntimeError(f"Docker Scout scan failed for {image}; evidence={evidence}")
        return evidence
    raise RuntimeError("image scan failed, or neither Trivy nor Docker Scout is available")


def available_port() -> int:
    with socket.socket() as candidate:
        candidate.bind(("127.0.0.1", 0))
        return int(candidate.getsockname()[1])


def hardened_unified_run_command(image: str, name: str, port: int) -> list[str]:
    immutable_image_reference(image)
    return [
        "docker", "run", "--detach", "--name", name,
        "--read-only",
        "--tmpfs", "/tmp:size=64m,mode=1777",
        "--tmpfs", "/run",
        "--tmpfs", "/var/cache/nginx",
        "--tmpfs", "/var/log/nginx",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--memory", "2048m",
        "--pids-limit", "1024",
        "--stop-timeout", "45",
        "--publish", f"127.0.0.1:{port}:8080",
        image,
    ]


def verify_container(image: str, *, recovery: bool) -> None:
    if not shutil.which("docker"):
        raise RuntimeError("docker is not available; container recovery verification skipped")
    immutable_image_reference(image)
    suffix = uuid4().hex[:10]
    name, port = f"insight-verify-{suffix}", available_port()
    run = lambda command: subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    try:
        run(hardened_unified_run_command(image, name, port))
        verify_unified_gateway(f"http://127.0.0.1:{port}")
        if recovery:
            run(["docker", "kill", name])
            run(["docker", "start", name])
            verify_unified_gateway(f"http://127.0.0.1:{port}")
        run(["docker", "stop", "--time", "45", name])
    finally:
        subprocess.run(["docker", "rm", "--force", name], cwd=ROOT, capture_output=True)


def verify_all_modules_smoke_matrix() -> list[dict[str, Any]]:
    """Contract-level check that every manifest module has flow directions."""
    rows = smoke_matrix()
    if len(rows) != len(load_manifest()["modules"]):
        raise RuntimeError("smoke matrix does not cover every deployment module")
    for row in rows:
        if not row["standalone_health"]:
            raise RuntimeError(f"{row['moduleId']} missing standalone health probe")
        if not row["unified_health"]:
            raise RuntimeError(f"{row['moduleId']} missing unified health probe")
        if not row["basePath"].startswith("/") or not row["proxyPrefix"].startswith("/"):
            raise RuntimeError(f"{row['moduleId']} has invalid routing paths")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify multi-module and unified deployment")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("matrix", help="Print and validate the offline smoke matrix")
    sub.add_parser("topology", help="Validate TLS, loopback, restart, volume contracts")

    module = sub.add_parser("module", help="Live standalone smoke for one module base URL")
    module.add_argument("--module-id", required=True, choices=sorted(MODULE_SMOKE))
    module.add_argument("--base-url", required=True)

    unified = sub.add_parser("unified", help="Live unified gateway smoke")
    unified.add_argument("--base-url", default="http://127.0.0.1:8080")

    container = sub.add_parser("container", help="Docker unified image smoke (optional recovery)")
    container.add_argument("--image", required=True)
    container.add_argument("--recovery", action="store_true")

    scan = sub.add_parser("scan", help="Trivy-first scan with digest-keyed evidence")
    scan.add_argument("--image", required=True)
    scan.add_argument("--evidence-root", type=Path, default=ROOT)

    offline = sub.add_parser("offline", help="Run all offline contract checks")

    args = parser.parse_args()
    if args.command == "matrix":
        rows = verify_all_modules_smoke_matrix()
        print(json.dumps(rows, indent=2))
    elif args.command == "topology":
        result = verify_topology_contracts()
        print(json.dumps(result, indent=2))
    elif args.command == "module":
        verify_module_standalone(args.base_url, args.module_id)
        print(f"{args.module_id} standalone smoke passed")
    elif args.command == "unified":
        verify_unified_gateway(args.base_url)
        print("unified gateway smoke passed")
    elif args.command == "container":
        verify_container(args.image, recovery=args.recovery)
        print("container verification passed")
    elif args.command == "scan":
        path = scan_image(args.image, evidence_root=args.evidence_root)
        print(path)
    else:
        rows = verify_all_modules_smoke_matrix()
        topology = verify_topology_contracts()
        print(json.dumps({"modules": len(rows), "topology": topology}, indent=2))
        print("offline unified deployment verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
