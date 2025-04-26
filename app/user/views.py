"""
Views for user API.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageMyUserView(generics.RetrieveUpdateAPIView):
    """Manage logged user."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class CreateUser(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, format=None):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        get_user_model().objects.create_user(**serializer.validated_data)
        return Response("", status.HTTP_201_CREATED)
