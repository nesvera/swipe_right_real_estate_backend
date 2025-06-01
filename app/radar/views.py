from django.db.models.query import QuerySet

from rest_framework import mixins, status, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from rest_framework_simplejwt import authentication

from user.models import User
from radar.models import Radar, RadarRealEstate
from radar.services import (
    deserializer_create_radar,
    serialize_create_radar,
    create_radar,
    InvalidSearchIdError,
)

from radar.serializers import (
    RadarCreateSerializer,
    RadarRetrieveSerializer,
    RadarUpdateSerializer,
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
        else:
            return RadarRetrieveSerializer

    def create(self, request: Request) -> Response:
        try:
            data_in = deserializer_create_radar(RadarCreateSerializer, request.data)
        except DeserializationError as e:
            print(
                f"Failed to deserialize payload while creating radar. Error: {e.errors}"
            )
            return Response(e.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            radar_obj = create_radar(request.user, data_in)
        except InvalidSearchIdError:
            return Response("Invalid search ID", status=status.HTTP_400_BAD_REQUEST)

        try:
            response = serialize_create_radar(RadarRetrieveSerializer, radar_obj)
        except SerializationError as e:
            print(
                f"Failed to serialize response while creating radar. Error: {e.errors}"
            )
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request: Request) -> Response:

        return Response("", status=status.HTTP_404_NOT_FOUND)


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
