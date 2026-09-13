from tests.base import BaseAPITestCase


class UsersDirectoryTests(BaseAPITestCase):
    def test_normal_user_forbidden(self):
        headers = self.auth_headers(self.normal_user, "UserPass123!")
        response = self.client.get("/api/auth/users/", **headers)
        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_users(self):
        headers = self.auth_headers(self.admin, "AdminPass123!")
        response = self.client.get("/api/auth/users/", **headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        emails = [u["email"] for u in body["data"]["results"]]
        self.assertIn("admin@test.local", emails)
        self.assertIn("user@test.local", emails)


class ConfigStatusTests(BaseAPITestCase):
    def test_config_status_requires_staff(self):
        headers = self.auth_headers(self.normal_user, "UserPass123!")
        response = self.client.get("/api/config-status/", **headers)
        self.assertEqual(response.status_code, 403)

    def test_config_status_reports_unconfigured_providers(self):
        headers = self.auth_headers(self.admin, "AdminPass123!")
        response = self.client.get("/api/config-status/", **headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("WHATSAPP", data)
        self.assertIn("EMAIL", data)
        self.assertIn("WEB_PUSH", data)
        # No real credentials are configured in the test environment.
        self.assertFalse(data["WHATSAPP"])
        self.assertFalse(data["WEB_PUSH"])
        # EMAIL_PROVIDER defaults to "console" mock mode, which is always "configured".
        self.assertTrue(data["EMAIL"])
