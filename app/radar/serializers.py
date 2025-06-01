from rest_framework import serializers

from radar.models import Radar


class RadarCreateSerializer(serializers.Serializer):
    """Used to create Radars"""

    name = serializers.CharField(max_length=255)
    search = serializers.UUIDField()


class RadarRetrieveSerializer(serializers.Serializer):
    """Used to retrieve Radars"""

    id = serializers.UUIDField()
    name = serializers.CharField()


class RadarUpdateSerializer(serializers.ModelSerializer):
    """Used to update Radars"""

    class Meta:
        model = Radar
        fields = ["name"]
