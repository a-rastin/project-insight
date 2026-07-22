import json
from pathlib import Path

from _support import AuthTestCase
import security


MODULE_ROOT = Path(__file__).parents[1]
CONTRACT_ROOT = MODULE_ROOT / "contracts"


class AuthDiscoveryTests(AuthTestCase):
    def test_contract_describes_runtime_security_and_compatibility_policy(self):
        client = self.raw_client()
        response = client.get("/contract")

        self.assertEqual(response.status_code, 200)
        contract = response.json()
        self.assertEqual(contract["moduleId"], "authentication")
        self.assertEqual(contract["basePath"], "/api/auth")
        self.assertEqual(contract["securityPolicy"]["sessionCookie"], {
            "name": security.cfg("AUTH_COOKIE_NAME"),
            "httpOnly": security.cookie_kwargs()["httponly"],
            "sameSite": "Lax",
            "secure": security.cookie_kwargs()["secure"],
            "path": security.cookie_kwargs()["path"],
            "maxAgeSeconds": security.cookie_kwargs()["max_age"],
        })
        self.assertEqual(contract["securityPolicy"]["csrf"], {
            "strategy": "signed-double-submit",
            "bootstrapPath": "/api/auth/csrf",
            "cookieName": security.cfg("AUTH_CSRF_COOKIE_NAME"),
            "headerName": security.cfg("AUTH_CSRF_HEADER_NAME"),
            "httpOnly": security.csrf_cookie_kwargs()["httponly"],
            "sameSite": "Lax",
            "secure": security.csrf_cookie_kwargs()["secure"],
            "path": security.csrf_cookie_kwargs()["path"],
            "maxAgeSeconds": security.csrf_cookie_kwargs()["max_age"],
            "writeMethods": ["POST", "PATCH"],
            "failureStatus": 403,
        })
        self.assertIn("session response", contract["securityPolicy"]["downstreamTrust"])
        self.assertIn("JWT", contract["securityPolicy"]["downstreamTrust"])
        self.assertEqual(contract["securityPolicy"]["jwks"], "deferred")
        self.assertTrue(any(route["path"] == "/api/auth/session/legacy" and route["deprecated"]
                            for route in contract["compatibilityRoutes"]))
        self.assertEqual(contract["compatibility"]["sessionAuthority"], "/api/auth/session")

    def test_openapi_and_published_schemas_are_consistent(self):
        client = self.raw_client()
        openapi_response = client.get("/openapi.json")
        self.assertEqual(openapi_response.status_code, 200)
        openapi = openapi_response.json()
        self.assertEqual(openapi["openapi"], "3.1.0")
        self.assertIn("/contract", openapi["paths"])
        self.assertIn("/api/auth/session", openapi["paths"])
        self.assertIn("/api/auth/session/legacy", openapi["paths"])

        contract = client.get("/contract").json()
        for name in contract["schemas"]:
            schema_response = client.get(f"/schemas/1.0.0/{name}")
            self.assertEqual(schema_response.status_code, 200)
            schema = schema_response.json()
            self.assertEqual(schema["$id"], f"urn:insight:authentication:1.0.0:{name}")
            self.assertEqual(json.loads((CONTRACT_ROOT / "schemas" / "1.0.0" / f"{name}.schema.json").read_text())["$id"], schema["$id"])

        self.assertEqual(client.get("/schemas/1.0.0/not-published").status_code, 404)

    def test_readiness_and_errors_never_disclose_secrets_paths_or_urls(self):
        secret = security.cfg("AUTH_JWT_SECRET")
        for path in ("/api/auth/ready", "/readyz"):
            body = self.raw_client().get(path).text
            self.assertNotIn(secret, body)
            self.assertNotIn(self.db_path, body)
            self.assertNotIn("localhost", body.lower())
            self.assertNotIn("127.0.0.1", body)
            self.assertNotIn("https://", body.lower())

        invalid_csrf = self.raw_client().post(
            "/api/auth/login",
            json={"username": "Admin", "password": "Admin", "role": "admin"},
        )
        self.assertEqual(invalid_csrf.status_code, 403)
        self.assertNotIn(secret, invalid_csrf.text)
        self.assertNotIn(self.db_path, invalid_csrf.text)


if __name__ == "__main__":
    import unittest

    unittest.main()
