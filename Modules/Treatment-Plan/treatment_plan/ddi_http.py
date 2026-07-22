"""HTTP adapter for the TP-13 DDI Checker seam."""
from __future__ import annotations

from typing import Any, Mapping

import httpx

from .ddi_check import SCHEMA_VERSION


class HttpDdiCheckerAdapter:
    """POST one exact medication-set check to the remote DDI Checker module."""

    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient,
        *,
        timeout_seconds: float = 2.0,
    ):
        if not isinstance(base_url, str) or not base_url.startswith(("http://", "https://")):
            raise ValueError("DDI Checker base_url must be an HTTP(S) URL")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._url = base_url.rstrip("/") + "/api/ddi-checker/v1/interaction-checks"
        self._client = client
        self._timeout = timeout_seconds

    async def check(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        idempotency_key = request.get("idempotencyKey")
        if not isinstance(idempotency_key, str) or not idempotency_key:
            raise ValueError("DDI request idempotencyKey is required")
        response = await self._client.post(
            self._url,
            json=dict(request),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Schema-Version": SCHEMA_VERSION,
                "Idempotency-Key": idempotency_key,
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, Mapping):
            raise ValueError("DDI Checker response must be a JSON object")
        return payload
