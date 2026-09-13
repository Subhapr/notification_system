import django_filters

from apps.notifications.models import NotificationLog


class NotificationLogFilter(django_filters.FilterSet):
    trigger = django_filters.CharFilter(field_name="trigger__code", lookup_expr="iexact")
    channel = django_filters.CharFilter(field_name="channel", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    date_from = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    date_to = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = NotificationLog
        fields = ["trigger", "channel", "status", "date_from", "date_to"]
