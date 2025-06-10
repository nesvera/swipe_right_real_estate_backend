from typing import Dict, List, Optional
from datetime import datetime, timezone

from rest_framework import serializers
from django.http.request import QueryDict
from django.db.models.query import QuerySet
from django.db.models import Q, Count

from common.errors.errors import SerializationError, DeserializationError

from user.models import User
from radar.models import Radar, RadarRealEstate
from search.models import Search, SearchResultRealEstate
from real_estate.models import RealEstate


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


def get_radar_real_estate_count(radar: Radar) -> Dict:
    # real estate information
    preference_count = RadarRealEstate.objects.values("preference").annotate(
        count=Count("id", filter=Q(radar=radar, removed_at__isnull=True), distinct=True)
    )
    removed_count = RadarRealEstate.objects.filter(
        radar=radar, removed_at__isnull=False
    ).count()

    # TODO - how to define if a real estate is new, or only the user did not see it yet (pending)?

    real_estate_dict = {
        "like_count": 0,
        "dislike_count": 0,
        "pending_count": 0,
        "added_count": 0,
        "removed_count": removed_count,
    }

    for preference in preference_count:
        count = preference.get("count", 0)
        preference_name = preference.get("preference", None)

        if preference_name is None:
            continue
        elif preference_name == RadarRealEstate.Preference.PENDING:
            real_estate_dict["pending_count"] = count
        elif preference_name == RadarRealEstate.Preference.LIKE:
            real_estate_dict["like_count"] = count
        elif preference_name == RadarRealEstate.Preference.DISLIKE:
            real_estate_dict["dislike_count"] = count

    return real_estate_dict


def serialize_create_radar(serializer: serializers.Serializer, radar: Radar) -> Dict:
    search_filter = radar.search.filter

    filter_dict = {
        "property_type": search_filter.property_type,
        "transaction_type": search_filter.transaction_type,
        "city": search_filter.city,
        "neighborhood": search_filter.neighborhood,
        "bedroom_quantity": search_filter.bedroom_quantity,
        "suite_quantity": search_filter.suite_quantity,
        "bathroom_quantity": search_filter.bathroom_quantity,
        "garage_slots_quantity": search_filter.garage_slots_quantity,
        "min_price": search_filter.min_price,
        "max_price": search_filter.max_price,
        "min_area": search_filter.min_area,
        "max_area": search_filter.max_area,
    }

    real_estate_dict = get_radar_real_estate_count(radar)

    data_out_dict = {
        "id": radar.id,
        "name": radar.name,
        "filter": filter_dict,
        "real_estate": real_estate_dict,
    }

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

    # TODO - check if there is already a radar with the search id, it should not be allowed to create again

    # Radar should only refer to search objects owned by the user
    if search_obj.created_by is not None and search_obj.created_by != user:
        raise InvalidSearchIdError

    radar_obj = Radar.objects.create(
        created_by=user, name=data.get("name"), search=search_obj
    )

    search_real_estate_filter = SearchResultRealEstate.objects.filter(search=search_obj)

    # TODO - how to sync real_estate creation with async task?
    for search_real_estate in search_real_estate_filter:
        RadarRealEstate.objects.create(
            radar=radar_obj, real_estate=search_real_estate.real_estate
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
        search_filter = radar.search.filter

        filter_dict = {
            "property_type": search_filter.property_type,
            "transaction_type": search_filter.transaction_type,
            "city": search_filter.city,
            "neighborhood": search_filter.neighborhood,
            "bedroom_quantity": search_filter.bedroom_quantity,
            "suite_quantity": search_filter.suite_quantity,
            "bathroom_quantity": search_filter.bathroom_quantity,
            "garage_slots_quantity": search_filter.garage_slots_quantity,
            "min_price": search_filter.min_price,
            "max_price": search_filter.max_price,
            "min_area": search_filter.min_area,
            "max_area": search_filter.max_area,
        }

        radar_data = {"id": radar.id, "name": radar.name, "filter": filter_dict}

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
            f"Radar ID {id} was created by other user. User requesting {user.id}"
        )

    return radar


