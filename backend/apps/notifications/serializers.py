from rest_framework import serializers

from apps.notifications.models import (
    NotificationLog,
    NotificationTemplate,
    Trigger,
    WebPushSubscription,
)
from services.notification_engine.provider_registry import get_provider_for_channel
from services.notification_engine.variables import available_variables_for


class TriggerSerializer(serializers.ModelSerializer):
    available_variables = serializers.SerializerMethodField()

    class Meta:
        model = Trigger
        fields = [
            "id",
            "name",
            "code",
            "description",
            "is_active",
            "available_variables",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_available_variables(self, obj):
        return available_variables_for(obj.code)

    def validate_code(self, value):
        return value.strip().upper().replace(" ", "_")


class NotificationTemplateSerializer(serializers.ModelSerializer):
    trigger_code = serializers.CharField(source="trigger.code", read_only=True)
    trigger_name = serializers.CharField(source="trigger.name", read_only=True)
    is_provider_configured = serializers.SerializerMethodField()

    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "trigger",
            "trigger_code",
            "trigger_name",
            "channel",
            "name",
            "subject",
            "title",
            "body",
            "enabled",
            "variable_mapping",
            "is_provider_configured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_is_provider_configured(self, obj):
        try:
            return get_provider_for_channel(obj.channel).is_configured()
        except Exception:
            return False

    def validate(self, attrs):
        channel = attrs.get("channel", getattr(self.instance, "channel", None))
        if channel == "EMAIL" and not attrs.get("subject", getattr(self.instance, "subject", "")):
            raise serializers.ValidationError({"subject": "Email templates require a subject."})
        return attrs


class NotificationLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True, default="")
    trigger_code = serializers.CharField(source="trigger.code", read_only=True, default="")

    class Meta:
        model = NotificationLog
        fields = [
            "id",
            "user",
            "user_email",
            "trigger",
            "trigger_code",
            "channel",
            "template",
            "status",
            "recipient",
            "rendered_subject",
            "provider_message_id",
            "provider_response",
            "error_message",
            "is_test",
            "created_at",
        ]
        read_only_fields = fields


class TestSendSerializer(serializers.Serializer):
    test_recipient = serializers.CharField(required=False, allow_blank=True)


class WebPushSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebPushSubscription
        fields = ["external_subscription_id", "browser", "device_metadata"]

    def create(self, validated_data):
        user = self.context["request"].user
        subscription, _ = WebPushSubscription.objects.update_or_create(
            external_subscription_id=validated_data["external_subscription_id"],
            defaults={
                "user": user,
                "browser": validated_data.get("browser", ""),
                "device_metadata": validated_data.get("device_metadata", {}),
                "is_active": True,
            },
        )
        return subscription
