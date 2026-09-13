"""
Base provider contract. Every channel adapter (WhatsApp, Email, Web
Push) implements this interface so the NotificationEngine never has
to know about raw HTTP/API details of any specific vendor.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProviderResult:
    """Normalized result returned by every provider's send() call."""

    success: bool
    provider_message_id: str = ""
    raw_response: dict = field(default_factory=dict)
    error_message: str = ""


class ConfigurationError(Exception):
    """Raised when a provider is invoked without the credentials it needs."""


class BaseNotificationProvider:
    """
    Every concrete provider must implement `send`, and should raise
    `ConfigurationError` from `check_configured()` if required
    credentials are missing, rather than failing with a confusing
    downstream error.
    """

    channel_name = "base"

    def is_configured(self) -> bool:
        raise NotImplementedError

    def check_configured(self):
        if not self.is_configured():
            raise ConfigurationError(
                f"{self.channel_name} provider is not configured. "
                f"See docs/ENVIRONMENT_VARIABLES.md."
            )

    def send(self, *, recipient: str, subject: str, title: str, body: str) -> ProviderResult:
        raise NotImplementedError
