"""
Serializers for search API
"""

from rest_framework import serializers
from common.pagination.serializers import PaginationSerializer

from search.models import Search, Filter
from real_estate.models import RealEstate


class SearchCreateSerializer(serializers.Serializer):
    """Serializer for request to create search"""

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
    bedroom_quantity = serializers.IntegerField(min_value=0)
    suite_quantity = serializers.IntegerField(min_value=0)
    bathroom_quantity = serializers.IntegerField(min_value=0)
    garage_slots_quantity = serializers.IntegerField(min_value=0)
    min_price = serializers.FloatField(min_value=0.0)
    max_price = serializers.FloatField(min_value=0.0)
    min_area = serializers.FloatField(min_value=0.0)
    max_area = serializers.FloatField(min_value=0.0)


class SearchRetrieveSerializer(serializers.Serializer):
    """Serializer for get Search objects"""

    id = serializers.UUIDField()
    query_status = serializers.ChoiceField(choices=Search.QueryStatus)
    number_real_estate_found = serializers.IntegerField(min_value=0)
    filter = SearchCreateSerializer()

class SearchListSerializer(PaginationSerializer):
    """Serializer for list Search objects"""
    data = SearchRetrieveSerializer(many=True)
