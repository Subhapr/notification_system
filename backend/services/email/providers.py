"""
Email provider abstraction.

BaseEmailProvider defines the contract. PostmarkEmailProvider is the
real, production integration. ConsoleEmailProvider is an explicit,
clearly-labelled development/mock mode that never claims to be a real
send (see apps/notifications: NotificationLog.provider_response
includes a `mode` field distinguishing REAL vs MOCK).

Adding another provider (Brevo, Resend, ...) means adding one class
here and registering it in `get_email_provider()` - the notification
engine and views never need to change.
"""
import logging

import requests
from django.conf import settings

from services.notification_engine.base_provider import (
    BaseNotificationProvider,
    ProviderResult,
)

logger = logging.getLogger("notifications")

REQUEST_TIMEOUT_SECONDS = 10


class BaseEmailProvider(BaseNotificationProvider):
    channel_name = "Email"


class PostmarkEmailProvider(BaseEmailProvider):
    """Real integration with the Postmark transactional email API."""

    ENDPOINT = "https://api.postmarkapp.com/email"

    def __init__(self):
        config = settings.POSTMARK_CONFIG
        self.server_token = config["SERVER_TOKEN"]
        self.from_email = config["FROM_EMAIL"]

    def is_configured(self) -> bool:
        return bool(self.server_token and self.from_email)

    def send(self, *, recipient: str, subject: str, title: str, body: str) -> ProviderResult:
        self.check_configured()

        if not recipient:
            return ProviderResult(success=False, error_message="Recipient email is missing.")

        payload = {
            "From": self.from_email,
            "To": recipient,
            "Subject": subject or "(no subject)",
            "HtmlBody": body,
            "TextBody": body,
            "MessageStream": "outbound",
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Postmark-Server-Token": self.server_token,
        }

        try:
            response = requests.post(
                self.ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
            )
        except requests.Timeout:
            logger.warning("Postmark provider timed out sending to %s", recipient)
            return ProviderResult(success=False, error_message="Postmark request timed out.")
        except requests.RequestException as exc:
            logger.warning("Postmark provider network error: %s", exc.__class__.__name__)
            return ProviderResult(success=False, error_message="Network error contacting Postmark.")

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text[:500]}

        if response.status_code >= 400:
            error_detail = data.get("Message", "Postmark API error.")
            logger.warning("Postmark API error %s: %s", response.status_code, error_detail)
            return ProviderResult(success=False, raw_response=data, error_message=error_detail)

        return ProviderResult(
            success=True,
            provider_message_id=data.get("MessageID", ""),
            raw_response=data,
        )


class BrevoEmailProvider(BaseEmailProvider):
    """
    Placeholder adapter demonstrating how a second real provider would
    slot in behind the same interface. Not wired up by default; set
    EMAIL_PROVIDER=brevo and implement the API call here to activate it.
    """

    def is_configured(self) -> bool:
        return False

    def send(self, *, recipient: str, subject: str, title: str, body: str) -> ProviderResult:
        self.check_configured()
        raise NotImplementedError("Brevo integration has not been implemented yet.")


class ConsoleEmailProvider(BaseEmailProvider):
    """
    Explicit MOCK/DEVELOPMENT provider. Never contacts a real API and
    never pretends the message left the building - it only logs the
    email and is clearly labelled as MOCK in every NotificationLog
    entry it produces.
    """

    def is_configured(self) -> bool:
        return True

    def send(self, *, recipient: str, subject: str, title: str, body: str) -> ProviderResult:
        logger.info("[MOCK EMAIL] to=%s subject=%r", recipient, subject)
        return ProviderResult(
            success=True,
            provider_message_id="mock-console",
            raw_response={"mode": "MOCK", "note": "Logged to console only, not actually sent."},
        )


def get_email_provider() -> BaseEmailProvider:
    provider_name = settings.EMAIL_PROVIDER.lower()
    providers = {
        "postmark": PostmarkEmailProvider,
        "brevo": BrevoEmailProvider,
        "console": ConsoleEmailProvider,
    }
    provider_class = providers.get(provider_name, ConsoleEmailProvider)
    return provider_class()
