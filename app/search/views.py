from django.db.models.query import QuerySet
from django.contrib.auth.models import AnonymousUser

from rest_framework import mixins, status, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from rest_framework_simplejwt import authentication

from search.models import Filter, Search
from search.serializers import (
    SearchCreateSerializer,
    SearchRetrieveSerializer,
    SearchListSerializer,
    SearchResultListSerializer,
)
from search import services

from common.errors.errors import SerializationError, DeserializationError


class SearchView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """View used to handle real estate searches"""

    serializer_class = None
    queryset = Search.objects.none()
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    # TODO - how to allow unauthenticated, and authenticated to access it?
    # TODO - the filter model has a key for user, how to handle it?
    # TODO - if user is not authenticated, how can the website display the last filters user queried?

    # TODO - need to understand better what is the purpose of it
    def get_serializer_class(self):
        if self.action == "create":
            return SearchCreateSerializer
        elif self.action == "list":
            return SearchListSerializer
        elif self.action == "retrieve":
            return SearchRetrieveSerializer
        else:
            return SearchRetrieveSerializer

    def get_queryset(self) -> QuerySet:
        return self.queryset

    def create(self, request: Request) -> Response:
        # TODO - think in a way to abstract serialization/deserialization
        try:
            data_in = services.deserialize_create_search(request.data)
        except DeserializationError as e:
            print(
                f"Fail to deserialize input data for create search. Error: {e.errors}"
            )
            return Response(e.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            search_obj = services.create_search(request.user, data_in)
        except Exception as e:
            print(f"Failed to create search. Error: {e}")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response = services.serialize_create_search(search_obj)
        except SerializationError as e:
            print(f"Failed to serialize create search response. Error: {e.errors}")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_201_CREATED)

    # TODO - improve pagination - query ?page=2&limit=50
    # TODO - improve pagination with sorting ?sort=created_at or ?order=desc

    def list(self, request: Request) -> Response:
        # TODO - missing pagination handling
        try:
            search_queryset = services.list_search(request.user)
        except Exception as e:
            print(f"Failed to list search. Error: {e}")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response = services.serialize_list_search(search_queryset)
        except SerializationError as e:
            print(f"Failed to serialize list search response. Error: {e.errors}")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, id: str) -> Response:
        try:
            search_obj = services.get_search(id)
        except Search.DoesNotExist:
            print(f"Failed to find search {id}")
            return Response("", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Failed to get search {id}. Error: {e}")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response = services.serialize_retrieve_search(search_obj)
        except SerializationError as e:
            print(f"Failed to serialize retrieve search response. Error: {e.errors}")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_200_OK)

    def partial_update(self, request: Request, pk=None) -> Response:
        return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchResultView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """View used to return list o real estate related to a search"""

    serializer_class = None
    queryset = QuerySet.none
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        return SearchResultListSerializer

    def list(self, request: Request, id: str) -> Response:
        # TODO - missing pagination handling
        try:
            search_queryset = services.list_search_result(id)
        except Exception as e:
            print(f"Failed to list search results. Error: {e}")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response = services.serialize_search_result(search_queryset)
        except SerializationError as e:
            print(
                f"Failed to serialize list search results response. Error: {e.errors}"
            )
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_200_OK)
