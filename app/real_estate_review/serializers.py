from rest_framework import serializers

from real_estate_review.models import RadarRealEstateReview


class RealEstateReviewCreateSerializer(serializers.Serializer):
    """Request payload to create real estate review"""

    radar_real_estate = serializers.UUIDField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    good_tags = serializers.ListField(
        child=serializers.ChoiceField(choices=RadarRealEstateReview.Tags),
        min_length=0,
        max_length=10,
        allow_empty=True,
        required=False,
    )
    bad_tags = serializers.ListField(
        child=serializers.ChoiceField(choices=RadarRealEstateReview.Tags),
        min_length=0,
        max_length=10,
        allow_empty=True,
        required=False,
    )
    user_notes = serializers.CharField(max_length=250, allow_blank=True)


class RealEstateReviewCreateResponseSerializer(serializers.Serializer):
    """Response payload from create real estate review"""

    id = serializers.UUIDField()


class RealEstateReviewUpdateSerializer(serializers.Serializer):
    """Request payload to update real estate review"""

    rating = serializers.IntegerField(min_value=1, max_value=5)
    good_tags = serializers.ListField(
        child=serializers.ChoiceField(choices=RadarRealEstateReview.Tags),
        min_length=0,
        max_length=10,
        allow_empty=True,
        required=False,
    )
    bad_tags = serializers.ListField(
        child=serializers.ChoiceField(choices=RadarRealEstateReview.Tags),
        min_length=0,
        max_length=10,
        allow_empty=True,
        required=False,
    )
    user_notes = serializers.CharField(max_length=250, allow_blank=True)


class RealEstateReviewUpdateResponseSerializer(serializers.Serializer):
    """Response payload from update real estate review"""

    id = serializers.UUIDField()
