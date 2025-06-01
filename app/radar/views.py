from django.db.models.query import QuerySet

from rest_framework import mixins, status, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from rest_framework_simplejwt import authentication

from user.models import User
from radar.models import Radar, RadarRealEstate

from radar.serializers import (
    RadarCreateSerializer,
    RadarRetrieveSerialier,
    RadarUpdateSerializer,
)


class RadarView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """View used to interact with Radars models such as create, delete, list, and get its info"""

    serializer_class = RadarRetrieveSerialier
    queryset = Radar.objects.none()
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> ModelSerializer:
        return None
        if self.action == "create":
            return RadarCreateSerializer
        else:
            return RadarRetrieveSerialier


class RadarRealEstateListView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """View used to list real estates related to a Radar"""

    serializer_class = RadarRetrieveSerialier
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

    serializer_class = RadarRetrieveSerialier
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
