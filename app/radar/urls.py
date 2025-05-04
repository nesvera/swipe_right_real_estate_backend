from django.urls import path

from radar.views import RadarView

app_name = "radar"

urlpatterns = [
    path(
        "radar/v1/radar",
        RadarView.as_view({"get": "list", "post": "create"}),
        name="radar",
    ),
    path(
        "radar/v1/radar/<int:pk>",
        RadarView.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="radar-pk",
    ),
]
