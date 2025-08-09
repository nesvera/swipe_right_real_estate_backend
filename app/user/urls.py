"""
URL mappings for user API.
"""

from django.urls import path

from user import views

app_name = "user"

urlpatterns = [
    path("user/v1/create", views.CreateUser.as_view(), name="create"),
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
