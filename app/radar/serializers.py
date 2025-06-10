from rest_framework import serializers

from radar.models import RadarRealEstate

from common.pagination.serializers import PaginationSerializer
from search.serializers import FilterRetrieveSerializer


class RadarCreateSerializer(serializers.Serializer):
    """Used to create Radars"""

    name = serializers.CharField(max_length=255)
    search = serializers.UUIDField()


class RadarRetrieveRealEstateSerializer(serializers.Serializer):
    """Information about real estate related to a radar"""

    like_count = serializers.IntegerField()
    dislike_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    added_count = serializers.IntegerField()
    removed_count = serializers.IntegerField()


class RadarRetrieveSerializer(serializers.Serializer):
    """Used to retrieve Radars"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    real_estate = RadarRetrieveRealEstateSerializer()
    filter = FilterRetrieveSerializer()


class RadarListItemSerializer(serializers.Serializer):
    """Used to retrieve Radars"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    filter = FilterRetrieveSerializer()


class RadarListSerializer(PaginationSerializer):
    """Used to list Radars"""

    data = RadarListItemSerializer(many=True)


class RadarRealEstateListItemSerializer(serializers.Serializer):
    """Item inside the list of real estates from a radar"""

    id = serializers.UUIDField()


class RadarRealEstateListSerializer(PaginationSerializer):
    """Used to list real estates from a radar"""

    data = RadarRealEstateListItemSerializer(many=True)


class RadarRealEstateListParamsSerializer(serializers.Serializer):
    preference = serializers.ChoiceField(
        choices=RadarRealEstate.Preference, required=False
    )


class RadarRealEstateRetrieveSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    preference = serializers.ChoiceField(choices=RadarRealEstate.Preference)


class RadarRealEstateUpdateSerializer(serializers.Serializer):
    preference = serializers.ChoiceField(choices=RadarRealEstate.Preference)
