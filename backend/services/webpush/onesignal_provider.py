"""
Real integration with the OneSignal REST API for browser Web Push.

Docs: https://documentation.onesignal.com/reference/create-notification

The REST API key is server-side only and must never be sent to the
frontend - only NEXT_PUBLIC_ONESIGNAL_APP_ID (a public, non-secret
identifier) is exposed there.
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
ENDPOINT = "https://onesignal.com/api/v1/notifications"


class OneSignalWebPushProvider(BaseNotificationProvider):
    channel_name = "Web Push"

    def __init__(self):
        config = settings.ONESIGNAL_CONFIG
        self.app_id = config["APP_ID"]
        self.rest_api_key = config["REST_API_KEY"]

    def is_configured(self) -> bool:
        return bool(self.app_id and self.rest_api_key)

    def send(self, *, recipient: str, subject: str, title: str, body: str) -> ProviderResult:
        """`recipient` is the OneSignal external_subscription_id (player id)."""
        self.check_configured()

        if not recipient:
            return ProviderResult(
                success=False,
                error_message="No active Web Push subscription for this user's browser.",
            )

        payload = {
            "app_id": self.app_id,
            "include_subscription_ids": [recipient],
            "headings": {"en": title or settings.SITE_NAME},
            "contents": {"en": body},
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.rest_api_key}",
        }

        try:
            response = requests.post(
                ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
            )
        except requests.Timeout:
            logger.warning("OneSignal provider timed out sending to %s", recipient)
            return ProviderResult(success=False, error_message="OneSignal request timed out.")
        except requests.RequestException as exc:
            logger.warning("OneSignal provider network error: %s", exc.__class__.__name__)
            return ProviderResult(success=False, error_message="Network error contacting OneSignal.")

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text[:500]}

        if response.status_code >= 400 or data.get("errors"):
            error_detail = str(data.get("errors", "OneSignal API error."))
            logger.warning("OneSignal API error %s: %s", response.status_code, error_detail)
            return ProviderResult(success=False, raw_response=data, error_message=error_detail)

        return ProviderResult(success=True, provider_message_id=data.get("id", ""), raw_response=data)
