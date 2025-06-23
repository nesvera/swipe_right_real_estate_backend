from rest_framework import serializers

from radar.models import RadarRealEstate
from real_estate.models import RealEstate

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
    property_type = serializers.ChoiceField(choices=RealEstate.PropertyType)
    transaction_type = serializers.ChoiceField(choices=RealEstate.TransactionType)
    city = serializers.CharField(max_length=100)
    neighborhood = serializers.CharField(max_length=100)
    bedroom_quantity = serializers.IntegerField(min_value=0)
    suite_quantity = serializers.IntegerField(min_value=0)
    garage_slots_quantity = serializers.IntegerField(min_value=0)
    price = serializers.FloatField(min_value=0.0)
    condo_price = serializers.FloatField(min_value=0.0)
    area = serializers.FloatField(min_value=0.0)
    area_total = serializers.FloatField(min_value=0.0)
    thumb_urls = serializers.ListField(child=serializers.CharField(max_length=500))


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
