from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """
    Only staff/admin users may access notification management endpoints.
    Regular users are limited to their own account endpoints.
    """

    message = "You do not have permission to manage notifications."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
