"""
Serializers for search API
"""

from rest_framework import serializers
from common.pagination.serializers import PaginationSerializer

from search.models import Search
from real_estate.models import RealEstate


class SearchCreateSerializer(serializers.Serializer):
    """Serializer for request to create search"""

    property_type = serializers.ListField(
        child=serializers.ChoiceField(choices=RealEstate.PropertyType),
        allow_empty=False,
    )
    transaction_type = serializers.ListField(
        child=serializers.ChoiceField(choices=RealEstate.TransactionType),
        allow_empty=False,
    )
    city = serializers.ListField(
        child=serializers.CharField(max_length=100), allow_empty=False
    )
    neighborhood = serializers.ListField(
        child=serializers.CharField(max_length=100), allow_empty=False
    )
    bedroom_quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )
    suite_quantity = serializers.ListField(child=serializers.IntegerField(min_value=0))
    bathroom_quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )
    garage_slots_quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )
    min_price = serializers.FloatField(min_value=0.0)
    max_price = serializers.FloatField(min_value=0.0)
    min_area = serializers.FloatField(min_value=0.0)
    max_area = serializers.FloatField(min_value=0.0)


class FilterRetrieveSerializer(serializers.Serializer):
    """Serializer for retrieving information about the filter from a search"""

    # property_type  = serializers.ListField(child=)
    property_type = serializers.ListField(
        child=serializers.ChoiceField(choices=RealEstate.PropertyType),
        allow_empty=False,
    )
    transaction_type = serializers.ListField(
        child=serializers.ChoiceField(choices=RealEstate.TransactionType),
        allow_empty=False,
    )
    city = serializers.ListField(
        child=serializers.CharField(max_length=100), allow_empty=False
    )
    neighborhood = serializers.ListField(
        child=serializers.CharField(max_length=100), allow_empty=False
    )
    bedroom_quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )
    suite_quantity = serializers.ListField(child=serializers.IntegerField(min_value=0))
    bathroom_quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )
    garage_slots_quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )
    min_price = serializers.FloatField(min_value=0.0)
    max_price = serializers.FloatField(min_value=0.0)
    min_area = serializers.FloatField(min_value=0.0)
    max_area = serializers.FloatField(min_value=0.0)


class SearchRetrieveSerializer(serializers.Serializer):
    """Serializer for get Search objects"""

    id = serializers.UUIDField()
    query_status = serializers.ChoiceField(choices=Search.QueryStatus)
    number_real_estate_found = serializers.IntegerField(min_value=0)
    filter = FilterRetrieveSerializer()


class SearchListSerializer(PaginationSerializer):
    """Serializer for list Search objects"""

    data = SearchRetrieveSerializer(many=True)


class SearchResultRealEstateSerializer(serializers.Serializer):
    """Serializer describing a real estate from search result"""

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
    thumb_urls = serializers.ListField(
        child=serializers.CharField(max_length=500), allow_empty=True
    )


class SearchResultListSerializer(PaginationSerializer):
    """Serializer to list real estate related to a search"""

    data = SearchResultRealEstateSerializer(many=True)
