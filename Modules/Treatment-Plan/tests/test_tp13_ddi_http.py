import unittest

import httpx

from tests.test_tp13_ddi_hash_binding import no_interaction_response
from tests.test_tp13_ddi_check import primary_plan
from treatment_plan.ddi_check import DdiMedicationChecker
from treatment_plan.ddi_http import HttpDdiCheckerAdapter


class TP13HttpAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_posts_versioned_idempotent_interaction_check(self):
        captured = {}

        def handler(request):
            captured["request"] = request
            body = __import__("json").loads(request.content)
            return httpx.Response(200, json=no_interaction_response(body))

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await DdiMedicationChecker(
                HttpDdiCheckerAdapter("https://ddi.internal", client)
            ).check(primary_plan(), ())

        request = captured["request"]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.url.path, "/api/ddi-checker/v1/interaction-checks")
        self.assertEqual(request.headers["x-schema-version"], "1.0.0")
        self.assertEqual(request.headers["idempotency-key"], __import__("json").loads(request.content)["idempotencyKey"])
        self.assertTrue(result.allows_no_interactions_claim)


if __name__ == "__main__":
    unittest.main()
