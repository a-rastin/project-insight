from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ModuleRegistration:
    module_id: str
    title: str
    roles: tuple[str, ...]
    contract_url: str


def ready_url_for(contract_url: str) -> str:
    parsed = urlsplit(contract_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or not parsed.path.endswith("/contract"):
        raise ValueError("contractUrl must be an HTTP(S) URL ending in /contract")
    path = f"{parsed.path[:-len('/contract')]}/ready"
    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, ""))


def _request_json(url: str, timeout_seconds: float) -> tuple[int | None, dict[str, Any] | None, str | None]:
    request = Request(url, headers={"accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            status = response.status
            body = response.read()
    except HTTPError as error:
        status = error.code
        body = error.read()
        error.close()
    except (OSError, URLError, TimeoutError) as error:
        return None, None, type(error).__name__

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return status, None, "invalid JSON"
    if not isinstance(payload, dict):
        return status, None, "JSON response is not an object"
    return status, payload, None


def discover_module(registration: ModuleRegistration, timeout_seconds: float) -> dict[str, Any]:
    contract_status, contract, contract_error = _request_json(registration.contract_url, timeout_seconds)
    ready_status, readiness, ready_error = _request_json(ready_url_for(registration.contract_url), timeout_seconds)

    result: dict[str, Any] = {
        "moduleId": registration.module_id,
        "title": registration.title,
        "href": None,
    }
    if contract_status is None:
        result.update(status="unavailable", reason=f"contract endpoint unavailable ({contract_error})")
        return result
    if contract_status < 200 or contract_status >= 300:
        result.update(status="unavailable", reason=f"contract endpoint returned HTTP {contract_status}")
        return result
    if contract_error or contract is None:
        result.update(status="incompatible", reason=f"contract response is invalid ({contract_error})")
        return result

    module_id = contract.get("moduleId")
    interface_version = contract.get("interfaceVersion")
    base_path = contract.get("basePath")
    if module_id != registration.module_id:
        result.update(status="incompatible", reason=f"contract moduleId is {module_id!r}, expected {registration.module_id!r}")
        return result
    if not isinstance(interface_version, str) or interface_version.split(".", 1)[0] != "1":
        result.update(status="incompatible", reason=f"unsupported interfaceVersion {interface_version!r}")
        return result
    if not isinstance(base_path, str) or not base_path.startswith("/"):
        result.update(status="incompatible", reason="contract basePath is missing or invalid")
        return result

    result["href"] = base_path
    if ready_status is None:
        result.update(status="degraded", reason=f"readiness endpoint unavailable ({ready_error})")
    elif ready_status < 200 or ready_status >= 300:
        result.update(status="degraded", reason=f"readiness endpoint returned HTTP {ready_status}")
    elif ready_error or readiness is None:
        result.update(status="degraded", reason=f"readiness response is invalid ({ready_error})")
    elif readiness.get("status") != "ready":
        result.update(status="degraded", reason=f"readiness status is {readiness.get('status')!r}")
    else:
        result.update(status="available", reason="contract and readiness checks passed")
    return result
