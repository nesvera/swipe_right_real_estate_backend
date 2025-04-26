""""
URL mappings for user API.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user import views

app_name = "user"

urlpatterns = [
    path("user/v1/create", views.CreateUser.as_view(), name="user"),
    path("user/v1/token", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("user/v1/token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("user/v1/token/verify", TokenVerifyView.as_view(), name="token_verify"),
    path("user/v1/me", views.ManageMyUserView.as_view(), name="me"),
]
