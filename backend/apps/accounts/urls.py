from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import LoginView, LogoutView, MeView, RefreshView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("", include(router.urls)),
]
