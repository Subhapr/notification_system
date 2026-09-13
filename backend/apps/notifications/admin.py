from django.contrib import admin

from apps.notifications.models import (
    NotificationLog,
    NotificationTemplate,
    Trigger,
    WebPushSubscription,
)


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active", "updated_at"]
    search_fields = ["code", "name"]


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["trigger", "channel", "name", "enabled", "updated_at"]
    list_filter = ["channel", "enabled"]
    search_fields = ["name", "trigger__code"]


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "channel", "recipient", "status", "trigger", "is_test"]
    list_filter = ["channel", "status", "is_test"]
    search_fields = ["recipient", "provider_message_id"]
    readonly_fields = [f.name for f in NotificationLog._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(WebPushSubscription)
class WebPushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "external_subscription_id", "is_active", "created_at"]
    list_filter = ["is_active"]
