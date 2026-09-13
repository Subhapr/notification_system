from django.test import TestCase

from apps.accounts.models import User
from apps.notifications.models import Channel, NotificationTemplate, Trigger


class BaseAPITestCase(TestCase):
    """Shared setup for admin user, normal user, and a LOGIN/LOGOUT trigger pair."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.local",
            password="AdminPass123!",
            is_staff=True,
            is_superuser=True,
            full_name="Admin Test",
            phone_number="+15550000001",
        )
        self.normal_user = User.objects.create_user(
            email="user@test.local",
            password="UserPass123!",
            full_name="Normal Test",
            phone_number="+15550000002",
        )
        self.login_trigger = Trigger.objects.create(
            code="LOGIN", name="Login", description="Fires on login", is_active=True
        )
        self.logout_trigger = Trigger.objects.create(
            code="LOGOUT", name="Logout", description="Fires on logout", is_active=True
        )

    def make_template(self, trigger, channel, enabled=True, **overrides):
        defaults = {
            "trigger": trigger,
            "channel": channel,
            "name": f"{trigger.code}-{channel}",
            "body": "Hi {{user_name}}, event at {{login_time}}.",
            "subject": "Subject {{site_name}}" if channel == Channel.EMAIL else "",
            "title": "Title" if channel == Channel.WEB_PUSH else "",
            "enabled": enabled,
        }
        defaults.update(overrides)
        return NotificationTemplate.objects.create(**defaults)

    def auth_headers(self, user, password):
        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": password},
            content_type="application/json",
        )
        access = response.json()["data"]["tokens"]["access"]
        return {"HTTP_AUTHORIZATION": f"Bearer {access}"}
