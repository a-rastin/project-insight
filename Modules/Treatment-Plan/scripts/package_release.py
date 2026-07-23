"""Cross-platform release image build, SBOM, scan, and human-gated promotion."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).parents[1]
IMMUTABLE_IMAGE = re.compile(r"^[^@\s]+@sha256:([0-9a-f]{64})$")


def immutable_image_reference(image: str) -> str:
    """Reject mutable tags at artifact verification and promotion boundaries."""
    if not IMMUTABLE_IMAGE.fullmatch(image):
        raise ValueError("image reference must use immutable @sha256 digest")
    return image


def image_digest(image: str) -> str:
    match = IMMUTABLE_IMAGE.fullmatch(immutable_image_reference(image))
    assert match is not None
    return "sha256:" + match.group(1)


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=capture)


def clinical_release_gates() -> None:
    run([sys.executable, "scripts/check_tp01_release_gate.py"])
    run([sys.executable, "scripts/check_tp21_clinical_safety_case.py"])


def build(image: str) -> None:
    run([
        "docker", "buildx", "build", "--file", "Dockerfile.release", "--load",
        "--sbom=true", "--provenance=mode=max", "--tag", image, ".",
    ])
    metadata = json.loads(run(["docker", "image", "inspect", image], capture=True).stdout)[0]
    user = metadata.get("Config", {}).get("User", "")
    if user not in {"10001", "10001:10001"}:
        raise RuntimeError("release image is not configured for the non-root runtime user")


def sbom(image: str, output: Path) -> None:
    immutable_image_reference(image)
    result = run(["docker", "sbom", "--format", "spdx-json", image], capture=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "image": image,
        "digest": image_digest(image),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "format": "spdx-json",
        "document": json.loads(result.stdout),
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_scan_evidence(root: Path, image: str, *, scanner: str, report: dict) -> Path:
    digest = image_digest(image)
    destination = root / "artifacts" / "scans" / f"{digest.replace(':', '-')}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "image": image,
        "digest": digest,
        "scanner": scanner,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "report": report,
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def scan_evidence_for_image(root: Path, image: str) -> dict:
    digest = image_digest(image)
    path = root / "artifacts" / "scans" / f"{digest.replace(':', '-')}.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def scan(image: str, *, evidence_root: Path | None = None) -> Path | None:
    """Scan with Trivy first; Docker Scout is optional developer fallback only."""
    immutable_image_reference(image)
    root = evidence_root or ROOT
    if shutil.which("trivy"):
        result = subprocess.run(
            [
                "trivy", "image", "--exit-code", "1", "--severity", "HIGH,CRITICAL",
                "--format", "json", image,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
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
        )
        report = {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
        evidence = write_scan_evidence(root, image, scanner="docker-scout", report=report)
        if result.returncode:
            raise RuntimeError(f"Docker Scout scan failed for {image}; evidence={evidence}")
        return evidence
    raise RuntimeError("image scan failed, or neither Trivy nor Docker Scout is available")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "sbom", "scan", "promote"))
    parser.add_argument("--image", default="insight-treatment-plan:0.1.0")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "treatment-plan.spdx.json")
    parser.add_argument("--evidence-root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.command == "build":
        build(args.image)
    elif args.command == "sbom":
        sbom(args.image, args.output)
    elif args.command == "scan":
        path = scan(args.image, evidence_root=args.evidence_root)
        if path is not None:
            print(path)
    else:
        clinical_release_gates()
        scan(args.image, evidence_root=args.evidence_root)
        print("promotion gates passed; deploy the immutable image digest, not a mutable tag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
