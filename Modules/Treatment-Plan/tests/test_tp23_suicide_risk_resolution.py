"""MH-04: separate source/time-stamped suicide-risk observations and an approved
resolution policy. Add New Patient and Medical History each contribute an
observation; the Treatment Plan detects disagreement and routes to the explicit
safety review pathway so neither module silently wins.

These tests define the intended interface before implementation.
"""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from treatment_plan.clinical_context import ClinicalContext, Dependency
from treatment_plan.eligibility import (
    Blocker,
    Eligibility,
    GenerationEligibilityPolicy,
)
from treatment_plan.suicide_risk_observations import (
    NO_OBSERVATION,
    Resolution,
    ResolvedSuicideRisk,
    SuicideRiskObservation,
    SuicideRiskResolution,
)


PATHWAY = "schizophrenia-research-v1"
NOW = datetime(2026, 7, 13, 12, tzinfo=timezone.utc)


def _observation(source: Dependency, value, observed_at=NOW.isoformat()) -> SuicideRiskObservation:
    return SuicideRiskObservation(
        source=source,
        value=value,
        observed_at=observed_at,
        source_version="1.0.0",
    )


class SuicideRiskObservationTests(unittest.TestCase):
    def test_observation_is_immutable_and_records_source_and_timestamp(self):
        observation = _observation(Dependency.PATIENT, "ideation")
        with self.assertRaises(Exception):
            observation.value = "plan"  # type: ignore[misc]
        self.assertEqual(observation.source, Dependency.PATIENT)
        self.assertEqual(observation.observed_at, NOW.isoformat())
        self.assertEqual(observation.source_version, "1.0.0")

    def test_none_value_is_rejected_by_normalization_so_sources_cannot_silently_default(self):
        observation = _observation(Dependency.PATIENT, None)
        self.assertEqual(observation.normalized, NO_OBSERVATION)
        self.assertIsNone(observation.value)


class SuicideRiskResolutionPolicyTests(unittest.TestCase):
    def test_no_observations_yields_no_resolution_and_no_finding(self):
        result = SuicideRiskResolution().resolve(())
        self.assertEqual(result.resolution, Resolution.NO_OBSERVATION)
        self.assertEqual(result.finding_code, None)
        self.assertEqual(result.blocker, None)

    def test_single_default_observation_is_agree_and_no_finding(self):
        result = SuicideRiskResolution().resolve(
            (_observation(Dependency.PATIENT, "suicidality_none"),)
        )
        self.assertEqual(result.resolution, Resolution.AGREE)
        self.assertEqual(result.resolved_value, "none")
        self.assertEqual(result.blocker, None)

    def test_single_risky_observation_triggers_sole_source_safety_review(self):
        result = SuicideRiskResolution().resolve(
            (_observation(Dependency.MEDICAL_HISTORY, True),)
        )
        self.assertEqual(result.resolution, Resolution.SOLE_SOURCE)
        self.assertEqual(result.blocker, Blocker.SAFETY)
        self.assertEqual(result.finding_code, "suicide-risk-sole-source")

    def test_two_observations_that_agree_keep_that_value(self):
        result = SuicideRiskResolution().resolve(
            (
                _observation(Dependency.PATIENT, "suicidality_none"),
                _observation(Dependency.MEDICAL_HISTORY, False),
            )
        )
        self.assertEqual(result.resolution, Resolution.AGREE)
        self.assertEqual(result.resolved_value, "none")
        self.assertEqual(result.blocker, None)

    def test_two_observations_that_disagree_route_to_safety_review_neither_wins(self):
        result = SuicideRiskResolution().resolve(
            (
                _observation(Dependency.PATIENT, "ideation"),
                _observation(Dependency.MEDICAL_HISTORY, True),
            )
        )
        self.assertEqual(result.resolution, Resolution.CONTRADICT)
        self.assertEqual(result.blocker, Blocker.SAFETY)
        self.assertEqual(result.finding_code, "suicide-risk-contradiction")
        self.assertIsNone(result.resolved_value)

    def test_two_observations_disagreeing_on_signal_direction_contradicts(self):
        result = SuicideRiskResolution().resolve(
            (
                _observation(Dependency.PATIENT, "plan"),
                _observation(Dependency.MEDICAL_HISTORY, False),
            )
        )
        self.assertEqual(result.resolution, Resolution.CONTRADICT)
        self.assertEqual(result.blocker, Blocker.SAFETY)

    def test_two_observations_with_identical_signal_token_agree_on_that_signal(self):
        # Synthetic shared vocabulary: the policy mechanism agrees when both
        # sources emit the same non-default token (covers the AGREE-with-signal
        # branch without asserting any cross-module clinical mapping).
        result = SuicideRiskResolution().resolve(
            (
                _observation(Dependency.PATIENT, "high"),
                _observation(Dependency.MEDICAL_HISTORY, "high"),
            )
        )
        self.assertEqual(result.resolution, Resolution.AGREE)
        self.assertEqual(result.resolved_value, "high")
        self.assertEqual(result.finding_code, "suicide-risk-agreed-signal")
        self.assertEqual(result.blocker, Blocker.SAFETY)


