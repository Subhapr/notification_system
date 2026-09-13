"""
NotificationEngine: the single entry point for firing a notification
event anywhere in the codebase (login, logout, and any future trigger
such as ORDER_PLACED).

    NotificationEngine.fire(trigger_code="LOGIN", user=user, context={...})

Flow (mirrors docs/ARCHITECTURE.md):

    Trigger occurs
        -> load active Trigger by code
        -> load enabled NotificationTemplates for that trigger
        -> for each enabled channel:
              resolve variables -> render template -> send through
              provider adapter -> create NotificationLog
        -> return a per-channel result summary

A failure sending one channel never prevents the others from being
attempted, and never propagates as an exception to the caller (e.g.
the login view) - so notification delivery problems can never break
core application flows like authentication.
"""
import logging

from apps.notifications.models import (
    Channel,
    NotificationLog,
    NotificationStatus,
    NotificationTemplate,
    Trigger,
)
from services.notification_engine.base_provider import ConfigurationError
from services.notification_engine.provider_registry import (
    get_provider_for_channel,
    resolve_recipient,
)
from services.notification_engine.template_renderer import render_template_string
from services.notification_engine.variables import build_context

logger = logging.getLogger("notifications")


class NotificationEngine:
    @classmethod
    def fire(cls, *, trigger_code: str, user, context: dict = None) -> list:
        """
        Fires every enabled, configured template for the given trigger.
        Returns a list of dicts summarizing the per-channel outcome,
        e.g. [{"channel": "EMAIL", "status": "SENT"}, ...].
        """
        try:
            trigger = Trigger.objects.get(code=trigger_code, is_active=True)
        except Trigger.DoesNotExist:
            logger.info("Trigger '%s' is inactive or does not exist; skipping.", trigger_code)
            return []

        templates = NotificationTemplate.objects.filter(trigger=trigger, enabled=True)
        rendered_context = build_context(user, context)

        results = []
        for template in templates:
            outcome = cls._dispatch_one(
                trigger=trigger, template=template, user=user, context=rendered_context
            )
            results.append(outcome)
        return results

    @classmethod
    def send_test(cls, *, template: NotificationTemplate, user, test_recipient: str = "") -> dict:
        """
        Used by the "Send Test" admin action. Behaves like a normal
        dispatch but is flagged is_test=True in the log, and lets the
        admin override the recipient (e.g. a test phone/email).
        """
        rendered_context = build_context(user, {})
        return cls._dispatch_one(
            trigger=template.trigger,
            template=template,
            user=user,
            context=rendered_context,
            override_recipient=test_recipient,
            is_test=True,
        )

    @classmethod
    def _dispatch_one(
        cls, *, trigger, template, user, context, override_recipient=None, is_test=False
    ) -> dict:
        channel = template.channel
        rendered_subject = render_template_string(template.subject, context)
        rendered_title = render_template_string(template.title, context)
        rendered_body = render_template_string(template.body, context)

        log = NotificationLog.objects.create(
            user=user,
            trigger=trigger,
            channel=channel,
            template=template,
            status=NotificationStatus.PENDING,
            rendered_subject=rendered_subject,
            rendered_body=rendered_body,
            is_test=is_test,
        )

        try:
            recipient = cls._resolve_recipient(channel, user, override_recipient)
            log.recipient = recipient or ""

            if not recipient:
                log.status = NotificationStatus.SKIPPED
                log.error_message = "No recipient available for this channel (missing contact info or subscription)."
                log.save()
                return {"channel": channel, "status": log.status, "message": log.error_message}

            provider = get_provider_for_channel(channel)
            result = provider.send(
                recipient=recipient,
                subject=rendered_subject,
                title=rendered_title,
                body=rendered_body,
            )

            log.provider_message_id = result.provider_message_id
            log.provider_response = _sanitize_response(result.raw_response)

            if result.success:
                log.status = NotificationStatus.SENT
            else:
                log.status = NotificationStatus.FAILED
                log.error_message = result.error_message or "Provider reported failure."

            log.save()
            return {"channel": channel, "status": log.status, "message": log.error_message}

        except ConfigurationError as exc:
            log.status = NotificationStatus.FAILED
            log.error_message = str(exc)
            log.save()
            logger.warning("Notification channel %s not configured: %s", channel, exc)
            return {"channel": channel, "status": log.status, "message": log.error_message}

        except Exception as exc:  # noqa: BLE001 - isolate provider failures per channel
            log.status = NotificationStatus.FAILED
            log.error_message = "Unexpected error while sending notification."
            log.save()
            logger.exception("Unexpected error dispatching %s notification: %s", channel, exc)
            return {"channel": channel, "status": log.status, "message": log.error_message}

    @staticmethod
    def _resolve_recipient(channel, user, override_recipient):
        if override_recipient:
            return override_recipient

        if channel == Channel.WEB_PUSH:
            subscription = (
                user.webpush_subscriptions.filter(is_active=True).order_by("-created_at").first()
                if user and user.is_authenticated
                else None
            )
            return subscription.external_subscription_id if subscription else ""

        return resolve_recipient(channel, user)


def _sanitize_response(raw_response: dict) -> dict:
    """Strips any accidental secret-looking keys before persisting provider responses."""
    if not isinstance(raw_response, dict):
        return {}
    blocked_keys = {"authorization", "access_token", "token", "api_key", "rest_api_key"}
    return {k: v for k, v in raw_response.items() if k.lower() not in blocked_keys}
