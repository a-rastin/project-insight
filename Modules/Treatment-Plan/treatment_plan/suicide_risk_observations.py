"""MH-04: source/time-stamped suicide-risk observations and an approved
resolution policy.

Add New Patient and Medical History each persist a suicide-risk value under
their own ownership. Treatment Plan consumes those values as separate
observations carrying source, timestamp, and source version, and runs one
deterministic resolution policy that routes disagreements to the explicit
safety review pathway so that neither module silently wins.

The observations preserve each source's own vocabulary verbatim; this module
does not translate ANP's clinician suicidality states into MH's "substantial
risk" boolean or invent clinical thresholds. The approved policy compares
normalized tokens: sources that report *different* tokens are treated as
contradictions requiring explicit review.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence

from .clinical_context import Dependency
from .eligibility import Blocker


NO_OBSERVATION = "__no_observation__"


_ANP_DEFAULT = "suicidality_none"
_MH_DEFAULT_FALSE = False


class _Source(str, Enum):
    ADD_NEW_PATIENT = "add-new-patient"
    MEDICAL_HISTORY = "medical-history"


@dataclass(frozen=True)
class SuicideRiskObservation:
    """One source/time-stamped suicide-risk observation.

    ``value`` is preserved verbatim from the source module; normalization to
    a comparison token happens lazily in ``normalized`` so the raw evidence is
    always available for the rule trace and the audit record. Sources own
    their own vocabularies; this module never rewrites them.
    """

    source: Dependency
    value: object
    observed_at: str | None
    source_version: str | None

    @property
    def normalized(self) -> str:
        """A comparison token that preserves each source's own vocabulary.

        ANP's ``suicidality_none`` and MH's ``False`` both map to ``"none"``;
        every non-default token is preserved as its lower-case string form so a
        disagreement between e.g. ANP ``ideation`` and MH ``True`` is a visible
        contradiction rather than a hidden defaulting.
        """
        if self.value is None:
            return NO_OBSERVATION
        if self.source is Dependency.PATIENT:
            text = str(self.value).strip().casefold()
            return "none" if text == _ANP_DEFAULT else text or NO_OBSERVATION
        if self.source is Dependency.MEDICAL_HISTORY:
            if isinstance(self.value, bool):
                return "none" if self.value is _MH_DEFAULT_FALSE else "substantial"
            text = str(self.value).strip().casefold()
            if text in {"", "false", "no", "0"}:
                return "none"
            if text in {"true", "yes", "1"}:
                return "substantial"
            return text
        text = str(self.value).strip().casefold()
        return text or NO_OBSERVATION

    @property
    def is_signal(self) -> bool:
        return self.normalized not in {NO_OBSERVATION, "none"}


class Resolution(str, Enum):
    AGREE = "agree"
    CONTRADICT = "contradict"
    SOLE_SOURCE = "sole-source"
    NO_OBSERVATION = "no-observation"


@dataclass(frozen=True)
class ResolvedSuicideRisk:
    resolution: Resolution
    resolved_value: str | None
    finding_code: str | None
    blocker: Blocker | None
    observations: tuple[SuicideRiskObservation, ...]
    evidence: tuple[str, ...]


class SuicideRiskResolution:
    """The approved resolution policy for two source/time-stamped observations.

    Deterministic and pure. Approved rules (no fabricated clinical thresholds):

    * no observations         → ``NO_OBSERVATION`` (no finding).
    * one observation saying ``none``                → ``AGREE`` (no finding).
    * one observation that signals risk             → ``SOLE_SOURCE`` safety review.
    * multiple observations with the same normalized token and that token is a
      signal                                       → ``AGREE`` on that signal but the
      pathway still routes to safety review because both sources corroborate risk.
    * multiple observations with the same ``none`` token → ``AGREE`` (no finding).
    * multiple observations with different normalized tokens → ``CONTRADICT``:
      the policy refuses to pick a winner and routes to explicit safety review.
    """

    def resolve(
        self, observations: Sequence[SuicideRiskObservation]
    ) -> ResolvedSuicideRisk:
        present = tuple(obs for obs in observations if obs is not None)
        if not present:
            return ResolvedSuicideRisk(
                Resolution.NO_OBSERVATION, None, None, None, (), ()
            )
        evidence = tuple(
            f"{obs.source.value}@{obs.observed_at}: {obs.value!r}"
            for obs in present
        )
        tokens = tuple(obs.normalized for obs in present)
        distinct = set(tokens)
        if len(present) == 1:
            sole = present[0]
            if not sole.is_signal:
                return ResolvedSuicideRisk(
                    Resolution.AGREE, "none", None, None, present, evidence
                )
            return ResolvedSuicideRisk(
                Resolution.SOLE_SOURCE,
                sole.normalized,
                "suicide-risk-sole-source",
                Blocker.SAFETY,
                present,
                evidence,
            )
        if len(distinct) == 1:
            token = next(iter(distinct))
            if token in {NO_OBSERVATION, "none"}:
                return ResolvedSuicideRisk(
                    Resolution.AGREE, "none", None, None, present, evidence
                )
            return ResolvedSuicideRisk(
                Resolution.AGREE,
                token,
                "suicide-risk-agreed-signal",
                Blocker.SAFETY,
                present,
                evidence,
            )
        return ResolvedSuicideRisk(
            Resolution.CONTRADICT,
            None,
            "suicide-risk-contradiction",
            Blocker.SAFETY,
            present,
            evidence,
        )

    def resolve_from_context(self, inputs: Mapping[Dependency, Mapping]) -> ResolvedSuicideRisk:
        """Build observations for ANP and MH from an assembled clinical context.

        Only the two owning modules for suicide-risk observations are sampled.
        ``observed_at`` and ``source_version`` come from the persisted snapshot's
        envelope so the observations remain source/time-stamped; a missing
        envelope value is preserved as ``None`` rather than fabricated.
        """
        observations: list[SuicideRiskObservation] = []
        patient = inputs.get(Dependency.PATIENT)
        if patient is not None:
            risk_flags = patient.get("riskFlags") if isinstance(patient, Mapping) else None
            suicidality = None
            if isinstance(risk_flags, Mapping):
                suicidality = risk_flags.get("suicidality")
            if suicidality is not None:
                observations.append(
                    SuicideRiskObservation(
                        Dependency.PATIENT,
                        suicidality,
                        patient.get("observedAt"),
                        patient.get("schemaVersion"),
                    )
                )
        medical_history = inputs.get(Dependency.MEDICAL_HISTORY)
        if medical_history is not None:
            substantial = medical_history.get("substantialSuicideRisk") if isinstance(
                medical_history, Mapping
            ) else None
            if substantial is not None:
                observations.append(
                    SuicideRiskObservation(
                        Dependency.MEDICAL_HISTORY,
                        substantial,
                        medical_history.get("observedAt"),
                        medical_history.get("schemaVersion"),
                    )
                )
        return self.resolve(observations)


def extract_observations(inputs: Mapping[Dependency, Mapping]) -> tuple[SuicideRiskObservation, ...]:
    return SuicideRiskResolution().resolve_from_context(inputs).observations
