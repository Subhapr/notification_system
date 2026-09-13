"""
Maps each Channel to its concrete provider instance. This is the only
place the notification engine touches concrete provider classes -
everywhere else it only knows about BaseNotificationProvider.
"""
from apps.notifications.models import Channel
from services.email.providers import get_email_provider
from services.webpush.onesignal_provider import OneSignalWebPushProvider
from services.whatsapp.whatsapp_cloud_provider import WhatsAppCloudProvider


def get_provider_for_channel(channel: str):
    if channel == Channel.WHATSAPP:
        return WhatsAppCloudProvider()
    if channel == Channel.EMAIL:
        return get_email_provider()
    if channel == Channel.WEB_PUSH:
        return OneSignalWebPushProvider()
    raise ValueError(f"Unknown channel: {channel}")


def resolve_recipient(channel: str, user) -> str:
    """
    Resolves the delivery address for a channel given a user.
    Web Push recipients are resolved separately (per active
    subscription) by the engine since a user may have multiple
    subscribed browsers.
    """
    if channel == Channel.WHATSAPP:
        return getattr(user, "phone_number", "") or ""
    if channel == Channel.EMAIL:
        return getattr(user, "email", "") or ""
    return ""
