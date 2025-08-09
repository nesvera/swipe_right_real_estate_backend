from rest_framework import mixins, status, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt import authentication
from drf_spectacular.utils import extend_schema

from common.errors.errors import DeserializationError, SerializationError
from radar.errors import InvalidRadarRealEstateIdError
from real_estate_review.errors import InvalidRealEstateReviewIdError

from real_estate_review.serializers import (
    RealEstateReviewCreateSerializer,
    RealEstateReviewCreateResponseSerializer,
    RealEstateReviewUpdateSerializer,
    RealEstateReviewUpdateResponseSerializer,
)
from real_estate_review.models import RadarRealEstateReview

from real_estate_review.services import (
    deserialize_create_real_estate_review,
    create_real_estate_review,
    serialize_create_real_estate_review,
    deserialize_update_real_estate_review,
    serialize_update_real_estate_review,
    update_real_estate_review,
)


class RealEstateReviewView(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """Used to create, and update real estate review model"""

    serializer_class = None
    queryset = RadarRealEstateReview.objects.none()
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> ModelSerializer:
        return RealEstateReviewCreateSerializer

    @extend_schema(
        request=RealEstateReviewCreateSerializer,
        responses=RealEstateReviewCreateResponseSerializer,
    )
    def create(self, request: Request) -> Response:
        try:
            data_in = deserialize_create_real_estate_review(
                RealEstateReviewCreateSerializer, request.data
            )
        except DeserializationError as e:
            print(
                f"Failed to deserialize payload while creating real estate review. Error: {e.errors}"
            )
            return Response(e.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            real_estate_review_obj = create_real_estate_review(request.user, data_in)
        except InvalidRadarRealEstateIdError:
            return Response(
                "Invalid radar real estate ID", status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = serialize_create_real_estate_review(
                RealEstateReviewCreateResponseSerializer, real_estate_review_obj
            )
        except SerializationError as e:
            print(
                f"Failed to serialize response while creating real estate review. Error: {e.errors}"
            )
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_201_CREATED)

    def partial_update(self, request: Request, id: str) -> Response:
        try:
            data_in = deserialize_update_real_estate_review(
                RealEstateReviewUpdateSerializer, request.data
            )
        except DeserializationError as e:
            print(
                f"Failed to deserialize payload while updating real estate review. Error: {e.errors}"
            )
            return Response(e.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            real_estate_review_obj = update_real_estate_review(
                request.user, id, data_in
            )
        except InvalidRealEstateReviewIdError:
            return Response(
                "Invalid real estate review ID", status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = serialize_update_real_estate_review(
                RealEstateReviewCreateResponseSerializer, real_estate_review_obj
            )
        except SerializationError as e:
            print(
                f"Failed to serialize response while creating real estate review. Error: {e.errors}"
            )
            return Response("", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_200_OK)
