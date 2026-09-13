import logging

from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.serializers import (
    LoginSerializer,
    LogoutSerializer,
    RefreshSerializer,
    UserSerializer,
)
from apps.core.permissions import IsStaffUser
from apps.core.responses import error_response, success_response
from apps.core.viewsets import EnvelopeReadOnlyModelViewSet
from services.notification_engine.engine import NotificationEngine

logger = logging.getLogger("notifications")


def _issue_tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Unable to log in.",
                errors=serializer.errors,
                status=400,
            )

        user = serializer.validated_data["user"]
        user.last_login_at = timezone.now()
        user.save(update_fields=["last_login_at"])

        tokens = _issue_tokens_for(user)

        # Notification dispatch must never block or break the login
        # response itself - failures are caught and logged internally
        # by the engine, per-channel, and never raised here.
        try:
            NotificationEngine.fire(
                trigger_code="LOGIN",
                user=user,
                context={"login_time": timezone.localtime().strftime("%Y-%m-%d %H:%M")},
            )
        except Exception:  # pragma: no cover - defensive, engine already isolates errors
            logger.exception("Unexpected error firing LOGIN notification")

        return success_response(
            data={"user": UserSerializer(user).data, "tokens": tokens},
            message="Logged in successfully.",
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="A valid refresh token is required to log out.",
                errors=serializer.errors,
                status=400,
            )

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            return error_response(message="Invalid or expired refresh token.", status=400)

        try:
            NotificationEngine.fire(
                trigger_code="LOGOUT",
                user=request.user,
                context={"logout_time": timezone.localtime().strftime("%Y-%m-%d %H:%M")},
            )
        except Exception:  # pragma: no cover
            logger.exception("Unexpected error firing LOGOUT notification")

        return success_response(message="Logged out successfully.")


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="A refresh token is required.",
                errors=serializer.errors,
                status=400,
            )
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            access = str(token.access_token)
        except TokenError:
            return error_response(message="Invalid or expired refresh token.", status=401)

        return success_response(data={"access": access}, message="Token refreshed.")


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(data=UserSerializer(request.user).data)


class UserViewSet(EnvelopeReadOnlyModelViewSet):
    """Admin-only, read-only directory of application users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsStaffUser]
