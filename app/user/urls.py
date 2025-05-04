"""
URL mappings for user API.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user import views

app_name = "user"

urlpatterns = [
    path("user/v1/create", views.CreateUser.as_view(), name="create"),
    path("user/v1/token", TokenObtainPairView.as_view(), name="auth"),
    path("user/v1/token/refresh", TokenRefreshView.as_view(), name="refresh"),
    path(
        "user/v1/user",
        views.ManageUserView.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
            }
        ),
        name="user_info",
    ),
]
