from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from .model_governance import ClinicalStatus


MODEL_REGISTRY_DIR = Path(__file__).resolve().parent / "model_registry"
XML_SCHEMA_PATH = "schemas/XSD.xml"


@dataclass(frozen=True, slots=True)
class ModelRegistryEntry:
    stable_id: str
    title: str
    file_path: str
    target_node: str
    active_version: str
    status: str
    schema_path: str = XML_SCHEMA_PATH
    clinical_status: ClinicalStatus = ClinicalStatus.UNVALIDATED
    limitations: tuple[str, ...] = ()

    def payload(self) -> dict[str, str | list[str]]:
        payload = asdict(self)
        payload["clinical_status"] = self.clinical_status.value
        payload["limitations"] = list(self.limitations)
        return payload


# BN-04: shipped networks ship as UNVALIDATED. Clinical approval is an
# explicit governance action through the admin REST seam; the registry
# never pre-fabricates approvals, identifiers, or clinical thresholds.
_COMPACT_BROADCAST_LIMITATIONS = ("compact-neutral-cpt-broadcast",)


MODEL_REGISTRY: tuple[ModelRegistryEntry, ...] = (
    ModelRegistryEntry(
        stable_id="bnm.pharmacotherapy",
        title="Pharmacotherapy",
        file_path="xml/BN-Pharmacotherapy.xml",
        target_node="management_recommendation",
        active_version="1.0.0",
        status="active",
    ),
    ModelRegistryEntry(
        stable_id="bnm.treatment-setting",
        title="Treatment Setting",
        file_path="xml/BN-Treatment-Setting.xml",
        target_node="management_recommendation",
        active_version="1.0.0",
        status="active",
        limitations=_COMPACT_BROADCAST_LIMITATIONS,
    ),
    ModelRegistryEntry(
        stable_id="bnm.involuntary-treatment-considerations",
        title="Involuntary Treatment Considerations",
        file_path="xml/BN-Involuntary-Treatment-Considerations.xml",
        target_node="management_recommendation",
        active_version="1.0.0",
        status="active",
        limitations=_COMPACT_BROADCAST_LIMITATIONS,
    ),
    ModelRegistryEntry(
        stable_id="bnm.clozapine-suicide-risk",
        title="Clozapine in Suicide Risk",
        file_path="xml/BN-Clozapine-in-Suicide-Risk.xml",
        target_node="Clinical_Action_Pattern",
        active_version="1.0.0",
        status="active",
    ),
)


def list_registry_entries() -> list[dict[str, str]]:
    resolve_owned_registry_file(XML_SCHEMA_PATH)
    for entry in MODEL_REGISTRY:
        resolve_owned_registry_file(entry.file_path)
    return [entry.payload() for entry in MODEL_REGISTRY]


def get_registry_entry(stable_id: str) -> ModelRegistryEntry | None:
    return next((entry for entry in MODEL_REGISTRY if entry.stable_id == stable_id), None)


def read_registry_model(stable_id: str) -> tuple[ModelRegistryEntry, str]:
    entry = get_registry_entry(stable_id)
    if entry is None:
        raise KeyError(stable_id)
    return entry, read_owned_registry_file(entry.file_path)


def read_registry_schema() -> str:
    return read_owned_registry_file(XML_SCHEMA_PATH)


def read_owned_registry_file(relative_path: str) -> str:
    path = resolve_owned_registry_file(relative_path)
    return path.read_text(encoding="utf-8")


def resolve_owned_registry_file(relative_path: str) -> Path:
    requested = Path(relative_path)
    if requested.is_absolute():
        raise ValueError("Registry file path must be relative.")

    base = MODEL_REGISTRY_DIR.resolve()
    path = (base / requested).resolve()
    if base not in (path, *path.parents) or not path.is_file():
        raise ValueError("Registry file path escapes BN Manager model registry.")
    return path
