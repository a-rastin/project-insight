"""Run unified module processes and forward container termination cleanly."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Event
from typing import Any


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ProcessSpec:
    command: tuple[str, ...]
    cwd: str
    env: dict[str, str]


def build_process_specs(manifest: dict[str, Any]) -> dict[str, ProcessSpec]:
    specs: dict[str, ProcessSpec] = {}
    for module in manifest["modules"]:
        environment = {
            key: str(value) for key, value in module["environment"].items()
        }
        environment.update(
            {
                "PORT": str(module["internalPort"]),
                "DATABASE_PATH": module["databasePath"],
            }
        )
        environment.setdefault("PYTHONUNBUFFERED", "1")
        specs[module["moduleId"]] = ProcessSpec(
            command=tuple(module["command"]),
            cwd=module["workingDirectory"],
            env=environment,
        )
    specs["nginx"] = ProcessSpec(
        command=("nginx", "-g", "daemon off;", "-c", "/opt/deployment/nginx.conf"),
        cwd="/opt/deployment",
        env={},
    )
    return specs


def load_manifest(path: Path = ROOT / "manifest.json") -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class Supervisor:
    def __init__(self, manifest: dict[str, Any]) -> None:
        self.specs = build_process_specs(manifest)
        self.processes: dict[str, subprocess.Popen[bytes]] = {}
        self.stopping = Event()
        self.stop_timeout = max(
            module["shutdown"]["timeoutSeconds"] for module in manifest["modules"]
        )

    def install_signal_handlers(self) -> None:
        signal.signal(signal.SIGTERM, self._handle_stop)
        signal.signal(signal.SIGINT, self._handle_stop)

    def _handle_stop(self, _signum: int, _frame: Any) -> None:
        self.stopping.set()
        self.stop_children()

    def start_children(self) -> None:
        inherited = os.environ.copy()
        for name, spec in self.specs.items():
            environment = inherited | spec.env
            self.processes[name] = subprocess.Popen(
                spec.command,
                cwd=spec.cwd,
                env=environment,
                start_new_session=True,
            )

    def stop_children(self) -> None:
        for process in self.processes.values():
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        deadline = time.monotonic() + self.stop_timeout
        while time.monotonic() < deadline and any(
            process.poll() is None for process in self.processes.values()
        ):
            time.sleep(0.1)
        for process in self.processes.values():
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def run(self) -> int:
        self.install_signal_handlers()
        try:
            self.start_children()
            while not self.stopping.is_set():
                for name, process in self.processes.items():
                    result = process.poll()
                    if result is not None:
                        self.stopping.set()
                        if result != 0:
                            print(f"{name} exited with status {result}", file=sys.stderr)
                        return result
                time.sleep(0.2)
            return 0
        finally:
            self.stop_children()


def main() -> int:
    return Supervisor(load_manifest()).run()


if __name__ == "__main__":
    raise SystemExit(main())
