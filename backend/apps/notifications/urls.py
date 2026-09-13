from rest_framework.routers import DefaultRouter

from django.urls import include, path

from apps.notifications.views import (
    NotificationLogViewSet,
    NotificationTemplateViewSet,
    ProviderConfigStatusView,
    TriggerViewSet,
    WebPushSubscribeView,
    WebPushUnsubscribeView,
)

router = DefaultRouter()
router.register(r"triggers", TriggerViewSet, basename="trigger")
router.register(r"notification-templates", NotificationTemplateViewSet, basename="notification-template")
router.register(r"notifications/logs", NotificationLogViewSet, basename="notification-log")

urlpatterns = [
    path("", include(router.urls)),
    path("config-status/", ProviderConfigStatusView.as_view(), name="config-status"),
    path("webpush/subscribe/", WebPushSubscribeView.as_view(), name="webpush-subscribe"),
    path("webpush/unsubscribe/", WebPushUnsubscribeView.as_view(), name="webpush-unsubscribe"),
]
