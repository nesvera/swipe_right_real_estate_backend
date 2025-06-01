from typing import Dict

from rest_framework import serializers
from django.http.request import QueryDict

from common.errors.errors import SerializationError, DeserializationError

from user.models import User
from radar.models import Radar
from search.models import Search


def deserializer_create_radar(
    serializer: serializers.Serializer, data: QueryDict
) -> Dict:
    data_in = serializer(data=data)
    if not data_in.is_valid():
        raise DeserializationError(data_in.errors)

    data_in_validated = data_in.validated_data

    radar_dict = {
        "name": data_in_validated.get("name"),
        "search": data_in_validated.get("search"),
    }

    return radar_dict


def serialize_create_radar(serializer: serializers.Serializer, radar: Radar) -> Dict:
    data_out_dict = {"id": radar.id, "name": radar.name}

    data_out = serializer(data=data_out_dict)
    if not data_out.is_valid():
        raise SerializationError(data_out.errors)

    return data_out.validated_data


class InvalidSearchIdError(Exception):
    pass


def create_radar(user: User, data: Dict) -> Radar:
    """Create radar object"""
    search_id = data.get("search")
    try:
        search_obj = Search.objects.get(id=search_id)
    except Search.DoesNotExist:
        print(f"Search ID {search_id} does not exist.")
        raise InvalidSearchIdError

    # Radar should only refer to search objects owned by the user
    if search_obj.created_by is not None and search_obj.created_by != user:
        raise InvalidSearchIdError

    radar_obj = Radar.objects.create(
        created_by=user, name=data.get("name"), search=search_obj
    )

    return radar_obj
