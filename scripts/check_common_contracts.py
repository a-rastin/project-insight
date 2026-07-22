"""Offline checks for the root-owned common interface contract package."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urldefrag
from uuid import UUID


class ContractError(ValueError):
    pass


class CompatibilityError(ContractError):
    pass


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _pointer(document, fragment):
    value = document
    if fragment:
        if not fragment.startswith("/"):
            raise ContractError(f"unsupported fragment #{fragment}")
        for token in fragment[1:].split("/"):
            value = value[token.replace("~1", "/").replace("~0", "~")]
    return value


def _resolve_ref(ref, schema_path: Path, document):
    file_part, fragment = urldefrag(ref)
    if file_part:
        target_path = (schema_path.parent / file_part).resolve()
        if not target_path.is_file():
            raise ContractError(f"unresolved reference: {ref}")
        target = load_json(target_path)
        return _pointer(target, fragment), target_path, target
    return _pointer(document, fragment), schema_path, document


def validate_instance(instance, schema, schema_path: Path, location="$", document=None):
    document = schema if document is None else document
    if "$ref" in schema:
        target, target_path, target_document = _resolve_ref(schema["$ref"], schema_path, document)
        return validate_instance(instance, target, target_path, location, target_document)
    if "allOf" in schema:
        for candidate in schema["allOf"]:
            validate_instance(instance, candidate, schema_path, location, document)
    if "oneOf" in schema:
        matches = 0
        for candidate in schema["oneOf"]:
            try:
                validate_instance(instance, candidate, schema_path, location, document)
                matches += 1
            except ContractError:
                pass
        if matches != 1:
            raise ContractError(f"{location}: expected exactly one matching schema")
    if "const" in schema and instance != schema["const"]:
        raise ContractError(f"{location}: expected {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise ContractError(f"{location}: value is not in enum")
    expected = schema.get("type")
    checks = {
        "object": lambda value: isinstance(value, dict),
        "array": lambda value: isinstance(value, list),
        "string": lambda value: isinstance(value, str),
        "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
        "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": lambda value: isinstance(value, bool),
        "null": lambda value: value is None,
    }
    if expected and not checks[expected](instance):
        raise ContractError(f"{location}: expected {expected}")
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                raise ContractError(f"{location}: missing required property {key}")
        properties = schema.get("properties", {})
        unknown = sorted(set(instance) - set(properties))
        additional = schema.get("additionalProperties", {})
        if unknown and additional is False:
            raise ContractError(f"{location}: unknown properties {unknown}")
        for key, value in instance.items():
            if key in properties:
                validate_instance(value, properties[key], schema_path, f"{location}.{key}", document)
            elif isinstance(additional, dict):
                validate_instance(value, additional, schema_path, f"{location}.{key}", document)
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            raise ContractError(f"{location}: too few items")
        if schema.get("uniqueItems") and len({json.dumps(value, sort_keys=True) for value in instance}) != len(instance):
            raise ContractError(f"{location}: duplicate items")
        if "items" in schema:
            for index, value in enumerate(instance):
                validate_instance(value, schema["items"], schema_path, f"{location}[{index}]", document)
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            raise ContractError(f"{location}: string is too short")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            raise ContractError(f"{location}: pattern mismatch")
        if schema.get("format") == "uuid":
            try:
                parsed = UUID(instance)
                if str(parsed) != instance or parsed.int == 0:
                    raise ValueError
            except ValueError as exc:
                raise ContractError(f"{location}: invalid canonical non-nil UUID") from exc
        if schema.get("format") == "date-time":
            try:
                if not instance.endswith("Z"):
                    raise ValueError
                datetime.fromisoformat(instance[:-1] + "+00:00")
            except ValueError as exc:
                raise ContractError(f"{location}: invalid UTC date-time") from exc
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if instance < schema.get("minimum", instance) or instance > schema.get("maximum", instance):
            raise ContractError(f"{location}: number outside allowed range")


def check_examples(root: Path):
    manifest = load_json(root / "examples" / "manifest.json")
    for filename, name in manifest.items():
        example_path = root / "examples" / "1.0.0" / filename
        schema_path = root / "schemas" / "1.0.0" / f"{name}.schema.json"
        validate_instance(load_json(example_path), load_json(schema_path), schema_path)


def check_openapi_references(root: Path):
    path = root / "openapi" / "1.0.0" / "common.openapi.json"
    document = load_json(path)

    def walk(value, current_path: Path, current_document):
        if isinstance(value, dict):
            if "$ref" in value:
                target, _, _ = _resolve_ref(value["$ref"], current_path, current_document)
                if target is None:
                    raise ContractError(f"empty reference: {value['$ref']}")
            for child in value.values():
                walk(child, current_path, current_document)
        elif isinstance(value, list):
            for child in value:
                walk(child, current_path, current_document)

    walk(document, path, document)


def check_schema_compatibility(baseline, candidate, examples, name="schema"):
    for index, example in enumerate(examples):
        try:
            validate_instance(example, baseline, Path(f"{name}.baseline.json"))
            validate_instance(example, candidate, Path(f"{name}.candidate.json"))
        except ContractError as exc:
            raise CompatibilityError(f"{name}: candidate rejects baseline example {index}: {exc}") from exc


def check_no_domain_implementation(root: Path):
    policy = load_json(root / "package-policy.json")
    allowed = set(policy["allowedCodeDirectories"])
    code_suffixes = {".py", ".js", ".mjs", ".ts", ".tsx"}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in code_suffixes:
            continue
        relative = path.relative_to(root)
        if relative.parts[0] not in allowed:
            raise ContractError(f"domain implementation is outside allowed adapter/client roots: {relative}")


def run(root: Path = Path(__file__).parents[1] / "contracts"):
    check_examples(root)
    check_openapi_references(root)
    check_no_domain_implementation(root)
    print("COMMON CONTRACTS: VALID")


if __name__ == "__main__":
    try:
        run()
    except (ContractError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(f"COMMON CONTRACTS: INVALID: {exc}")
        raise SystemExit(1)
