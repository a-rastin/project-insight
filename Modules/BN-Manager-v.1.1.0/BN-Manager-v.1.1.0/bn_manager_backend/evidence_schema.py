from __future__ import annotations

import hashlib
from typing import Any

from clinical_graph_models.model import ClinicalGraphModel, Node

from .model_registry import ModelRegistryEntry


def model_content_hash(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def build_evidence_schema(
    entry: ModelRegistryEntry,
    model: ClinicalGraphModel,
    text: str,
) -> dict[str, Any]:
    """Expose allowed evidence nodes/states, required/optional membership, target, version/hash.

    Semantic meaning is taken only from author-supplied VARIABLE PROPERTY text in the
    owned XML. Required evidence is empty unless a node explicitly declares
    ``required=true``; clinical owners have not approved required flags on the
    four canonical networks, so callers must treat all evidence as optional unless
    a later owned property marks otherwise.
    """
    node_map = model.node_map()
    target_node = node_map.get(entry.target_node)
    if target_node is None:
        raise KeyError(entry.target_node)

    allowed: list[dict[str, Any]] = []
    for node in model.nodes:
        if node.kind != "chance" or node.name == entry.target_node:
            continue
        allowed.append(_evidence_node_payload(node))

    required_evidence = [item["node_id"] for item in allowed if item["required"]]
    optional_evidence = [item["node_id"] for item in allowed if not item["required"]]

    return {
        "stable_id": entry.stable_id,
        "title": entry.title,
        "status": entry.status,
        "model_version": entry.active_version,
        "active_version": entry.active_version,
        "model_hash": model_content_hash(text),
        "target": {
            "node_id": target_node.name,
            "label": target_node.label,
            "kind": target_node.kind,
            "states": list(target_node.states),
            "semantic_meaning": _semantic_meaning(target_node),
        },
        "allowed_evidence": allowed,
        "required_evidence": required_evidence,
        "optional_evidence": optional_evidence,
        "schema": {
            "format": "XML",
            "version": "0.3",
            "path": entry.schema_path,
        },
    }


def _evidence_node_payload(node: Node) -> dict[str, Any]:
    return {
        "node_id": node.name,
        "label": node.label,
        "kind": node.kind,
        "states": list(node.states),
        "required": _is_required(node),
        "semantic_meaning": _semantic_meaning(node),
    }


def _is_required(node: Node) -> bool:
    raw = node.attributes.get("required")
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return raw.strip().lower() in {"true", "1", "yes", "required"}
    return False


def _semantic_meaning(node: Node) -> str:
    extras = node.attributes.get("properties")
    if isinstance(extras, list):
        parts = [str(item).strip() for item in extras if str(item).strip()]
        if parts:
            return " ".join(parts)
    for key in ("semantic_meaning", "description", "meaning"):
        value = node.attributes.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""
