import asyncio
import json
import unittest
from pathlib import Path

import httpx

from treatment_plan.bn_evaluation import (
    BnEvaluationOrchestrator, BnFindingCode, BnManagerHttpEvaluator, BnModel,
    InMemoryBnEvaluationStore, MAPPING_VERSION, NormalizedSnapshotFacts, RawBnEvaluation,
)
from treatment_plan.bn_store import RepositoryBnEvaluationStore
from treatment_plan.repository import InMemoryRepository

FIXTURE = Path(__file__).with_name("fixtures") / "tp10_bn_golden.json"
MODEL_HASHES = {model: "sha256:" + format(index, "064x") for index, model in enumerate(BnModel, 1)}


class FakeEvaluator:
    def __init__(self): self.requests = []
    async def evaluate(self, model, evidence, mapping_version):
        self.requests.append((model, dict(evidence), mapping_version)); await asyncio.sleep(0)
        return RawBnEvaluation(f"evaluation-{model.value}", model.value, "2026.07.1",
                               MODEL_HASHES[model], {"candidate-a": .7, "candidate-b": .3},
                               "2026-07-14T12:00:00Z")


class TP10BnEvaluationTests(unittest.IsolatedAsyncioTestCase):
    async def test_synthetic_golden_candidate_maps_and_stores_all_models(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8")); evaluator = FakeEvaluator(); store = InMemoryBnEvaluationStore()
        bundle = await BnEvaluationOrchestrator(evaluator, store).evaluate(NormalizedSnapshotFacts.from_mapping(fixture["snapshotFacts"]))
        actual = {model.value: evidence for model, evidence, _ in evaluator.requests}
        self.assertEqual(actual, fixture["expectedEvidence"])
        self.assertEqual({version for _, _, version in evaluator.requests}, {MAPPING_VERSION})
        self.assertTrue(bundle.complete); self.assertEqual(len(bundle.evaluations), 4)
        self.assertEqual({item.model_hash for item in bundle.evaluations}, set(MODEL_HASHES.values()))
        self.assertEqual(store.get(bundle.snapshot_id), bundle); self.assertTrue(bundle.content_hash.startswith("sha256:"))
        self.assertTrue(all(item.ratio == 1 for item in bundle.coverage))

    async def test_unsupported_state_is_typed_and_never_reaches_evaluator(self):
        evaluator = FakeEvaluator(); facts = NormalizedSnapshotFacts("snapshot-unsupported", symptom_severity="not-assessed", suicide_risk="HIGH")
        bundle = await BnEvaluationOrchestrator(evaluator, InMemoryBnEvaluationStore()).evaluate(facts)
        requests = {model: evidence for model, evidence, _ in evaluator.requests}
        self.assertNotIn("SymptomSeverity", requests[BnModel.TREATMENT_SETTING]); self.assertEqual(requests[BnModel.TREATMENT_SETTING]["SuicideRisk"], "High")
        finding = next(item for item in bundle.findings if item.fact == "symptom_severity")
        self.assertEqual(finding.code, BnFindingCode.UNSUPPORTED_EVIDENCE_STATE)
        setting = next(item for item in bundle.coverage if item.model is BnModel.TREATMENT_SETTING)
        self.assertEqual(setting.unsupported_facts, ("symptom_severity",)); self.assertFalse(bundle.complete)

    async def test_invalid_model_identity_and_distribution_are_typed(self):
        class InvalidEvaluator(FakeEvaluator):
            async def evaluate(self, model, evidence, mapping_version):
                result = await super().evaluate(model, evidence, mapping_version)
                return RawBnEvaluation("bad", model.value, "", "not-a-hash", {"x": .4}) if model is BnModel.PHARMACOTHERAPY else result
        bundle = await BnEvaluationOrchestrator(InvalidEvaluator(), InMemoryBnEvaluationStore()).evaluate(NormalizedSnapshotFacts("snapshot-invalid"))
        invalid = [item for item in bundle.findings if item.code is BnFindingCode.INVALID_MODEL_RESPONSE]
        self.assertEqual([item.model for item in invalid], [BnModel.PHARMACOTHERAPY])
        self.assertNotIn(BnModel.PHARMACOTHERAPY, {item.model for item in bundle.evaluations})

    async def test_repository_adapter_persists_versions_hashes_and_posteriors(self):
        repository = InMemoryRepository(); repository.migrate()
        bundle = await BnEvaluationOrchestrator(FakeEvaluator(), RepositoryBnEvaluationStore(repository)).evaluate(NormalizedSnapshotFacts("snapshot-repository", suicide_risk="low"))
        stored = repository.get("bn-evaluation:snapshot-repository"); self.assertIsNotNone(stored)
        payload = json.loads(stored.value); self.assertEqual(payload["contentHash"], bundle.content_hash)
        self.assertEqual(len(payload["bundle"]["evaluations"]), 4)
        self.assertIn("posterior", payload["bundle"]["evaluations"][0]); self.assertIn("model_hash", payload["bundle"]["evaluations"][0])

    async def test_http_adapter_sends_only_mapped_evidence_and_reads_exact_identity(self):
        seen = {}
        def handler(request):
            seen.update(json.loads(request.content))
            return httpx.Response(200, json={"evaluationId":"remote-1","modelId":"treatment-setting","modelVersion":"7.4.2","modelHash":"sha256:"+"a"*64,"posterior":{"outpatient":1.0},"evaluatedAt":"2026-07-14T12:00:00Z"})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await BnManagerHttpEvaluator("https://bn.internal", client).evaluate(BnModel.TREATMENT_SETTING, {"SuicideRisk":"Low"}, MAPPING_VERSION)
        self.assertEqual(seen["evidence"], {"SuicideRisk":"Low"}); self.assertEqual(seen["evidenceVocabularyVersion"], MAPPING_VERSION)
        self.assertEqual(result.model_version, "7.4.2"); self.assertEqual(result.model_hash, "sha256:"+"a"*64)


if __name__ == "__main__": unittest.main()
