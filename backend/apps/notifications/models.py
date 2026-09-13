import uuid

from django.conf import settings
from django.db import models


class Channel(models.TextChoices):
    WHATSAPP = "WHATSAPP", "WhatsApp"
    EMAIL = "EMAIL", "Email"
    WEB_PUSH = "WEB_PUSH", "Web Push"


class NotificationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    SKIPPED = "SKIPPED", "Skipped"


class Trigger(models.Model):
    """
    A data-driven event definition (e.g. LOGIN, LOGOUT). New triggers
    can be added entirely from the admin UI/API without any code
    change to the notification engine - the engine only ever looks
    triggers up by `code`.
    """

    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=64, unique=True, help_text="Stable machine code, e.g. LOGIN")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.code


class NotificationTemplate(models.Model):
    """
    A template belongs to exactly one (trigger, channel) pair. This is
    what the "Notification Settings" matrix on the frontend renders as
    a single cell.
    """

    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE, related_name="templates")
    channel = models.CharField(max_length=20, choices=Channel.choices)

    name = models.CharField(max_length=150)
    subject = models.CharField(max_length=255, blank=True, help_text="Email subject line only.")
    title = models.CharField(max_length=255, blank=True, help_text="Web Push title only.")
    body = models.TextField(help_text="Message body. Supports {{variable}} placeholders.")

    enabled = models.BooleanField(default=False)
    variable_mapping = models.JSONField(
        default=list,
        blank=True,
        help_text="List of variable names available for this trigger, e.g. ['user_name', 'email'].",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trigger", "channel"], name="unique_template_per_trigger_channel"
            )
        ]
        ordering = ["trigger__name", "channel"]

    def __str__(self):
        return f"{self.trigger.code} / {self.channel}"


class NotificationLog(models.Model):
    """
    Immutable audit trail of every notification attempt. Each channel
    is logged independently so a failure in one channel never hides
    the success of another.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notification_logs",
    )
    trigger = models.ForeignKey(
        Trigger, on_delete=models.SET_NULL, null=True, related_name="logs"
    )
    channel = models.CharField(max_length=20, choices=Channel.choices)
    template = models.ForeignKey(
        NotificationTemplate, on_delete=models.SET_NULL, null=True, related_name="logs"
    )

    status = models.CharField(
        max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING
    )
    recipient = models.CharField(max_length=255, blank=True)
    rendered_subject = models.CharField(max_length=255, blank=True)
    rendered_body = models.TextField(blank=True)

    provider_message_id = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    is_test = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["channel"]),
        ]

    def __str__(self):
        return f"{self.channel} -> {self.recipient} [{self.status}]"


class WebPushSubscription(models.Model):
    """
    Registered browser Web Push subscription (OneSignal player/
    subscription id). Admins never enter this manually - the browser
    registers it automatically once the visitor grants permission.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="webpush_subscriptions"
    )
    external_subscription_id = models.CharField(
        max_length=255, unique=True, help_text="OneSignal player/subscription id."
    )
    browser = models.CharField(max_length=100, blank=True)
    device_metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} · {self.external_subscription_id[:12]}"
