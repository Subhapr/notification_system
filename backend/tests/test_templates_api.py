from unittest.mock import patch

from apps.notifications.models import Channel, NotificationTemplate
from services.notification_engine.base_provider import ProviderResult
from tests.base import BaseAPITestCase


class TemplatePermissionTests(BaseAPITestCase):
    def test_normal_user_cannot_list_templates(self):
        headers = self.auth_headers(self.normal_user, "UserPass123!")
        response = self.client.get("/api/notification-templates/", **headers)
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_create_template(self):
        headers = self.auth_headers(self.normal_user, "UserPass123!")
        response = self.client.post(
            "/api/notification-templates/",
            {
                "trigger": self.login_trigger.id,
                "channel": Channel.EMAIL,
                "name": "Hack attempt",
                "subject": "x",
                "body": "x",
            },
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_request_rejected(self):
        response = self.client.get("/api/notification-templates/")
        self.assertEqual(response.status_code, 401)

    def test_admin_can_list_and_create_templates(self):
        headers = self.auth_headers(self.admin, "AdminPass123!")
        response = self.client.post(
            "/api/notification-templates/",
            {
                "trigger": self.login_trigger.id,
                "channel": Channel.EMAIL,
                "name": "Login email",
                "subject": "Welcome {{user_name}}",
                "body": "Hi {{user_name}}",
                "enabled": True,
            },
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(NotificationTemplate.objects.count(), 1)


class TemplateToggleAndTestSendTests(BaseAPITestCase):
    def test_toggle_flips_enabled_state(self):
        template = self.make_template(self.login_trigger, Channel.EMAIL, enabled=False)
        headers = self.auth_headers(self.admin, "AdminPass123!")

        response = self.client.post(
            f"/api/notification-templates/{template.id}/toggle/", **headers
        )
        self.assertEqual(response.status_code, 200)
        template.refresh_from_db()
        self.assertTrue(template.enabled)

        response = self.client.post(
            f"/api/notification-templates/{template.id}/toggle/", **headers
        )
        template.refresh_from_db()
        self.assertFalse(template.enabled)

    @patch("services.notification_engine.provider_registry.get_email_provider")
    def test_send_test_success(self, mock_email_factory):
        mock_provider = mock_email_factory.return_value
        mock_provider.is_configured.return_value = True
        mock_provider.send.return_value = ProviderResult(success=True, provider_message_id="msg-1")

        template = self.make_template(self.login_trigger, Channel.EMAIL, enabled=True)
        headers = self.auth_headers(self.admin, "AdminPass123!")

        response = self.client.post(
            f"/api/notification-templates/{template.id}/test/",
            {"test_recipient": "someone@example.com"},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_send_test_unconfigured_provider_returns_error(self):
        # WhatsApp has no credentials configured in the test environment.
        template = self.make_template(self.login_trigger, Channel.WHATSAPP, enabled=True)
        headers = self.auth_headers(self.admin, "AdminPass123!")

        response = self.client.post(
            f"/api/notification-templates/{template.id}/test/",
            {"test_recipient": "+15551234567"},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.json()["success"])


class WebPushSubscriptionTests(BaseAPITestCase):
    def test_user_can_subscribe_own_browser(self):
        headers = self.auth_headers(self.normal_user, "UserPass123!")
        response = self.client.post(
            "/api/webpush/subscribe/",
            {"external_subscription_id": "sub-abc", "browser": "Chrome"},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.normal_user.webpush_subscriptions.count(), 1)

    def test_user_can_unsubscribe(self):
        headers = self.auth_headers(self.normal_user, "UserPass123!")
        self.client.post(
            "/api/webpush/subscribe/",
            {"external_subscription_id": "sub-abc"},
            content_type="application/json",
            **headers,
        )
        response = self.client.post(
            "/api/webpush/unsubscribe/",
            {"external_subscription_id": "sub-abc"},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        sub = self.normal_user.webpush_subscriptions.get(external_subscription_id="sub-abc")
        self.assertFalse(sub.is_active)
