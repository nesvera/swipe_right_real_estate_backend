""""
URL mappings for user API.
"""

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

from user import views

app_name = "user"

user_info_router = DefaultRouter()
user_info_router.register("", views.ManageUserView, basename="user_info")

urlpatterns = [
    path("user/v1/create", views.CreateUser.as_view(), name="create"),
    path("user/v1/token", TokenObtainPairView.as_view(), name="auth"),
    path("user/v1/token/refresh", TokenRefreshView.as_view(), name="refresh"),
    path("user/v1/user", include(user_info_router.urls)),
]
