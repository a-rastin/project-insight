"""BN-05 — Treatment Plan caller policy.

Asserts the caller-aware BN Manager adapter forwards the psychiatrist session
(cookie + csrf) and uses the canonical request body shape against the owned
`/api/bn-manager/v1/treatment-plan/evaluate` route. Per-model evidence schema
mapping tests read the live BN Manager registry and confirm the captured fixture
matches the committed BN-04 evidence vocabulary exactly.

Rule-8 boundary: the orchestrator's `_MODEL_RULES` / `NormalizedSnapshotFacts`
are intentionally left untouched. The caller surface routes the BN Manager
node-id evidence dict directly through a per-request caller-aware adapter and
returns a thin bundle of the four raw evaluations.
"""
import json
import sys
import unittest
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from treatment_plan.app import create_app
from treatment_plan.bn_caller_policy import (
    BnManagerTreatmentPlanEvaluator,
    Caller,
)
from treatment_plan.bn_evaluation import BnModel, MAPPING_VERSION, RawBnEvaluation
from treatment_plan.config import Settings
from treatment_plan.repository import InMemoryRepository
from treatment_plan.security import (
    AccessDenied,
    Capability,
    InMemoryAuthenticationAdapter,
    Security,
    Session,
)
from datetime import datetime, timedelta, timezone

FIXTURE = Path(__file__).with_name("fixtures") / "bn05_registry_evidence_mapping.json"
NOW = datetime(2026, 7, 23, tzinfo=timezone.utc)

BN_MANAGER_ROOT = (
    Path(__file__).parents[2]
    / "BN-Manager-v.1.1.0"
    / "BN-Manager-v.1.1.0"
)


def bn_manager_client_factory():
    sys.path.insert(0, str(BN_MANAGER_ROOT))
    try:
        from bn_manager_backend.auth_adapter import session_from_payload
        from bn_manager_backend.evaluation_store import InMemoryEvaluationStore
        from bn_manager_backend.main import create_app as bn_create_app
    except ImportError as exc:
        raise unittest.SkipTest(
            "BN Manager module or its native dependencies (lxml) are not "
            "importable in this interpreter; run the schema-mapping tests "
            "against the BN Manager venv."
        ) from exc

    class FakeAdapter:
        def __init__(self, session):
            self.session = session

        def fetch_session(self, request):
            return self.session

    payload = {
        "schemaVersion": "1.0.0",
        "authenticated": True,
        "user": {"id": "psy-1", "roles": ["psychiatrist"]},
        "session": {"id": "session-1", "expiresAt": "2099-01-01T00:00:00Z"},
        "gates": {"disclaimerAccepted": True, "passwordChangeRequired": False},
    }
    return TestClient(
        bn_create_app(
            session_adapter=FakeAdapter(session_from_payload(payload)),
            evaluation_store=InMemoryEvaluationStore(),
        )
    )


class CallerAdapterContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_sends_cookie_csrf_and_canonical_body(self):
        seen = {}

        def handler(request: httpx.Request):
            seen["url"] = str(request.url)
            seen["headers"] = {key: value for key, value in request.headers.items()}
            seen["body"] = json.loads(request.content)
            response = {
                "ok": True,
                "data": {
                    "surface": "Treatment Plan",
                    "evaluation": {
                        "evaluationId": "eval-1",
                        "modelId": "bnm.clozapine-suicide-risk",
                        "modelVersion": "1.0.0",
                        "modelHash": "sha256:" + "a" * 64,
                        "posterior": {"Initiate_Clozapine": 1.0},
                        "evaluatedAt": "2026-07-23T11:00:00Z",
                    },
                    "values": {"Initiate_Clozapine": 1.0},
                    "rankings": [{"state": "Initiate_Clozapine", "probability": 1.0}],
                    "evaluated_by": "psy-1",
                    "warnings": [],
                },
                "meta": {},
            }
            return httpx.Response(200, json=response)

        caller = Caller(
            subject="psy-1",
            roles=frozenset({"psychiatrist"}),
            csrf_token="csrf-1",
            cookie="csrf_token=csrf-1",
        )
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            evaluator = BnManagerTreatmentPlanEvaluator(
                base_url="https://bn.internal",
                client=client,
                caller=caller,
            )
            result = await evaluator.evaluate(
                BnModel.CLOZAPINE_SUICIDE_RISK,
                {"Schizophrenia_Suicide_Indication": "Met"},
                MAPPING_VERSION,
            )

        self.assertEqual(seen["url"], "https://bn.internal/api/bn-manager/v1/treatment-plan/evaluate")
        self.assertEqual(seen["headers"]["cookie"], "csrf_token=csrf-1")
        self.assertEqual(seen["headers"]["x-csrf-token"], "csrf-1")
        self.assertEqual(seen["headers"]["accept"], "application/json")
        self.assertEqual(seen["headers"]["content-type"], "application/json")
        self.assertEqual(
            seen["body"],
            {
                "model": {"model_id": "bnm.clozapine-suicide-risk"},
                "evidence": {"Schizophrenia_Suicide_Indication": "Met"},
            },
        )
        self.assertIsInstance(result, RawBnEvaluation)
        self.assertEqual(result.evaluation_id, "eval-1")
        self.assertEqual(result.model_id, "bnm.clozapine-suicide-risk")
        self.assertEqual(result.model_version, "1.0.0")
        self.assertEqual(result.model_hash, "sha256:" + "a" * 64)
        self.assertEqual(result.posterior, {"Initiate_Clozapine": 1.0})
        self.assertEqual(result.evaluated_at, "2026-07-23T11:00:00Z")

    async def test_raises_on_non_2xx_response(self):
        def handler(request: httpx.Request):
            return httpx.Response(
                503,
                json={"ok": False, "error": {"code": "BNM_UNAVAILABLE"}, "meta": {}},
            )

        caller = Caller(subject="psy-1", roles=frozenset({"psychiatrist"}),
                        csrf_token="csrf-1", cookie="csrf_token=csrf-1")
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            evaluator = BnManagerTreatmentPlanEvaluator(
                base_url="https://bn.internal", client=client, caller=caller,
            )
            with self.assertRaises(httpx.HTTPStatusError):
                await evaluator.evaluate(
                    BnModel.PHARMACOTHERAPY, {}, MAPPING_VERSION
                )

    async def test_missing_cookie_or_csrf_is_rejected_at_construction(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={}))) as client:
            for kwargs in ({"cookie": "", "csrf_token": "x"}, {"cookie": "c", "csrf_token": ""}):
                with self.assertRaises(ValueError):
                    BnManagerTreatmentPlanEvaluator(
                        base_url="https://bn.internal", client=client,
                        caller=Caller(subject="u", roles=frozenset(), **kwargs),
                    )


class RegistryEvidenceSchemaMappingTests(unittest.TestCase):
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def setUp(self):
        self.client = bn_manager_client_factory()

    def test_fixture_matches_live_registry_for_all_four_models(self):
        for stable_id, expected in self.fixture.items():
            with self.subTest(model=stable_id):
                response = self.client.get(f"/api/bn-manager/v1/models/{stable_id}/schema")
                self.assertEqual(response.status_code, 200)
                data = response.json()["data"]

                self.assertEqual(data["stable_id"], stable_id)
                self.assertEqual(data["model_version"], expected["model_version"])
                self.assertEqual(data["model_hash"], expected["model_hash"])
                self.assertEqual(data["title"], expected["title"])

                self.assertEqual(data["target"]["node_id"], expected["target"])
                self.assertEqual(
                    sorted(data["target"]["states"]),
                    sorted(expected["target_states"]),
                )

                live_allowed = {
                    node["node_id"]: list(node["states"])
                    for node in data["allowed_evidence"]
                }
                self.assertEqual(
                    sorted(live_allowed),
                    sorted(expected["allowed_evidence"].keys()),
                )
                for node_id, states in expected["allowed_evidence"].items():
                    self.assertEqual(
                        sorted(live_allowed[node_id]),
                        sorted(states),
                        msg=f"state mismatch for {stable_id}.{node_id}",
                    )

                self.assertEqual(data["required_evidence"], expected["required_evidence"])
                self.assertEqual(
                    sorted(data["optional_evidence"]),
                    sorted(expected["optional_evidence"]),
                )
                self.assertEqual(
                    sorted(data["limitations"]),
                    sorted(expected["limitations"]),
                )

    def test_fixture_models_are_the_four_bn_model_stable_ids(self):
        expected = {
            "bnm." + model.value for model in BnModel
        }
        self.assertEqual(set(self.fixture.keys()), expected)


