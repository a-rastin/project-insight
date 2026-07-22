"""Validate the shared TP-03 identifier and transport contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

UUID_SAMPLE = "123e4567-e89b-42d3-a456-426614174000"


def evaluate(contract: dict) -> list[str]:
    failures: list[str] = []
    if contract.get("schemaVersion") != "1.0.0":
        failures.append("schemaVersion must be 1.0.0")
    if contract.get("contractId") != "insight.identifier-transport":
        failures.append("contractId must identify the shared interface")

    identifiers = contract.get("identifiers", {})
    uuid_rule = identifiers.get("canonicalUuid", {})
    try:
        uuid_pattern = re.compile(uuid_rule.get("pattern", ""))
    except re.error as error:
        failures.append(f"canonical UUID pattern is invalid: {error}")
        uuid_pattern = None
    if uuid_pattern and not uuid_pattern.fullmatch(UUID_SAMPLE):
        failures.append("canonical UUID pattern rejects a lowercase RFC 4122 UUID")
    if uuid_pattern and uuid_pattern.fullmatch(UUID_SAMPLE.upper()):
        failures.append("canonical UUID pattern accepts non-canonical uppercase UUIDs")
    if uuid_rule.get("generation") != "UUIDv4" or uuid_rule.get("nilAllowed") is not False:
        failures.append("UUID generation must be v4 and nil UUIDs must be forbidden")
    for name in ("patientId", "encounterId"):
        rule = identifiers.get(name, {})
        if rule.get("kind") != "canonicalUuid" or rule.get("owner") != "Add New Patient" or rule.get("immutable") is not True:
            failures.append(f"{name} must be an immutable canonical UUID owned by Add New Patient")

    alias = contract.get("patientAlias", {})
    if alias.get("name") != "patientCode" or alias.get("pattern") != "^[A-Z0-9]{6}$":
        failures.append("patientCode must be exactly six uppercase ASCII letters/digits")
    for flag, expected in (("unique", True), ("immutable", True), ("reusable", False), ("foreignKeyAllowed", False)):
        if alias.get(flag) is not expected:
            failures.append(f"patientCode {flag} must be {expected}")
    for case, status in {"malformed": 400, "notFound": 404, "collision": 409, "creationCollision": 409}.items():
        if alias.get("resolution", {}).get(case, {}).get("status") != status:
            failures.append(f"alias {case} must return HTTP {status}")

    encounter = contract.get("encounter", {})
    for flag in ("patientBindingImmutable", "followUpCreatesNewEncounter", "selectionByTimestampForbidden", "crossEncounterMixingForbidden"):
        if encounter.get(flag) is not True:
            failures.append(f"encounter rule {flag} must be true")

    time_rule = contract.get("time", {})
    if time_rule.get("utcOffsetRequired") != "Z" or time_rule.get("timezoneFormat") != "IANA TZ database name":
        failures.append("time interface must require UTC instants and IANA timezones")
    try:
        instant_pattern = re.compile(time_rule.get("instantPattern", ""))
    except re.error as error:
        failures.append(f"instant pattern is invalid: {error}")
    else:
        if not instant_pattern.fullmatch("2026-07-13T11:22:33.123Z"):
            failures.append("instant pattern rejects a canonical UTC timestamp")
        if instant_pattern.fullmatch("2026-07-13T04:22:33-07:00"):
            failures.append("instant pattern accepts a non-UTC offset")

    headers = contract.get("headers", {})
    required = {"X-Request-ID", "X-Correlation-ID", "X-Causation-ID", "Idempotency-Key", "X-Schema-Version", "ETag", "If-Match"}
    missing = sorted(required - set(headers))
    if missing:
        failures.append("missing headers: " + ", ".join(missing))
    if headers.get("X-Correlation-ID", {}).get("forwardUnchanged") is not True:
        failures.append("X-Correlation-ID must be forwarded unchanged")

    behavior = contract.get("behavior", {})
    for name, status in {"invalidIdentifier": 400, "invalidHeader": 400, "unsupportedSchemaVersion": 422, "idempotencyConflict": 409, "etagMismatch": 412, "missingPrecondition": 428}.items():
        if behavior.get(name, {}).get("status") != status:
            failures.append(f"{name} must return HTTP {status}")
    if behavior.get("errorMediaType") != "application/problem+json":
        failures.append("errors must use application/problem+json")
    return failures


def main(path: str | None = None) -> int:
    contract_path = Path(path) if path else Path(__file__).parents[1] / "contracts" / "identifier-transport-contract.v1.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"TP-03 IDENTIFIER CONTRACT: INVALID\n- cannot load contract: {error}")
        return 1
    failures = evaluate(contract)
    if failures:
        print("TP-03 IDENTIFIER CONTRACT: INVALID")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("TP-03 IDENTIFIER CONTRACT: VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
