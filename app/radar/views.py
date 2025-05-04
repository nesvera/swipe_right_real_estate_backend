from django.db.models.query import QuerySet

from rest_framework import mixins, status, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from rest_framework_simplejwt import authentication

from user.models import User
from radar.models import Radar

from radar.serializers import (
    RadarCreateSerializer,
    RadarRetrieveSerialier,
    RadarUpdateSerializer,
)


class RadarView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """View used to interact with Radars models"""

    serializer_class = RadarRetrieveSerialier
    queryset = Radar.objects.none()
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # try to use the following authentication approach for checking ownership
    # class IsOwnerOrReadOnly(permissions.BasePermission):

    def get_serializer_class(self) -> ModelSerializer:
        if self.action == "create":
            return RadarCreateSerializer
        elif self.action == "update":
            return RadarUpdateSerializer
        else:
            return RadarRetrieveSerialier
