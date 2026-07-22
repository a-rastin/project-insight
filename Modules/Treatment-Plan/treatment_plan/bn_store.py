"""Persistence adapter for TP-10 BN evaluation bundles."""
import json
from typing import Any

from .bn_evaluation import BnEvaluationBundle
from .repository import RuntimeRecord


class RepositoryBnEvaluationStore:
    """Store canonical immutable BN bundles through the module repository seam."""

    def __init__(self, repository: Any):
        self._repository = repository

    def save(self, bundle: BnEvaluationBundle) -> None:
        key = f"bn-evaluation:{bundle.snapshot_id}"
        value = json.dumps(
            {"bundle": bundle.to_dict(), "contentHash": bundle.content_hash},
            sort_keys=True, separators=(",", ":"),
        )
        previous = self._repository.get(key)
        if previous is not None and previous.value != value:
            raise ValueError("a different BN bundle is already stored for this snapshot")
        if previous is None:
            self._repository.put(RuntimeRecord(key, value))
