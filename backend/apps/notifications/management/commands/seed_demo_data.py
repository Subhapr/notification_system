from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.notifications.models import Channel, NotificationTemplate, Trigger

DEMO_ADMIN_EMAIL = "admin@notifyhub.local"
DEMO_USER_EMAIL = "user@notifyhub.local"
DEMO_PASSWORD = "DemoPass123!"

TRIGGERS = [
    {
        "code": "LOGIN",
        "name": "User Login",
        "description": "Fires whenever a user successfully authenticates.",
    },
    {
        "code": "LOGOUT",
        "name": "User Logout",
        "description": "Fires whenever a user logs out.",
    },
]

SAMPLE_TEMPLATES = {
    "LOGIN": {
        Channel.WHATSAPP: {
            "name": "Login - WhatsApp",
            "body": "Hi {{user_name}}, you just logged in to {{site_name}} at {{login_time}}.",
        },
        Channel.EMAIL: {
            "name": "Login - Email",
            "subject": "Welcome back to {{site_name}}",
            "body": "<p>Hi {{user_name}},</p><p>You logged in successfully at {{login_time}}.</p>",
        },
        Channel.WEB_PUSH: {
            "name": "Login - Web Push",
            "title": "Welcome back!",
            "body": "Hi {{user_name}}, your login to {{site_name}} was successful.",
        },
    },
    "LOGOUT": {
        Channel.WHATSAPP: {
            "name": "Logout - WhatsApp",
            "body": "Hi {{user_name}}, you logged out of {{site_name}} at {{logout_time}}.",
        },
        Channel.EMAIL: {
            "name": "Logout - Email",
            "subject": "You've been logged out of {{site_name}}",
            "body": "<p>Hi {{user_name}},</p><p>You logged out at {{logout_time}}. If this wasn't you, please secure your account.</p>",
        },
        Channel.WEB_PUSH: {
            "name": "Logout - Web Push",
            "title": "Signed out",
            "body": "Hi {{user_name}}, you've been signed out of {{site_name}}.",
        },
    },
}


class Command(BaseCommand):
    help = "Seed safe demo data: admin/normal users, LOGIN/LOGOUT triggers, sample templates."

    def handle(self, *args, **options):
        admin_user, created = User.objects.get_or_create(
            email=DEMO_ADMIN_EMAIL,
            defaults={"is_staff": True, "is_superuser": True, "full_name": "Demo Admin"},
        )
        if created:
            admin_user.set_password(DEMO_PASSWORD)
            admin_user.save()

        normal_user, created = User.objects.get_or_create(
            email=DEMO_USER_EMAIL,
            defaults={"full_name": "Demo User", "phone_number": ""},
        )
        if created:
            normal_user.set_password(DEMO_PASSWORD)
            normal_user.save()

        for trigger_data in TRIGGERS:
            trigger, _ = Trigger.objects.update_or_create(
                code=trigger_data["code"],
                defaults={
                    "name": trigger_data["name"],
                    "description": trigger_data["description"],
                    "is_active": True,
                },
            )
            channel_templates = SAMPLE_TEMPLATES.get(trigger.code, {})
            for channel, data in channel_templates.items():
                NotificationTemplate.objects.update_or_create(
                    trigger=trigger,
                    channel=channel,
                    defaults={
                        "name": data["name"],
                        "subject": data.get("subject", ""),
                        "title": data.get("title", ""),
                        "body": data["body"],
                        # Disabled by default - the admin turns channels on
                        # once real provider credentials are configured.
                        "enabled": False,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
        self.stdout.write(f"  Admin login: {DEMO_ADMIN_EMAIL} / {DEMO_PASSWORD}")
        self.stdout.write(f"  Normal user: {DEMO_USER_EMAIL} / {DEMO_PASSWORD}")
        self.stdout.write("  Templates seeded as DISABLED (no provider credentials configured yet).")
