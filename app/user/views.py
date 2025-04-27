"""
Views for user API.
"""

from django.contrib.auth import get_user_model
from rest_framework import permissions, mixins, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication
from rest_framework.serializers import ModelSerializer

from user.serializers import (
    UserSerializer,
    UserUpdateSerializer,
    UserPartialUpdateSerializer,
    AuthTokenSerializer,
)
from user.utils import validate_password


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """Manage logged user."""

    serializer_class = UserSerializer
    queryset = get_user_model().objects.none()
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> ModelSerializer:
        """Overwrite get_serializer_class"""
        if self.action == "update":
            return UserUpdateSerializer
        elif self.action == "partial_update":
            return UserPartialUpdateSerializer
        else:
            return self.serializer_class

    def retrieve(self, request: Request, pk=None) -> Response:
        request_user = request.user

        user_obj = get_user_model().objects.get(id=request_user.id)

        out_serializer = UserSerializer(user_obj)
        return Response(out_serializer.data, status=status.HTTP_200_OK)

    def update(self, request: Request, pk=None) -> Response:
        request_user = request.user
        if request_user is None:
            return Response("User not found", status=status.HTTP_400_BAD_REQUEST)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        request_data = serializer.validated_data
        new_password = request_data.pop("password")

        is_password_valid = validate_password(new_password)
        if not is_password_valid:
            return Response(
                "Password does not meet security requirements",
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_obj = get_user_model().objects.get(id=request_user.id)
        user_obj.set_password(new_password)
        user_obj.save()

        user_obj_filter = get_user_model().objects.filter(id=request_user.id)
        user_obj_filter.update(**request_data)

        out_serializer = UserSerializer(user_obj)
        return Response(out_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request: Request, pk=None) -> Response:
        request_user = request.user
        if request_user is None:
            return Response("User not found", status=status.HTTP_400_BAD_REQUEST)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        request_data = serializer.validated_data
        new_password = request_data.pop("password", None)

        user_obj = get_user_model().objects.get(id=request_user.id)

        if new_password is not None:
            is_password_valid = validate_password(new_password)
            if not is_password_valid:
                return Response(
                    "Password does not meet security requirements",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_obj.set_password(new_password)
            user_obj.save()

        user_obj_filter = get_user_model().objects.filter(id=request_user.id)
        user_obj_filter.update(**request_data)

        out_serializer = UserSerializer(user_obj)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class CreateUser(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, format=None) -> Response:
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        is_password_valid = validate_password(serializer.validated_data.get("password"))
        if not is_password_valid:
            return Response(
                "Password does not meet security requirements",
                status=status.HTTP_400_BAD_REQUEST,
            )

        get_user_model().objects.create_user(**serializer.validated_data)
        return Response("", status.HTTP_201_CREATED)
