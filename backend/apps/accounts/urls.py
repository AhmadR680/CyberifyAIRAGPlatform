from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ProfileView, RegisterView


class PublicTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]


class PublicTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


urlpatterns = [
    path("register/",RegisterView.as_view(),name="register"),

    path("login/",PublicTokenObtainPairView.as_view(),name="login"),

    path("refresh/",PublicTokenRefreshView.as_view(),name="refresh"),

    path("me/",ProfileView.as_view(),name="profile"),
]