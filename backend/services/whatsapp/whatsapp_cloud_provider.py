"""
Real integration with the Meta WhatsApp Cloud API sandbox.

Docs: https://developers.facebook.com/docs/whatsapp/cloud-api

Credentials are read from Django settings (which in turn come from
environment variables) and are NEVER logged or exposed to the
frontend.
"""
import logging

import requests
from django.conf import settings

from services.notification_engine.base_provider import (
    BaseNotificationProvider,
    ConfigurationError,
    ProviderResult,
)

logger = logging.getLogger("notifications")

REQUEST_TIMEOUT_SECONDS = 10


class WhatsAppCloudProvider(BaseNotificationProvider):
    channel_name = "WhatsApp"

    def __init__(self):
        config = settings.WHATSAPP_CONFIG
        self.access_token = config["ACCESS_TOKEN"]
        self.phone_number_id = config["PHONE_NUMBER_ID"]
        self.api_version = config["API_VERSION"]

    def is_configured(self) -> bool:
        return bool(self.access_token and self.phone_number_id)

    def _endpoint(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def send(self, *, recipient: str, subject: str, title: str, body: str) -> ProviderResult:
        self.check_configured()

        if not recipient:
            return ProviderResult(success=False, error_message="Recipient phone number is missing.")

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            # Sandbox/session messages support free-form text. Production
            # sends outside the 24h customer service window require an
            # approved message template instead - see docs/ARCHITECTURE.md.
            "text": {"preview_url": False, "body": body[:4096]},
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self._endpoint(), json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
            )
        except requests.Timeout:
            logger.warning("WhatsApp provider timed out sending to %s", recipient)
            return ProviderResult(success=False, error_message="WhatsApp request timed out.")
        except requests.RequestException as exc:
            logger.warning("WhatsApp provider network error: %s", exc.__class__.__name__)
            return ProviderResult(success=False, error_message="Network error contacting WhatsApp.")

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text[:500]}

        if response.status_code >= 400:
            error_detail = data.get("error", {}).get("message", "WhatsApp API error.")
            logger.warning("WhatsApp API error %s: %s", response.status_code, error_detail)
            return ProviderResult(success=False, raw_response=data, error_message=error_detail)

        message_id = ""
        messages = data.get("messages") or []
        if messages:
            message_id = messages[0].get("id", "")

        return ProviderResult(success=True, provider_message_id=message_id, raw_response=data)
