"""Generated from contracts/openapi/1.0.0/common.openapi.json; do not edit."""
from __future__ import annotations


class CommonContractsClient:
    """Small generated client; transport is injected by the consuming module."""

    def __init__(self, get_json):
        self._get_json = get_json

    def get_contract(self):
        return self._get_json("/contract")

    def get_openapi(self):
        return self._get_json("/openapi.json")

    def get_schema(self, version: str, name: str):
        return self._get_json(f"/schemas/{version}/{name}")
