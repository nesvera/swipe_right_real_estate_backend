from django.urls import path

from radar.views import RadarView, RadarRealEstateView, RadarRealEstateListView

app_name = "radar"

urlpatterns = [
    path(
        "radar/v1/radar",
        RadarView.as_view({"get": "list", "post": "create"}),
        name="radar",
    ),
    path(
        "radar/v1/radar/<str:id>",
        RadarView.as_view(
            {
                "get": "retrieve",
                "delete": "destroy",
            }
        ),
        name="radar-id",
    ),
    path(
        "radar/v1/radar/<str:id>/real-estate",
        RadarRealEstateListView.as_view({"get": "list"}),
        name="radar-real-estate-list",
    ),
    path(
        "radar/v1/real-estate/<str:id>",
        RadarRealEstateView.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
            }
        ),
        name="radar-real-estate",
    ),
]
