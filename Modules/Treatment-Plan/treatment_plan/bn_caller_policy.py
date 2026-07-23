"""BN-05 — caller-aware BN Manager adapter for the Treatment Plan surface.

The Treatment Plan service authorizes a psychiatrist to call the BN Manager
``/api/bn-manager/v1/treatment-plan/evaluate`` route. The adapter forwards the
psychiatrist's session cookie and CSRF token and uses the canonical BN Manager
request body shape (``{"model": {"model_id": ...}, "evidence": ...}``). The BN
Manager derives the caller identity server-side from the forwarded session, so
psychiatrist attribution is preserved without Treatment Plan signing the
caller claim itself.

Deliberately kept thin (rule 4 of the BN-05 work-packet): no normalization of
``NormalizedSnapshotFacts``, no ``_MODEL_RULES`` touch, no orchestrator storage.
The contract surface is :class:`Caller`, ``BnManagerTreatmentPlanEvaluator``,
and the ``RawBnEvaluation`` returned by the existing ``bn_evaluation`` seam.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import httpx

from .bn_evaluation import BnModel, MAPPING_VERSION, RawBnEvaluation


EVALUATE_PATH = "/api/bn-manager/v1/treatment-plan/evaluate"
_STABLE_ID_PREFIX = "bnm."


@dataclass(frozen=True)
class Caller:
    """Per-request psychiatrist caller forwarded to the BN Manager.

    The cookie and CSRF token are the verbatim values from the Treatment Plan
    request so the BN Manager session adapter re-runs authn/authz and records
    the psychiatrist as ``evaluated_by``. ``surface`` defaults to the Treatment
    Plan surface name that the BN Manager evaluate route stamps on the audit
    record.
    """

    subject: str
    roles: frozenset[str]
    csrf_token: str
    cookie: str
    surface: str = "Treatment Plan"


def _stable_id(model: BnModel) -> str:
    return _STABLE_ID_PREFIX + model.value


class BnManagerTreatmentPlanEvaluator:
    """Caller-aware HTTP adapter for the owned Treatment Plan BN Manager route.

    Constructed per request with the resolved psychiatrist caller. Sends the
    canonical request body and raises ``httpx.HTTPStatusError`` on any non-2xx
    response so the caller surface maps the upstream status to the Treatment
    Plan error envelope.
    """

    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient,
        caller: Caller,
        timeout_seconds: float = 3.0,
    ) -> None:
        if not caller.cookie:
            raise ValueError("Caller.cookie is required for the BN Manager forward")
        if not caller.csrf_token:
            raise ValueError("Caller.csrf_token is required for the BN Manager forward")
        self._base_url = base_url.rstrip("/")
        self._client = client
        self._caller = caller
        self._timeout = timeout_seconds

    async def evaluate(
        self,
        model: BnModel,
        evidence: Mapping[str, str],
        mapping_version: str = MAPPING_VERSION,
    ) -> RawBnEvaluation:
        response = await self._client.post(
            f"{self._base_url}{EVALUATE_PATH}",
            headers={
                "Cookie": self._caller.cookie,
                "x-csrf-token": self._caller.csrf_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={
                "model": {"model_id": _stable_id(model)},
                "evidence": dict(evidence),
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            raise ValueError("BN Manager evaluate response is missing its data envelope")
        evaluation = data.get("evaluation")
        if not isinstance(evaluation, dict):
            raise ValueError("BN Manager evaluate response is missing the evaluation record")
        return RawBnEvaluation(
            evaluation_id=evaluation.get("evaluationId"),
            model_id=evaluation.get("modelId"),
            model_version=evaluation.get("modelVersion"),
            model_hash=evaluation.get("modelHash"),
            posterior=evaluation.get("posterior"),
            evaluated_at=evaluation.get("evaluatedAt"),
        )
