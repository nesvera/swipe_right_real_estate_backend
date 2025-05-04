from rest_framework import serializers

from radar.models import Radar


class RadarRetrieveSerialier(serializers.ModelSerializer):
    """Used to retrieve Radars"""

    class Meta:
        model = Radar
        fields = ["id", "name"]


class RadarCreateSerializer(serializers.ModelSerializer):
    """Used to create Radars"""

    class Meta:
        model = Radar
        fields = ["name"]


class RadarUpdateSerializer(serializers.ModelSerializer):
    """Used to update Radars"""

    class Meta:
        model = Radar
        fields = ["name"]
