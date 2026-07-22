"""Production adapter that reads immutable contract artifacts from disk."""
from __future__ import annotations

import json
import re
from pathlib import Path


class FilesystemContractAdapter:
    """Load common contract documents without importing module/domain code."""

    def __init__(self, contracts_root: Path):
        self.root = Path(contracts_root).resolve()

    def _load(self, path: Path):
        resolved = path.resolve()
        if self.root not in resolved.parents:
            raise ValueError("contract path escapes package root")
        if not resolved.is_file():
            raise KeyError(str(path))
        with resolved.open(encoding="utf-8") as handle:
            return json.load(handle)

    def get_schema(self, version: str, name: str):
        if not re.fullmatch(r"\d+\.\d+\.\d+", version) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", name):
            raise ValueError("invalid schema coordinates")
        return self._load(self.root / "schemas" / version / f"{name}.schema.json")

    def get_openapi(self):
        return self._load(self.root / "openapi" / "1.0.0" / "common.openapi.json")

    def get_contract(self):
        return self._load(self.root / "examples" / "1.0.0" / "module-contract.json")
