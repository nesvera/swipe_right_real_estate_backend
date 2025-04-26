"""
Serializers for the user API view.
"""

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object."""

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ["id"]


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"), username=email, password=password
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
