from django.urls import path

from real_estate_review.views import RealEstateReviewView

app_name = "real_estate_review"

urlpatterns = [
    path(
        "realestate/v1/review",
        RealEstateReviewView.as_view({"post": "create"}),
        name="real-estate-review",
    ),
    path(
        "realestate/v1/review/<str:id>",
        RealEstateReviewView.as_view({"patch": "partial_update"}),
        name="real-estate-review-id",
    ),
]