class CapabilityAndRouteTests(unittest.TestCase):
    def _security(self, session):
        adapter = InMemoryAuthenticationAdapter({"sid=trusted": session})
        return Security(adapter, now=lambda: NOW)

    def _session(self, roles=("psychiatrist",)):
        return Session(
            "user-1",
            frozenset(roles),
            NOW + timedelta(hours=1),
            "csrf-secret",
            session_id="dev-session",
        )

    def test_bn_evaluate_capability_requires_psychiatrist_and_csrf(self):
        security = self._security(self._session(("admin",)))
        with self.assertRaises(AccessDenied):
            security.authorize("sid=trusted", Capability.BN_EVALUATE, "csrf-secret")
        security = self._security(self._session(("psychiatrist",)))
        for token in (None, "wrong"):
            with self.assertRaisesRegex(AccessDenied, "CSRF"):
                security.authorize("sid=trusted", Capability.BN_EVALUATE, token)
        self.assertEqual(
            "user-1",
            security.authorize("sid=trusted", Capability.BN_EVALUATE, "csrf-secret").user_id,
        )

    def test_route_rejects_missing_csrf_or_non_psychiatrist(self):
        settings = Settings(environment="test")
        security = self._security(self._session(("admin",)))
        app = create_app(settings, InMemoryRepository(), security)
        with TestClient(app) as client:
            response = client.post("/api/treatment-plan/v1/bn-evaluate", json={})
            self.assertEqual(response.status_code, 401)

    def test_route_calls_bn_manager_through_caller_aware_adapter(self):
        settings = Settings(environment="test", bn_manager_url="http://bn.internal")
        security = self._security(self._session(("psychiatrist",)))
        app = create_app(settings, InMemoryRepository(), security)
        captured = {}

        def handler(request: httpx.Request):
            captured["headers"] = {k: v for k, v in request.headers.items()}
            captured["body"] = json.loads(request.content)
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "data": {
                        "surface": "Treatment Plan",
                        "evaluation": {
                            "evaluationId": "eval-tp-1",
                            "modelId": "bnm.clozapine-suicide-risk",
                            "modelVersion": "1.0.0",
                            "modelHash": "sha256:" + "b" * 64,
                            "posterior": {"Initiate_Clozapine": 0.7, "Optimize_Current_Therapy": 0.3},
                            "evaluatedAt": "2026-07-23T12:00:00Z",
                        },
                        "values": {"Initiate_Clozapine": 0.7, "Optimize_Current_Therapy": 0.3},
                        "rankings": [],
                        "evaluated_by": "user-1",
                        "warnings": [],
                    },
                    "meta": {},
                },
            )

        import httpx as _httpx

        original = getattr(app.state, "bn_manager_client", None)
        client = _httpx.AsyncClient(transport=_httpx.MockTransport(handler))
        app.state.bn_manager_client = client
        try:
            with TestClient(app) as api:
                response = api.post(
                    "/api/treatment-plan/v1/bn-evaluate",
                    json={
                        "model_id": "bnm.clozapine-suicide-risk",
                        "evidence": {"Schizophrenia_Suicide_Indication": "Met"},
                    },
                    headers={"Cookie": "sid=trusted", "X-CSRF-Token": "csrf-secret"},
                )
        finally:
            if original is None:
                del app.state.bn_manager_client
            else:
                app.state.bn_manager_client = original

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["surface"], "Treatment Plan")
        self.assertEqual(len(body["evaluations"]), 1)
        evaluation = body["evaluations"][0]
        self.assertEqual(evaluation["model_id"], "bnm.clozapine-suicide-risk")
        self.assertEqual(evaluation["model_version"], "1.0.0")
        self.assertEqual(evaluation["model_hash"], "sha256:" + "b" * 64)
        self.assertEqual(evaluation["evaluation_id"], "eval-tp-1")
        self.assertEqual(
            captured["body"],
            {
                "model": {"model_id": "bnm.clozapine-suicide-risk"},
                "evidence": {"Schizophrenia_Suicide_Indication": "Met"},
            },
        )
        self.assertEqual(captured["headers"]["cookie"], "sid=trusted")
        self.assertEqual(captured["headers"]["x-csrf-token"], "csrf-secret")

    def test_route_rejects_unknown_body_fields(self):
        settings = Settings(environment="test", bn_manager_url="http://bn.internal")
        security = self._security(self._session(("psychiatrist",)))
        app = create_app(settings, InMemoryRepository(), security)
        with TestClient(app) as client:
            response = client.post(
                "/api/treatment-plan/v1/bn-evaluate",
                json={"model_id": "bnm.clozapine-suicide-risk", "rogue": "value"},
                headers={"Cookie": "sid=trusted", "X-CSRF-Token": "csrf-secret"},
            )
        self.assertEqual(response.status_code, 422)

    def test_route_requires_evidence_field(self):
        settings = Settings(environment="test", bn_manager_url="http://bn.internal")
        security = self._security(self._session(("psychiatrist",)))
        app = create_app(settings, InMemoryRepository(), security)
        with TestClient(app) as client:
            response = client.post(
                "/api/treatment-plan/v1/bn-evaluate",
                json={"model_id": "bnm.clozapine-suicide-risk"},
                headers={"Cookie": "sid=trusted", "X-CSRF-Token": "csrf-secret"},
            )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
