from apps.notifications.models import Channel, NotificationLog, NotificationStatus
from tests.base import BaseAPITestCase


class LoginTriggerTests(BaseAPITestCase):
    def test_login_success_returns_tokens_and_user(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "admin@test.local", "password": "AdminPass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertIn("access", body["data"]["tokens"])
        self.assertIn("refresh", body["data"]["tokens"])
        self.assertEqual(body["data"]["user"]["email"], "admin@test.local")

    def test_login_invalid_credentials_rejected(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "admin@test.local", "password": "wrong"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_login_fires_enabled_email_template_and_logs_it(self):
        self.make_template(self.login_trigger, Channel.EMAIL, enabled=True)

        response = self.client.post(
            "/api/auth/login/",
            {"email": "admin@test.local", "password": "AdminPass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        logs = NotificationLog.objects.filter(channel=Channel.EMAIL)
        self.assertEqual(logs.count(), 1)
        log = logs.first()
        self.assertEqual(log.status, NotificationStatus.SENT)
        self.assertEqual(log.recipient, "admin@test.local")
        self.assertIn("Admin Test", log.rendered_body)

    def test_login_does_not_fire_disabled_template(self):
        self.make_template(self.login_trigger, Channel.EMAIL, enabled=False)

        self.client.post(
            "/api/auth/login/",
            {"email": "admin@test.local", "password": "AdminPass123!"},
            content_type="application/json",
        )
        self.assertEqual(NotificationLog.objects.count(), 0)

    def test_login_does_not_fire_logout_templates(self):
        self.make_template(self.logout_trigger, Channel.EMAIL, enabled=True)

        self.client.post(
            "/api/auth/login/",
            {"email": "admin@test.local", "password": "AdminPass123!"},
            content_type="application/json",
        )
        self.assertEqual(NotificationLog.objects.count(), 0)


class LogoutTriggerTests(BaseAPITestCase):
    def test_logout_requires_authentication(self):
        response = self.client.post(
            "/api/auth/logout/", {"refresh": "bogus"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_logout_fires_enabled_templates_and_blacklists_token(self):
        self.make_template(self.logout_trigger, Channel.WHATSAPP, enabled=True)

        login_response = self.client.post(
            "/api/auth/login/",
            {"email": "admin@test.local", "password": "AdminPass123!"},
            content_type="application/json",
        )
        tokens = login_response.json()["data"]["tokens"]

        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": tokens["refresh"]},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )
        self.assertEqual(response.status_code, 200)

        # WhatsApp isn't configured in tests, so the channel should be
        # logged as FAILED (configuration error) rather than silently
        # dropped or crashing the logout request.
        logs = NotificationLog.objects.filter(channel=Channel.WHATSAPP)
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().status, NotificationStatus.FAILED)

        # Refresh token should now be blacklisted.
        refresh_response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": tokens["refresh"]},
            content_type="application/json",
        )
        self.assertEqual(refresh_response.status_code, 401)


class MeEndpointTests(BaseAPITestCase):
    def test_me_requires_auth(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 401)

    def test_me_returns_current_user(self):
        headers = self.auth_headers(self.normal_user, "UserPass123!")
        response = self.client.get("/api/auth/me/", **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["email"], "user@test.local")
