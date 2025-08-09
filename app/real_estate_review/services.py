from typing import Dict

from rest_framework import serializers
from django.http.request import QueryDict
from django.contrib.auth.models import User

from common.errors.errors import SerializationError, DeserializationError
from real_estate_review.errors import InvalidRealEstateReviewIdError

from radar.models import RadarRealEstate
from radar.errors import InvalidRadarRealEstateIdError
from real_estate_review.models import RadarRealEstateReview


def deserialize_create_real_estate_review(
    serializer: serializers.Serializer, data: QueryDict
) -> Dict:
    """Deserialize request and adapt to model fields"""

    data_in = serializer(data=data)
    if not data_in.is_valid():
        raise DeserializationError(data_in.errors)

    data_in_validated = data_in.validated_data

    real_estate_review_dict = {
        "radar_real_estate": data_in_validated.get("radar_real_estate"),
        "rating": data_in_validated.get("rating"),
        "good_tags": data_in_validated.get("good_tags", []),
        "bad_tags": data_in_validated.get("bad_tags", []),
        "user_notes": data_in_validated.get("user_notes"),
    }

    return real_estate_review_dict


def serialize_create_real_estate_review(
    serializer: serializers.Serializer, real_estate_review: RadarRealEstateReview
) -> Dict:
    """Serialize response from model"""
    data_out_dict = {"id": real_estate_review.id}

    data_out = serializer(data=data_out_dict)
    if not data_out.is_valid():
        raise SerializationError(data_out.errors)

    return data_out.validated_data


def create_real_estate_review(user: User, data: Dict) -> RadarRealEstateReview:
    """Create real estate review object in the database"""
    radar_real_estate_id = data.get("radar_real_estate")
    try:
        radar_real_estate = RadarRealEstate.objects.get(id=radar_real_estate_id)
    except RadarRealEstate.DoesNotExist:
        print(f"Radar real estate ID {radar_real_estate_id} does not exist")
        raise InvalidRadarRealEstateIdError

    if radar_real_estate.radar.created_by != user:
        print(
            f"Radar real estate ID {radar_real_estate_id} is not owned by {user.email}"
        )
        raise InvalidRadarRealEstateIdError

    real_estate_review_obj = RadarRealEstateReview.objects.create(
        created_by=user,
        radar_real_estate=radar_real_estate,
        preference=radar_real_estate.preference,
        rating=data.get("rating"),
        good_tags=data.get("good_tags"),
        bad_tags=data.get("bad_tags"),
        user_notes=data.get("user_notes"),
    )

    return real_estate_review_obj


def deserialize_update_real_estate_review(
    serializer: serializers.Serializer, data: QueryDict
) -> Dict:
    """Deserialize request and adapt to model fields"""

    data_in = serializer(data=data)
    if not data_in.is_valid():
        raise DeserializationError(data_in.errors)

    data_in_validated = data_in.validated_data

    real_estate_review_dict = {}

    if data_in_validated.get("rating", None):
        real_estate_review_dict["rating"] = data_in_validated.get("rating")

    if data_in_validated.get("good_tags", None):
        real_estate_review_dict["good_tags"] = data_in_validated.get("good_tags")

    if data_in_validated.get("bad_tags", None):
        real_estate_review_dict["bad_tags"] = data_in_validated.get("bad_tags")

    if data_in_validated.get("user_notes", None):
        real_estate_review_dict["user_notes"] = data_in_validated.get("user_notes")

    return real_estate_review_dict


def serialize_update_real_estate_review(
    serializer: serializers.Serializer, real_estate_review: RadarRealEstateReview
) -> Dict:
    """Serialize response from model"""
    data_out_dict = {"id": real_estate_review.id}

    data_out = serializer(data=data_out_dict)
    if not data_out.is_valid():
        raise SerializationError(data_out.errors)

    return data_out.validated_data


def update_real_estate_review(
    user: User, real_estate_review_id: str, data: Dict
) -> RadarRealEstateReview:
    """Update real estate review object in the database"""

    try:
        real_estate_review_obj = RadarRealEstateReview.objects.get(
            id=real_estate_review_id
        )
    except RadarRealEstateReview.DoesNotExist:
        print(f"Real estate review ID {real_estate_review_id} does not exist")
        raise InvalidRealEstateReviewIdError

    if real_estate_review_obj.created_by != user:
        print(
            f"Real estate review ID {real_estate_review_id} is not owned by {user.email} to be updated"
        )
        raise InvalidRealEstateReviewIdError

    updated_fields = []

    if data.get("rating", None):
        real_estate_review_obj.rating = data.get("rating")
        updated_fields.append("rating")

    if data.get("good_tags", None):
        real_estate_review_obj.good_tags = data.get("good_tags")
        updated_fields.append("good_tags")

    if data.get("bad_tags", None):
        real_estate_review_obj.bad_tags = data.get("bad_tags")
        updated_fields.append("bad_tags")

    if data.get("user_notes", None):
        real_estate_review_obj.user_notes = data.get("user_notes")
        updated_fields.append("user_notes")

    real_estate_review_obj.save(update_fields=updated_fields)
    return real_estate_review_obj
