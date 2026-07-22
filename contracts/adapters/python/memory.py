"""In-memory test adapter implementing the production registry interface."""
from __future__ import annotations

from pathlib import Path

from .filesystem import FilesystemContractAdapter


class InMemoryContractAdapter:
    def __init__(self, schemas: dict[tuple[str, str], dict], openapi: dict, contract: dict):
        self._schemas = schemas
        self._openapi = openapi
        self._contract = contract

    @classmethod
    def from_directory(cls, contracts_root: Path):
        filesystem = FilesystemContractAdapter(contracts_root)
        version_dir = Path(contracts_root) / "schemas" / "1.0.0"
        schemas = {
            ("1.0.0", path.name.removesuffix(".schema.json")): filesystem.get_schema("1.0.0", path.name.removesuffix(".schema.json"))
            for path in version_dir.glob("*.schema.json")
        }
        return cls(schemas, filesystem.get_openapi(), filesystem.get_contract())

    def get_schema(self, version: str, name: str):
        try:
            return self._schemas[(version, name)]
        except KeyError as exc:
            raise KeyError(f"{version}/{name}") from exc

    def get_openapi(self):
        return self._openapi

    def get_contract(self):
        return self._contract
