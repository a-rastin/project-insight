from _support import AuthTestCase
import security


class AuthContractTests(AuthTestCase):
    def test_login_role_contract_and_safe_redirects(self):
        client = self.client()

        invalid_role = client.post(
            "/api/auth/login",
            json={"username": "Admin", "password": "Admin", "role": "clinician"},
        )
        self.assertEqual(invalid_role.status_code, 422)

        mismatch = client.post(
            "/api/auth/login",
            json={"username": "Admin", "password": "Admin", "role": "psychiatrist"},
        )
        self.assertEqual(mismatch.status_code, 403)
        self.assertEqual(mismatch.json()["detail"], "Wrong username or password")

        login = client.post(
            "/api/auth/login",
            json={
                "username": "Admin",
                "password": "Admin",
                "role": "admin",
                "next": "https://example.com/steal",
            },
        )
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json()["next"], "/dashboard/admin")

    def test_admin_lifecycle_contract_revokes_stale_sessions(self):
        client = self.login_admin()
        created = client.post(
            "/api/auth/register",
            json={"username": "doc3", "password": "secret", "role": "psychiatrist"},
        )
        self.assertEqual(created.status_code, 201)
        doc = security.get_user("doc3")
        security.set_disclaimer_signed(doc["user_uuid"])

        user_client = self.client()
        self.assertEqual(
            user_client.post(
                "/api/auth/login",
                json={"username": "doc3", "password": "secret", "role": "psychiatrist"},
            ).status_code,
            200,
        )
        user_token = user_client.cookies.get(security.cfg("AUTH_COOKIE_NAME"))
        self.assertEqual(user_client.get("/api/auth/session/legacy").status_code, 200)

        reset = client.post(
            f"/api/auth/admin/users/{doc['user_uuid']}/reset-password",
            json={"temporary_password": "temp-doc3"},
        )
        self.assertEqual(reset.status_code, 200)
        self.assertEqual(reset.json()["temporary_password"], "temp-doc3")
        self.assertEqual(self.client_with_session_token(user_token).get("/api/auth/session/legacy").status_code, 401)

        temp_client = self.client()
        temp_login = temp_client.post(
            "/api/auth/login",
            json={"username": "doc3", "password": "temp-doc3", "role": "psychiatrist"},
        )
        self.assertEqual(temp_login.status_code, 200)
        self.assertEqual(temp_login.json()["next"], "/dashboard/user")
        self.assertEqual(temp_client.get("/api/auth/session/legacy").status_code, 200)

        rotated = temp_client.post(
            "/api/auth/password/change",
            json={"current_password": "temp-doc3", "new_password": "rotated-doc3"},
        )
        self.assertEqual(rotated.status_code, 200)
        self.assertEqual(temp_client.get("/api/auth/session/legacy").status_code, 200)

        role_update = client.patch(f"/api/auth/admin/users/{doc['user_uuid']}/role", json={"role": "admin"})
        self.assertEqual(role_update.status_code, 200)
        self.assertEqual(temp_client.get("/api/auth/session/legacy").status_code, 401)

        admin_login = self.client()
        self.assertEqual(
            admin_login.post(
                "/api/auth/login",
                json={"username": "doc3", "password": "rotated-doc3", "role": "admin"},
            ).status_code,
            200,
        )

    def test_unauthorized_admin_contract(self):
        anonymous = self.client().get("/api/auth/admin/users")
        self.assertEqual(anonymous.status_code, 401)

        client = self.login_admin()
        admin = security.get_user("Admin")
        self_disable = client.post(f"/api/auth/admin/users/{admin['user_uuid']}/disable")
        self.assertEqual(self_disable.status_code, 403)
        self_demote = client.patch(f"/api/auth/admin/users/{admin['user_uuid']}/role", json={"role": "psychiatrist"})
        self.assertEqual(self_demote.status_code, 403)


if __name__ == "__main__":
    import unittest

    unittest.main()
