from django.db.models.query import QuerySet

from rest_framework import mixins, status, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from rest_framework_simplejwt import authentication

from user.models import User
from radar.models import Radar, RadarRealEstate
from radar import services

from radar.serializers import (
    RadarCreateSerializer,
    RadarRetrieveSerializer,
    RadarUpdateSerializer,
    RadarListSerializer,
)

from common.errors.errors import SerializationError, DeserializationError


class RadarView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """View used to interact with Radars models such as create, delete, list, and get its info"""

    serializer_class = RadarRetrieveSerializer
    queryset = Radar.objects.none()
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> ModelSerializer:
        if self.action == "create":
            return RadarCreateSerializer
        elif self.action == "list":
            return RadarListSerializer
        else:
            return RadarRetrieveSerializer

    def create(self, request: Request) -> Response:
        try:
            data_in = services.deserializer_create_radar(
                RadarCreateSerializer, request.data
            )
        except DeserializationError as e:
            print(
                f"Failed to deserialize payload while creating radar. Error: {e.errors}"
            )
            return Response(e.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            radar_obj = services.create_radar(request.user, data_in)
        except services.InvalidSearchIdError:
            return Response("Invalid search ID", status=status.HTTP_400_BAD_REQUEST)

        try:
            response = services.serialize_create_radar(
                RadarRetrieveSerializer, radar_obj
            )
        except SerializationError as e:
            print(
                f"Failed to serialize response while creating radar. Error: {e.errors}"
            )
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request: Request) -> Response:
        # TODO - how to handle pagination?
        try:
            radar_queryset = services.list_radar(request.user)
        except Exception as e:
            print(f"Failed to list radars for user {request.user.id}. Error: {e}.")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response = services.serialize_list_radar(
                RadarListSerializer, radar_queryset
            )
        except SerializationError as e:
            print(f"Failed to serializer response while listing radars. Error: {e}.")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, id: str) -> Response:
        try:
            radar = services.retrieve_radar(request.user, id)
        except services.InvalidRadarIdError as e:
            print(f"Failed to retrieve radar. User: {request.user.id}. Error: {e}.")
            return Response("", status=status.HTTP_404_NOT_FOUND)

        try:
            response = services.serialize_retrieve_radar(RadarRetrieveSerializer, radar)
        except Exception as e:
            print(f"Failed to serialize response while retrieve radar. Error: {e}.")
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request: Request, id: str) -> Response:
        try:
            radar = services.retrieve_radar(request.user, id)
        except services.InvalidRadarIdError as e:
            print(f"Failed to retrieve radar. User: {request.user.id}. Error: {e}.")
            return Response("", status=status.HTTP_404_NOT_FOUND)

        radar.delete()

        return Response("", status=status.HTTP_200_OK)


class RadarRealEstateListView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """View used to list real estates related to a Radar"""

    serializer_class = RadarRetrieveSerializer
    queryset = RadarRealEstate.objects.none()
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> ModelSerializer:
        return None
        return RadarRetrieveSerialier


class RadarRealEstateView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """View used to retrieve real estate info, and update assessment from user about it"""

    serializer_class = RadarRetrieveSerializer
    queryset = RadarRealEstate.objects.none()
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> ModelSerializer:
        return None
        if self.action == "retrieve":
            return RadarCreateSerializer
        elif self.action == "update":
            return RadarUpdateSerializer
        else:
            return RadarRetrieveSerialier
