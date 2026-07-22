"""Validate unique ownership and REST-only cross-module relationship rules."""

from __future__ import annotations

import json
from pathlib import Path


def evaluate(registry: dict) -> list[str]:
    failures: list[str] = []
    entities = registry.get("entities", [])
    names = [item.get("entity") for item in entities]
    duplicates = sorted({name for name in names if name and names.count(name) > 1})
    if duplicates:
        failures.append("entities with multiple ownership records: " + ", ".join(duplicates))
    for item in entities:
        missing = [key for key in ("entity", "owner", "id", "idKind") if not item.get(key)]
        if missing:
            failures.append(f"incomplete ownership record {item.get('entity', '<unnamed>')}: {', '.join(missing)}")
    required = {"Patient", "Encounter", "Medication Knowledge", "Recommendation", "Final Plan"}
    if not required.issubset(set(names)):
        failures.append("missing required entities: " + ", ".join(sorted(required - set(names))))
    if not any(str(name).startswith("Assessment:") for name in names):
        failures.append("no assessment type ownership registered")
    if not any(str(name).startswith("Audit:") for name in names):
        failures.append("no audit type ownership registered")

    policy = registry.get("relationshipPolicy", {})
    expected = {
        "transport": "internal_rest_only",
        "stableIdentifiersRequired": True,
        "crossDatabaseAccessAllowed": False,
        "crossModuleWritesAllowed": False,
        "cachedReferencesAreAuthoritative": False,
    }
    for key, value in expected.items():
        if policy.get(key) != value:
            failures.append(f"unsafe relationship policy: {key} must be {value!r}")
    return failures


def main() -> int:
    registry_path = Path(__file__).parents[1] / "governance" / "context-ownership.v1.json"
    failures = evaluate(json.loads(registry_path.read_text(encoding="utf-8")))
    if failures:
        print("TP-02 CONTEXT OWNERSHIP: INVALID")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("TP-02 CONTEXT OWNERSHIP: VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
