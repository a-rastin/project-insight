"""Static REST-only ownership checks for module source trees."""
from __future__ import annotations

import ast
import json
import os
import posixpath
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping, Protocol


_TEXT_SUFFIXES = {".cjs", ".js", ".json", ".mjs", ".py", ".ts", ".tsx"}
_IGNORED_PARTS = {".git", "__pycache__", ".venv", "venv", "build", "cache", "dist", "graphify-out", "node_modules"}
_ALLOWED_COMMON_IMPORTS = ("contracts.clients", "contracts.adapters")
_CLINICAL_WORDS = re.compile(
    r"\b(clinical|patient|medication|diagnos(?:is|tic)|treatment|encounter|drug|interaction|health|rxnorm)\b",
    re.IGNORECASE,
)
_PATH_LITERAL = re.compile(
    r"(?P<quote>['\"])(?P<value>[^'\"]+(?:\.sqlite3?|\.db|(?:runtime|state|active-kb)[^'\"]*\.json))(?P=quote)",
    re.IGNORECASE,
)
_NODE_IMPORT = re.compile(
    r"(?:import\s+(?:[^\"']+?\s+from\s+)?|export\s+[^\"']+?\s+from\s+|require\s*\(\s*)['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)


class SourceAdapter(Protocol):
    """Small source seam used by production and test adapters."""

    def files(self) -> Iterable[str]: ...

    def read_text(self, path: str) -> str: ...


class FilesystemSourceAdapter:
    """Production adapter that reads source files below one repository root."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def files(self) -> Iterable[str]:
        for directory, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [name for name in dirnames if name not in _IGNORED_PARTS]
            for filename in filenames:
                path = Path(directory) / filename
                if path.suffix.lower() not in _TEXT_SUFFIXES:
                    continue
                yield path.relative_to(self.root).as_posix()

    def read_text(self, path: str) -> str:
        return (self.root / PurePosixPath(path)).read_text(encoding="utf-8")


class InMemorySourceAdapter:
    """In-memory test adapter implementing the source interface."""

    def __init__(self, sources: Mapping[str, str]):
        self._sources = {
            PurePosixPath(path.replace("\\", "/")).as_posix(): text
            for path, text in sources.items()
        }

    def files(self) -> Iterable[str]:
        return tuple(sorted(self._sources))

    def read_text(self, path: str) -> str:
        return self._sources[path]


@dataclass(frozen=True)
class ArchitectureViolation:
    code: str
    source: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code}: {self.source}: {self.detail}"


def _module_roots(paths: Iterable[str]) -> dict[str, str]:
    roots: dict[str, str] = {}
    for path in paths:
        parts = PurePosixPath(path).parts
        try:
            index = parts.index("Modules")
        except ValueError:
            continue
        if index + 1 < len(parts):
            root = "/".join(parts[: index + 2])
            roots[root.casefold()] = root
    return roots


def _module_for_path(path: str, roots: Mapping[str, str]) -> str | None:
    normalized = PurePosixPath(path.replace("\\", "/")).as_posix()
    matches = [root for root in roots.values() if normalized == root or normalized.startswith(root + "/")]
    return max(matches, key=len) if matches else None


def _module_name(root: str) -> str:
    return PurePosixPath(root).parts[-1]


def _same_module_name(value: str, root: str) -> bool:
    normalize = lambda item: re.sub(r"[^a-z0-9]", "", item.casefold())
    return normalize(value) == normalize(_module_name(root))


def _common_import_allowed(value: str) -> bool:
    value = value.replace("/", ".")
    return any(value == prefix or value.startswith(prefix + ".") for prefix in _ALLOWED_COMMON_IMPORTS)


def _target_module_from_import(value: str, source_module: str | None, roots: Mapping[str, str]) -> str | None:
    value = value.replace("\\", "/")
    if value.startswith("contracts/") or value.startswith("contracts."):
        return None
    dotted_value = value.replace(".", "/")
    if dotted_value.startswith("Modules/"):
        candidate = "/".join(dotted_value.split("/")[:2])
        return roots.get(candidate.casefold())
    if value.startswith("Modules/"):
        candidate = "/".join(value.split("/")[:2])
        return roots.get(candidate.casefold())
    for root in roots.values():
        if _same_module_name(value.split(".")[0].split("/")[0], root):
            return root
    if value.startswith(".") and source_module:
        candidate = posixpath.normpath(PurePosixPath(source_module).joinpath(value).as_posix())
        parts = candidate.split("/")
        if "Modules" in parts:
            index = parts.index("Modules")
            if index + 1 < len(parts):
                return roots.get("/".join(parts[: index + 2]).casefold())
    return None


def _python_imports(path: str, text: str, roots: Mapping[str, str]) -> Iterable[str]:
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError:
        return ()
    source_module = _module_for_path(path, roots)
    targets = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                prefix = "." * node.level + module
                targets.append(prefix)
            else:
                targets.append(module)
    resolved = []
    for target in targets:
        if _common_import_allowed(target):
            continue
        target_module = _target_module_from_import(target, source_module, roots)
        if target_module and target_module != source_module:
            resolved.append(target_module)
    return tuple(resolved)


def _node_imports(path: str, text: str, roots: Mapping[str, str]) -> Iterable[str]:
    source_module = _module_for_path(path, roots)
    targets = []
    for value in _NODE_IMPORT.findall(text):
        if _common_import_allowed(value):
            continue
        target = _target_module_from_import(value, source_module, roots)
        if target and target != source_module:
            targets.append(target)
    return tuple(targets)


def _canonical_path(value: str, source_module: str | None) -> str | None:
    value = value.replace("\\", "/").strip()
    if not value or value.startswith(("http:", "https:", "data:")):
        return None
    if re.match(r"^[A-Za-z]:/", value) or value.startswith("/"):
        return posixpath.normpath(value).casefold()
    base = source_module or ""
    return posixpath.normpath(posixpath.join(base, value)).casefold()


def _path_references(path: str, text: str, source_module: str | None):
    for match in _PATH_LITERAL.finditer(text):
        value = match.group("value")
        canonical = _canonical_path(value, source_module)
        if canonical:
            yield value, canonical


def _under_module(path: str, module: str) -> bool:
    return path == module or path.startswith(module + "/")


def _config_violations(adapter: SourceAdapter, paths: tuple[str, ...], roots: Mapping[str, str]):
    violations = []
    data_paths: dict[str, list[tuple[str, str]]] = {}
    database_paths: dict[str, list[tuple[str, str]]] = {}
    for root in roots.values():
        config_path = f"{root}/module-config.json"
        if config_path not in paths:
            violations.append(ArchitectureViolation("MODULE_DATA_CONFIG_MISSING", root, "module-config.json is required"))
            continue
        try:
            config = json.loads(adapter.read_text(config_path))
        except (json.JSONDecodeError, KeyError) as exc:
            violations.append(ArchitectureViolation("MODULE_DATA_CONFIG_INVALID", config_path, str(exc)))
            continue
        for key in ("dataDirectory", "databasePath"):
            value = config.get(key)
            if not isinstance(value, str) or not value.strip():
                violations.append(ArchitectureViolation("MODULE_DATA_CONFIG_INVALID", config_path, f"{key} must be a non-empty path"))
                continue
            canonical = _canonical_path(value, root)
            if canonical is None or not _under_module(canonical, root.casefold()):
                violations.append(ArchitectureViolation("MODULE_DATA_CONFIG_CROSS_ROOT", config_path, f"{key} must stay inside {root}"))
            elif key == "dataDirectory":
                data_paths.setdefault(canonical, []).append((root, config_path))
            else:
                database_paths.setdefault(canonical, []).append((root, config_path))
    for canonical, uses in data_paths.items():
        if len({module for module, _ in uses}) > 1:
            violations.append(ArchitectureViolation("SHARED_DATA_DIRECTORY", uses[0][1], f"{canonical} is configured by multiple modules"))
    for canonical, uses in database_paths.items():
        if len({module for module, _ in uses}) > 1:
            violations.append(ArchitectureViolation("CROSS_MODULE_DATABASE_PATH", uses[0][1], f"{canonical} is configured by multiple modules"))
    return violations


def check_architecture(source: SourceAdapter | Path) -> tuple[ArchitectureViolation, ...]:
    """Return REST-only ownership violations through the source interface."""
    adapter = FilesystemSourceAdapter(source) if isinstance(source, Path) else source
    paths = tuple(sorted(PurePosixPath(path.replace("\\", "/")).as_posix() for path in adapter.files()))
    roots = _module_roots(paths)
    violations: list[ArchitectureViolation] = list(_config_violations(adapter, paths, roots))
    database_uses: dict[str, list[tuple[str, str]]] = {}
    runtime_json_uses: dict[str, list[tuple[str, str]]] = {}

    for path in paths:
        text = adapter.read_text(path)
        source_module = _module_for_path(path, roots)
        if source_module:
            if path.endswith(".py"):
                imports = _python_imports(path, text, roots)
            elif path.endswith((".js", ".mjs", ".cjs", ".ts", ".tsx")):
                imports = _node_imports(path, text, roots)
            else:
                imports = ()
            for target in imports:
                violations.append(
                    ArchitectureViolation("CROSS_MODULE_IMPORT", path, f"{source_module} imports {target}")
                )
            if path.endswith((".js", ".mjs", ".cjs", ".ts", ".tsx")) and re.search(
                r"\b(?:localStorage|sessionStorage|indexedDB|caches)\b", text
            ) and (_CLINICAL_WORDS.search(text) or _CLINICAL_WORDS.search(source_module)):
                violations.append(
                    ArchitectureViolation(
                        "CLINICAL_BROWSER_STORAGE",
                        path,
                        "browser storage cannot own clinical integration state",
                    )
                )
            reference_base = source_module if "__file__" in text else None
            for value, canonical in _path_references(path, text, reference_base):
                if re.search(r"\.(?:sqlite3?|db)$", value, re.IGNORECASE):
                    database_uses.setdefault(canonical, []).append((source_module, path))
                elif value.lower().endswith(".json") and re.search(
                    r"(?:runtime|state|active-kb)", value, re.IGNORECASE
                ):
                    runtime_json_uses.setdefault(canonical, []).append((source_module, path))

    for canonical, uses in database_uses.items():
        modules = {module for module, _ in uses}
        owner = next((root for root in roots.values() if _under_module(canonical, root.casefold())), None)
        if len(modules) > 1 or (owner and owner not in modules):
            violations.append(
                ArchitectureViolation(
                    "CROSS_MODULE_DATABASE_PATH",
                    uses[0][1],
                    f"{canonical} is referenced by {', '.join(sorted(modules))}",
                )
            )
    for canonical, uses in runtime_json_uses.items():
        modules = {module for module, _ in uses}
        owner = next((root for root in roots.values() if _under_module(canonical, root.casefold())), None)
        if len(modules) > 1 or (owner and owner not in modules):
            violations.append(
                ArchitectureViolation(
                    "SHARED_RUNTIME_JSON",
                    uses[0][1],
                    f"{canonical} is referenced by {', '.join(sorted(modules))}",
                )
            )

    return tuple(sorted(set(violations), key=lambda item: (item.code, item.source, item.detail)))


def run(root: Path = Path(__file__).parents[1]) -> tuple[ArchitectureViolation, ...]:
    violations = check_architecture(FilesystemSourceAdapter(root))
    if violations:
        for violation in violations:
            print(violation)
        print(f"ARCHITECTURE: INVALID ({len(violations)} violation(s))")
    else:
        print("ARCHITECTURE: VALID")
    return violations


if __name__ == "__main__":
    raise SystemExit(1 if run() else 0)
