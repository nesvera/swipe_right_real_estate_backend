from django.urls import path

from search.views import SearchView, SearchResultView

app_name = "search"

urlpatterns = [
    # TODO - probably list is not necessary anymore since user should use only radar
    path(
        "search/v1/search",
        SearchView.as_view({"get": "list", "post": "create"}),
        name="search",
    ),
    # TODO - probably not necessary anymore since user will not know about search elements, only radar
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
