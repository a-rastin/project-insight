"""Offline TP-05 JSON Schema, example, compatibility, and OpenAPI conformance."""
from __future__ import annotations

import json, re, sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urldefrag
from uuid import UUID

ROOT = Path(__file__).parents[1]
SCHEMAS = ROOT / "contracts" / "schemas"
EXAMPLES = ROOT / "contracts" / "examples"
OPENAPI = ROOT / "contracts" / "openapi" / "treatment-plan.openapi.v1.0.0.json"

class ContractError(ValueError): pass

def load(path: Path):
    with path.open(encoding="utf-8") as handle: return json.load(handle)

def _pointer(document, fragment):
    value = document
    if fragment:
        if not fragment.startswith("/"): raise ContractError(f"unsupported fragment #{fragment}")
        for token in fragment[1:].split("/"):
            value = value[token.replace("~1", "/").replace("~0", "~")]
    return value

def validate(instance, schema, schema_path: Path, location="$", document=None):
    document = schema if document is None else document
    if "$ref" in schema:
        file_part, fragment = urldefrag(schema["$ref"])
        if file_part:
            target_path = (schema_path.parent / file_part).resolve(); target = load(target_path)
            return validate(instance, _pointer(target, fragment), target_path, location, target)
        return validate(instance, _pointer(document, fragment), schema_path, location, document)
    if "oneOf" in schema:
        matches = 0
        for candidate in schema["oneOf"]:
            try: validate(instance, candidate, schema_path, location, document); matches += 1
            except ContractError: pass
        if matches != 1: raise ContractError(f"{location}: expected exactly one matching schema")
    if "const" in schema and instance != schema["const"]: raise ContractError(f"{location}: expected {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]: raise ContractError(f"{location}: value is not in enum")
    expected = schema.get("type")
    checks = {"object": lambda x:isinstance(x,dict), "array": lambda x:isinstance(x,list), "string": lambda x:isinstance(x,str), "integer": lambda x:isinstance(x,int) and not isinstance(x,bool), "number": lambda x:isinstance(x,(int,float)) and not isinstance(x,bool), "boolean": lambda x:isinstance(x,bool), "null": lambda x:x is None}
    if expected and not checks[expected](instance): raise ContractError(f"{location}: expected {expected}")
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance: raise ContractError(f"{location}: missing required property {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(instance) - set(properties))
            if unknown: raise ContractError(f"{location}: unknown properties {unknown}")
        for key, value in instance.items():
            if key in properties: validate(value, properties[key], schema_path, f"{location}.{key}", document)
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0): raise ContractError(f"{location}: too few items")
        if schema.get("uniqueItems") and len({json.dumps(x,sort_keys=True) for x in instance}) != len(instance): raise ContractError(f"{location}: duplicate items")
        if "items" in schema:
            for index, value in enumerate(instance): validate(value, schema["items"], schema_path, f"{location}[{index}]", document)
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0): raise ContractError(f"{location}: string is too short")
        if "pattern" in schema and not re.search(schema["pattern"], instance): raise ContractError(f"{location}: pattern mismatch")
        if schema.get("format") == "uuid":
            try:
                parsed=UUID(instance)
                if str(parsed) != instance or parsed.int == 0: raise ValueError
            except ValueError: raise ContractError(f"{location}: invalid canonical non-nil UUID")
        if schema.get("format") == "date-time":
            try:
                if not instance.endswith("Z"): raise ValueError
                datetime.fromisoformat(instance[:-1] + "+00:00")
            except ValueError: raise ContractError(f"{location}: invalid UTC date-time")
    if isinstance(instance, (int,float)) and not isinstance(instance,bool) and instance < schema.get("minimum", instance): raise ContractError(f"{location}: below minimum")

def schema_for(version, name): return SCHEMAS / version / f"{name}.schema.json"

def validate_examples():
    registry=load(ROOT/"contracts"/"schema-registry.v1.json")
    for version in registry["versions"]:
        for name in registry["schemas"]:
            validate(load(EXAMPLES/version/f"{name}.json"), load(schema_for(version,name)), schema_for(version,name))

def check_compatibility():
    """Every later compatible version must continue accepting earlier same-major examples."""
    versions=sorted((p.name for p in SCHEMAS.iterdir() if p.is_dir()), key=lambda x:tuple(map(int,x.split("."))))
    registry=load(ROOT/"contracts"/"schema-registry.v1.json")
    for candidate in versions:
        major=int(candidate.split(".")[0])
        for earlier in versions:
            if int(earlier.split(".")[0]) != major or tuple(map(int,earlier.split("."))) > tuple(map(int,candidate.split("."))): continue
            for name in registry["schemas"]:
                validate(load(EXAMPLES/earlier/f"{name}.json"),load(schema_for(candidate,name)),schema_for(candidate,name))

def lint_openapi():
    spec=load(OPENAPI)
    if spec.get("openapi") != "3.1.0": raise ContractError("OpenAPI must be 3.1.0")
    if spec.get("info",{}).get("version") != "1.0.0": raise ContractError("OpenAPI info.version mismatch")
    operation_ids=[]
    for route,item in spec.get("paths",{}).items():
        for method,operation in item.items():
            if method not in {"get","post","put","patch","delete"}: continue
            oid=operation.get("operationId")
            if not oid: raise ContractError(f"{method.upper()} {route}: missing operationId")
            operation_ids.append(oid)
            if not operation.get("responses"): raise ContractError(f"{oid}: missing responses")
    if len(operation_ids) != len(set(operation_ids)): raise ContractError("duplicate operationId")
    def walk(value, path=OPENAPI):
        if isinstance(value,dict):
            if "$ref" in value:
                file_part,fragment=urldefrag(value["$ref"])
                target_path=(path.parent/file_part).resolve() if file_part else OPENAPI
                target=load(target_path); _pointer(target,fragment)
            for child in value.values(): walk(child,path)
        elif isinstance(value,list):
            for child in value: walk(child,path)
    walk(spec)

def run(): validate_examples(); check_compatibility(); lint_openapi()

if __name__ == "__main__":
    try: run()
    except (ContractError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(f"TP-05 CONTRACTS: INVALID: {exc}", file=sys.stderr); raise SystemExit(1)
    print("TP-05 CONTRACTS: VALID")
