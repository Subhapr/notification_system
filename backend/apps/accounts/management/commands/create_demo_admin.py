import os

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User


class Command(BaseCommand):
    """
    Development-only helper for creating a demo admin user.

    Credentials are never hardcoded. Provide them via CLI arguments or
    the DEMO_ADMIN_EMAIL / DEMO_ADMIN_PASSWORD environment variables.

    Usage:
        python manage.py create_demo_admin --email admin@example.com --password changeme123
        # or
        DEMO_ADMIN_EMAIL=admin@example.com DEMO_ADMIN_PASSWORD=changeme123 python manage.py create_demo_admin
    """

    help = "Create (or update) a demo admin user for local development."

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, default=None)
        parser.add_argument("--password", type=str, default=None)

    def handle(self, *args, **options):
        email = options["email"] or os.getenv("DEMO_ADMIN_EMAIL")
        password = options["password"] or os.getenv("DEMO_ADMIN_PASSWORD")

        if not email or not password:
            raise CommandError(
                "Provide --email/--password or set DEMO_ADMIN_EMAIL / "
                "DEMO_ADMIN_PASSWORD environment variables."
            )

        user, created = User.objects.get_or_create(
            email=email.lower().strip(),
            defaults={"is_staff": True, "is_superuser": True, "full_name": "Demo Admin"},
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} admin user: {email}"))
