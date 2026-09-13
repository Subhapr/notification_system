import logging

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsStaffUser
from apps.core.responses import error_response, success_response
from apps.core.viewsets import EnvelopeModelViewSet, EnvelopeReadOnlyModelViewSet
from apps.notifications.filters import NotificationLogFilter
from apps.notifications.models import NotificationLog, NotificationTemplate, Trigger
from apps.notifications.serializers import (
    NotificationLogSerializer,
    NotificationTemplateSerializer,
    TestSendSerializer,
    TriggerSerializer,
    WebPushSubscribeSerializer,
)
from services.notification_engine.engine import NotificationEngine

logger = logging.getLogger("notifications")


class TriggerViewSet(EnvelopeModelViewSet):
    """
    Admin-only CRUD for triggers. Creating a trigger here is all that
    is needed to make it usable by NotificationEngine.fire(code=...)
    elsewhere in the codebase.
    """

    queryset = Trigger.objects.all()
    serializer_class = TriggerSerializer
    permission_classes = [IsStaffUser]


class NotificationTemplateViewSet(EnvelopeModelViewSet):
    """
    Admin-only CRUD for templates, plus `toggle` and `test` actions
    that power the Notification Settings matrix on the frontend.
    """

    queryset = NotificationTemplate.objects.select_related("trigger").all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        qs = super().get_queryset()
        trigger_code = self.request.query_params.get("trigger")
        if trigger_code:
            qs = qs.filter(trigger__code__iexact=trigger_code)
        return qs

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        template = self.get_object()
        template.enabled = not template.enabled
        template.save(update_fields=["enabled", "updated_at"])
        return success_response(
            data=NotificationTemplateSerializer(template).data,
            message=f"Template {'enabled' if template.enabled else 'disabled'}.",
        )

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        template = self.get_object()
        serializer = TestSendSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid test request.", errors=serializer.errors)

        test_recipient = serializer.validated_data.get("test_recipient", "")
        result = NotificationEngine.send_test(
            template=template, user=request.user, test_recipient=test_recipient
        )

        if result["status"] == "SENT":
            return success_response(data=result, message="Test notification sent.")
        return error_response(
            message=result.get("message") or "Test notification failed.",
            errors={"result": result},
            status=422,
        )


class NotificationLogViewSet(EnvelopeReadOnlyModelViewSet):
    """Admin-only, read-only audit trail with filtering for the Logs page."""

    queryset = NotificationLog.objects.select_related("user", "trigger", "template").all()
    serializer_class = NotificationLogSerializer
    permission_classes = [IsStaffUser]
    filterset_class = NotificationLogFilter


class ProviderConfigStatusView(APIView):
    """
    Admin-only summary of which providers currently have credentials
    configured, so the Settings page can show real status without
    ever exposing the credentials themselves.
    """

    permission_classes = [IsStaffUser]

    def get(self, request):
        from services.notification_engine.provider_registry import get_provider_for_channel
        from apps.notifications.models import Channel

        status = {}
        for channel in Channel.values:
            try:
                status[channel] = get_provider_for_channel(channel).is_configured()
            except Exception:
                status[channel] = False
        return success_response(data=status)


class WebPushSubscribeView(APIView):
    """
    Any authenticated user's browser can register itself for Web Push.
    This is called by the frontend after the visitor grants
    notification permission - admins never type a subscription id in
    by hand.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WebPushSubscribeSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error_response(message="Unable to register subscription.", errors=serializer.errors)
        subscription = serializer.save()
        return success_response(
            data={"id": subscription.id, "external_subscription_id": subscription.external_subscription_id},
            message="Browser subscribed for Web Push notifications.",
        )


class WebPushUnsubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        external_id = request.data.get("external_subscription_id")
        if not external_id:
            return error_response(message="external_subscription_id is required.", status=400)

        updated = request.user.webpush_subscriptions.filter(
            external_subscription_id=external_id
        ).update(is_active=False)

        if not updated:
            return error_response(message="Subscription not found.", status=404)
        return success_response(message="Unsubscribed from Web Push notifications.")
