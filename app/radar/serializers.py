from rest_framework import serializers

from radar.models import Radar

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


class RadarUpdateSerializer(serializers.ModelSerializer):
    """Used to update Radars"""

    class Meta:
        model = Radar
        fields = ["name"]
