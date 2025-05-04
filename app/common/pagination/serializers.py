from rest_framework import serializers


class PaginationMetadataSerializer(serializers.Serializer):
    """Serializer for pagination metadata"""

    total = serializers.IntegerField(min_value=0)
    page = serializers.IntegerField(min_value=0)
    per_page = serializers.IntegerField(min_value=0)
    total_pages = serializers.IntegerField(min_value=0)


class PaginationSerializer(serializers.Serializer):
    """Serializer for list Search objects"""

    data = None
    meta = PaginationMetadataSerializer()