def serialize_retrieve_radar(serializer: serializers.Serializer, radar: Radar) -> Dict:
    search_filter = radar.search.filter

    # filter information
    filter_dict = {
        "property_type": search_filter.property_type,
        "transaction_type": search_filter.transaction_type,
        "city": search_filter.city,
        "neighborhood": search_filter.neighborhood,
        "bedroom_quantity": search_filter.bedroom_quantity,
        "suite_quantity": search_filter.suite_quantity,
        "bathroom_quantity": search_filter.bathroom_quantity,
        "garage_slots_quantity": search_filter.garage_slots_quantity,
        "min_price": search_filter.min_price,
        "max_price": search_filter.max_price,
        "min_area": search_filter.min_area,
        "max_area": search_filter.max_area,
    }

    real_estate_dict = get_radar_real_estate_count(radar)

    data_out_dict = {
        "id": radar.id,
        "name": radar.name,
        "real_estate": real_estate_dict,
        "filter": filter_dict,
    }

    data_out = serializer(data=data_out_dict)
    if not data_out.is_valid():
        raise SerializationError(data_out.errors)

    return data_out.validated_data


def list_real_estate(
    user: User, radar_id: str, query_params: Optional[Dict]
) -> QuerySet:

    query_preference = query_params.get(
        "preference", RadarRealEstate.Preference.PENDING
    )

    try:
        radar = Radar.objects.get(id=radar_id)
    except Radar.DoesNotExist:
        raise InvalidRadarIdError(f"Radar ID {radar_id} not found")

    if radar.created_by != user:
        raise InvalidRadarIdError(
            f"Radar ID {id} was created by other user. User requesting {user.id}"
        )

    real_estate = RadarRealEstate.objects.filter(
        radar=radar, preference=query_preference
    )

    return real_estate


def serialize_real_estate_list(
    serializer: serializers.Serializer, radar_real_estates: List[RealEstate]
) -> Dict:
    radar_real_estate_list = []

    for radar_re in radar_real_estates:
        re_dict = {"id": radar_re.id}

        radar_real_estate_list.append(re_dict)

    list_response_dict = {
        "data": radar_real_estate_list,
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


def deserialize_list_query_params_radar_real_estate(
    serializer: serializers.Serializer, query_params: Dict
) -> Dict:
    qp_serializer = serializer(data=query_params)
    if not qp_serializer.is_valid():
        raise DeserializationError(qp_serializer.errors)

    return qp_serializer.validated_data


class InvalidRadarRealEstateIdError(Exception):
    pass


def retrieve_radar_real_estate(user: User, id: str) -> RadarRealEstate:
    try:
        radar_real_estate = RadarRealEstate.objects.get(id=id)
    except RadarRealEstate.DoesNotExist:
        raise InvalidRadarRealEstateIdError(f"Radar real estate with ID {id} not found")

    if radar_real_estate.radar.created_by != user:
        raise InvalidRadarRealEstateIdError(
            f"Radar real estate with ID {id} is not owned by {user.id}"
        )

    return radar_real_estate


def serialize_radar_real_estate_retrieve(
    serializer: serializers.Serializer, radar_real_estate: RadarRealEstate
) -> Dict:
    data_out_dict = {
        "id": radar_real_estate.id,
        "preference": radar_real_estate.preference,
    }

    data_out = serializer(data=data_out_dict)
    if not data_out.is_valid():
        raise SerializationError(data_out.errors)

    return data_out.validated_data


def deserialize_update_radar_real_estate(
    serializer: serializers.Serializer, data: QueryDict
) -> Dict:
    data_in = serializer(data=data)
    if not data_in.is_valid():
        raise DeserializationError(data_in.errors)

    return data_in.validated_data


def update_radar_real_estate(
    radar_real_estate: RadarRealEstate, data_in: Dict
) -> RadarRealEstate:
    radar_real_estate.preference = data_in.get("preference")
    radar_real_estate.viewed_at = datetime.now(timezone.utc)
    radar_real_estate.save()

    return radar_real_estate