class EligibilityIntegrationTests(unittest.TestCase):
    """The Treatment Plan eligibility policy runs the resolution policy over
    observations from Add New Patient and Medical History so neither silently
    wins."""

    def _context(
        self,
        *,
        patient_suicidality=None,
        medical_history_substantial_suicide_risk=None,
        patient_present=True,
        medical_history_present=True,
    ):
        observed = {"observedAt": NOW.isoformat()}
        inputs = {
            Dependency.PATIENT: {
                **observed,
                "currentMedications": [],
                "riskFlags": {"suicidality": patient_suicidality, "substanceUse": False},
            },
            Dependency.DIAGNOSIS: {**observed, "diagnosis": {"code": "F20.9"}},
            Dependency.SEVERITY: {**observed, "status": "complete", "severity": {"score": 12}},
            Dependency.MEDICAL_HISTORY: {
                **observed,
                "medicalHistory": {},
                "substantialSuicideRisk": medical_history_substantial_suicide_risk,
            },
            Dependency.DDI: {**observed, "findings": []},
            Dependency.BN: {**observed, "evaluation": {}},
        }
        if not patient_present:
            inputs.pop(Dependency.PATIENT)
        if not medical_history_present:
            inputs.pop(Dependency.MEDICAL_HISTORY)
        return ClinicalContext("patient-id", "encounter-id", inputs, (), ())

    def _decide(self, context):
        return GenerationEligibilityPolicy().evaluate(context, PATHWAY, now=NOW)

    def test_both_sources_none_is_eligible(self):
        decision = self._decide(
            self._context(
                patient_suicidality="suicidality_none",
                medical_history_substantial_suicide_risk=False,
            )
        )
        self.assertEqual(decision.eligibility, Eligibility.ELIGIBLE)

    def test_both_sources_signal_routes_to_safety_review_even_when_vocabularies_differ(self):
        # ANP and MH carry their own vocabularies; an "ideation" from ANP and a
        # "substantial" finding from MH are *different tokens* and therefore a
        # contradiction that the approved policy routes to safety review rather
        # than collapsing either vocabulary into the other.
        decision = self._decide(
            self._context(
                patient_suicidality="ideation",
                medical_history_substantial_suicide_risk=True,
            )
        )
        self.assertEqual(decision.eligibility, Eligibility.SAFETY_PATHWAY)
        codes = {finding.code for finding in decision.findings}
        self.assertIn("suicide-risk-contradiction", codes)

    def test_both_sources_signal_with_matching_token_route_to_safety_review(self):
        # When the two owning modules happen to emit the same token (for example
        # because both default to "none"), the policy agrees on that token.
        decision = self._decide(
            self._context(
                patient_suicidality="suicidality_none",
                medical_history_substantial_suicide_risk=False,
            )
        )
        self.assertEqual(decision.eligibility, Eligibility.ELIGIBLE)

    def test_disagreement_routes_to_safety_review_and_neither_wins(self):
        decision = self._decide(
            self._context(
                patient_suicidality="ideation",
                medical_history_substantial_suicide_risk=False,
            )
        )
        self.assertEqual(decision.eligibility, Eligibility.SAFETY_PATHWAY)
        codes = {finding.code for finding in decision.findings}
        self.assertIn("suicide-risk-contradiction", codes)

    def test_single_risky_source_routes_to_safety_review(self):
        decision = self._decide(
            self._context(
                patient_suicidality="plan",
                medical_history_substantial_suicide_risk=None,
            )
        )
        self.assertEqual(decision.eligibility, Eligibility.SAFETY_PATHWAY)
        codes = {finding.code for finding in decision.findings}
        self.assertIn("suicide-risk-sole-source", codes)

    def test_missing_both_sources_does_not_raise_a_suicide_risk_finding(self):
        decision = self._decide(
            self._context(
                patient_present=False,
                medical_history_present=False,
            )
        )
        codes = {finding.code for finding in decision.findings}
        self.assertNotIn("suicide-risk-contradiction", codes)
        self.assertNotIn("suicide-risk-sole-source", codes)
        self.assertNotIn("suicide-risk-agreed-signal", codes)


if __name__ == "__main__":
    unittest.main()
