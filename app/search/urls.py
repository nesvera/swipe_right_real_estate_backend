from django.urls import path

from search.views import SearchView, SearchResultView

app_name = "search"

urlpatterns = [
    path(
        "search/v1/search",
        SearchView.as_view({"get": "list", "post": "create"}),
        name="search",
    ),
    path(
        "search/v1/search/<str:id>",
        SearchView.as_view({"get": "retrieve", "patch": "partial_update"}),
        name="search-pk",
    ),
    path(
        "search/v1/search/<str:id>/result",
        SearchResultView.as_view({"get": "list"}),
        name="search-pk-result",
    ),
]
