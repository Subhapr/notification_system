from unittest.mock import patch

from apps.notifications.models import (
    Channel,
    NotificationLog,
    NotificationStatus,
    WebPushSubscription,
)
from services.notification_engine.base_provider import ProviderResult
from services.notification_engine.engine import NotificationEngine
from services.notification_engine.template_renderer import (
    extract_variable_names,
    render_template_string,
)
from tests.base import BaseAPITestCase


class TemplateRendererTests(BaseAPITestCase):
    def test_render_replaces_known_variables(self):
        result = render_template_string("Hi {{user_name}}, welcome to {{site_name}}!", {
            "user_name": "Ada",
            "site_name": "NotifyHub",
        })
        self.assertEqual(result, "Hi Ada, welcome to NotifyHub!")

    def test_render_leaves_unknown_variables_blank_not_broken(self):
        result = render_template_string("Hi {{unknown_var}}", {})
        self.assertEqual(result, "Hi ")

    def test_render_does_not_evaluate_arbitrary_python(self):
        malicious = "{{__import__('os').system('echo hacked')}}"
        result = render_template_string(malicious, {})
        # The pattern only matches simple identifiers, so this is left
        # untouched rather than executed.
        self.assertEqual(result, malicious)

    def test_extract_variable_names(self):
        names = extract_variable_names("{{user_name}} logged in at {{login_time}} on {{user_name}}")
        self.assertEqual(names, ["user_name", "login_time"])


class NotificationEngineChannelIsolationTests(BaseAPITestCase):
    @patch("services.notification_engine.provider_registry.get_email_provider")
    @patch("services.notification_engine.provider_registry.WhatsAppCloudProvider")
    def test_one_channel_failure_does_not_block_others(self, mock_whatsapp_cls, mock_email_factory):
        # Email succeeds, WhatsApp fails - both should be logged independently.
        mock_email_provider = mock_email_factory.return_value
        mock_email_provider.is_configured.return_value = True
        mock_email_provider.send.return_value = ProviderResult(
            success=True, provider_message_id="email-123"
        )

        mock_whatsapp_provider = mock_whatsapp_cls.return_value
        mock_whatsapp_provider.is_configured.return_value = True
        mock_whatsapp_provider.check_configured.return_value = None
        mock_whatsapp_provider.send.return_value = ProviderResult(
            success=False, error_message="Invalid recipient"
        )

        self.make_template(self.login_trigger, Channel.EMAIL, enabled=True)
        self.make_template(self.login_trigger, Channel.WHATSAPP, enabled=True)

        results = NotificationEngine.fire(
            trigger_code="LOGIN", user=self.admin, context={"login_time": "10:00"}
        )

        statuses = {r["channel"]: r["status"] for r in results}
        self.assertEqual(statuses[Channel.EMAIL], NotificationStatus.SENT)
        self.assertEqual(statuses[Channel.WHATSAPP], NotificationStatus.FAILED)

        self.assertEqual(
            NotificationLog.objects.filter(channel=Channel.EMAIL, status=NotificationStatus.SENT).count(),
            1,
        )
        self.assertEqual(
            NotificationLog.objects.filter(
                channel=Channel.WHATSAPP, status=NotificationStatus.FAILED
            ).count(),
            1,
        )

    def test_inactive_trigger_is_skipped_entirely(self):
        self.login_trigger.is_active = False
        self.login_trigger.save()
        self.make_template(self.login_trigger, Channel.EMAIL, enabled=True)

        results = NotificationEngine.fire(trigger_code="LOGIN", user=self.admin, context={})
        self.assertEqual(results, [])
        self.assertEqual(NotificationLog.objects.count(), 0)

    def test_disabled_channel_is_not_sent(self):
        self.make_template(self.login_trigger, Channel.EMAIL, enabled=False)
        results = NotificationEngine.fire(trigger_code="LOGIN", user=self.admin, context={})
        self.assertEqual(results, [])

    def test_missing_recipient_is_skipped_not_failed(self):
        # normal_user has no phone number cleared out for this case
        self.normal_user.phone_number = ""
        self.normal_user.save()
        self.make_template(self.login_trigger, Channel.WHATSAPP, enabled=True)

        results = NotificationEngine.fire(trigger_code="LOGIN", user=self.normal_user, context={})
        self.assertEqual(results[0]["status"], NotificationStatus.SKIPPED)

    def test_webpush_uses_active_subscription(self):
        WebPushSubscription.objects.create(
            user=self.admin, external_subscription_id="sub-123", is_active=True
        )
        self.make_template(self.login_trigger, Channel.WEB_PUSH, enabled=True)

        with patch(
            "services.notification_engine.engine.get_provider_for_channel"
        ) as mock_get_provider:
            mock_provider = mock_get_provider.return_value
            mock_provider.send.return_value = ProviderResult(success=True, provider_message_id="push-1")
            results = NotificationEngine.fire(trigger_code="LOGIN", user=self.admin, context={})

        self.assertEqual(results[0]["status"], NotificationStatus.SENT)
        log = NotificationLog.objects.get(channel=Channel.WEB_PUSH)
        self.assertEqual(log.recipient, "sub-123")
