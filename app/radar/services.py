from typing import Dict, List

from rest_framework import serializers
from django.http.request import QueryDict
from django.db.models.query import QuerySet

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


def list_radar(user: User) -> QuerySet:
    radar_queryset = Radar.objects.filter(created_by=user)

    return radar_queryset


def serialize_list_radar(
    serializer: serializers.Serializer, radars: List[Radar]
) -> List[Dict]:
    # convert radar queryset to paginated list
    radar_list = []
    for radar in radars:
        radar_data = {"id": radar.id, "name": radar.name}

        radar_list.append(radar_data)

    list_response_dict = {
        "data": radar_list,
        "meta": {
            "total": 0,
            "page": 0,
            "per_page": 0,
            "total_pages": 0,
        },
    }

    data_out = serializer(data=list_response_dict)
    if not data_out.is_valid():
        raise SerializationError(data_out.errors)

    return data_out.validated_data


class InvalidRadarIdError(Exception):
    pass


def retrieve_radar(user: User, id: str) -> Radar:
    try:
        radar = Radar.objects.get(id=id)
    except Radar.DoesNotExist:
        raise InvalidRadarIdError(f"Radar ID {id} not found")

    if radar.created_by != user:
        raise InvalidRadarIdError(
            f"Radar ID {id} was not created by other user. User requesting {user.id}"
        )

    return radar


def serialize_retrieve_radar(serializer: serializers.Serializer, radar: Radar) -> Dict:
    data_out_dict = {"id": radar.id, "name": radar.name}

    data_out = serializer(data=data_out_dict)
    if not data_out.is_valid():
        raise SerializationError(data_out.errors)

    return data_out.validated_data
