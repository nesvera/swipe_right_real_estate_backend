from rest_framework import serializers

from radar.models import RadarRealEstate

from common.pagination.serializers import PaginationSerializer


class RadarCreateSerializer(serializers.Serializer):
    """Used to create Radars"""

    name = serializers.CharField(max_length=255)
    search = serializers.UUIDField()


class RadarRetrieveSerializer(serializers.Serializer):
    """Used to retrieve Radars"""

    id = serializers.UUIDField()
    name = serializers.CharField()


class RadarListSerializer(PaginationSerializer):
    """Used to list Radars"""

    data = RadarRetrieveSerializer(many=True)


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
