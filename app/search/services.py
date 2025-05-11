from typing import Dict, List

from django.http.request import QueryDict
from django.db.models.query import QuerySet

from search.models import Filter, Search, SearchResultRealEstate
from search.serializers import (
    SearchCreateSerializer,
    SearchRetrieveSerializer,
    SearchListSerializer,
    SearchResultListSerializer,
)

from user.models import User

from common.errors.errors import SerializationError, DeserializationError

from search.task import crawl_isc_real_estate_search
from search.webcrawler_isc import WebsiteISCFilter


def deserialize_create_search(data: QueryDict) -> Dict:
    data_in = SearchCreateSerializer(data=data)
    if not data_in.is_valid():
        raise DeserializationError(data_in.errors)

    data_in_validated = data_in.validated_data

    # convert serializer data to format that matches the model
    filter_dict = {
        "property_type": data_in_validated.get("property_type"),
        "transaction_type": data_in_validated.get("transaction_type"),
        "city": data_in_validated.get("city"),
        "neighborhood": data_in_validated.get("neighborhood"),
        "bedroom_quantity": data_in_validated.get("bedroom_quantity"),
        "suite_quantity": data_in_validated.get("suite_quantity"),
        "bathroom_quantity": data_in_validated.get("bathroom_quantity"),
        "garage_slots_quantity": data_in_validated.get("garage_slots_quantity"),
        "min_price": data_in_validated.get("min_price"),
        "max_price": data_in_validated.get("max_price"),
        "min_area": data_in_validated.get("min_area"),
        "max_area": data_in_validated.get("max_area"),
    }

    return filter_dict


def serialize_create_search(search_obj: Search) -> Dict:

    data_out_dict = {
        "id": search_obj.id,
        "query_status": search_obj.query_status,
        "number_real_estate_found": search_obj.number_real_estate_found,
        "filter": {
            "property_type": search_obj.filter.property_type,
            "transaction_type": search_obj.filter.transaction_type,
            "city": search_obj.filter.city,
            "neighborhood": search_obj.filter.neighborhood,
            "bedroom_quantity": search_obj.filter.bedroom_quantity,
            "suite_quantity": search_obj.filter.suite_quantity,
            "bathroom_quantity": search_obj.filter.bathroom_quantity,
            "garage_slots_quantity": search_obj.filter.garage_slots_quantity,
            "min_price": search_obj.filter.min_price,
            "max_price": search_obj.filter.max_price,
            "min_area": search_obj.filter.min_area,
            "max_area": search_obj.filter.max_area,
        },
    }

    data_out = SearchRetrieveSerializer(data=data_out_dict)
    if not data_out.is_valid():
        raise SerializationError(data_out.errors)

    return data_out.validated_data


def serialize_list_search(search_queryset: QuerySet) -> Dict:
    data_list = []
    for search_obj in search_queryset:
        search_dict = {
            "id": search_obj.id,
            "query_status": search_obj.query_status,
            "number_real_estate_found": search_obj.number_real_estate_found,
            "filter": {
                "property_type": search_obj.filter.property_type,
                "transaction_type": search_obj.filter.transaction_type,
                "city": search_obj.filter.city,
                "neighborhood": search_obj.filter.neighborhood,
                "bedroom_quantity": search_obj.filter.bedroom_quantity,
                "suite_quantity": search_obj.filter.suite_quantity,
                "bathroom_quantity": search_obj.filter.bathroom_quantity,
                "garage_slots_quantity": search_obj.filter.garage_slots_quantity,
                "min_price": search_obj.filter.min_price,
                "max_price": search_obj.filter.max_price,
                "min_area": search_obj.filter.min_area,
                "max_area": search_obj.filter.max_area,
            },
        }
        data_list.append(search_dict)

    list_response_dict = {
        "data": data_list,
        "meta": {
            "total": 0,
            "page": 0,
            "per_page": 0,
            "total_pages": 0,
        },
    }

    list_serializer = SearchListSerializer(data=list_response_dict)
    if not list_serializer.is_valid():
        raise SerializationError(list_serializer.errors)

    return list_serializer.validated_data


def serialize_retrieve_search(search_obj: Search) -> Dict:

    data_out_dict = {
        "id": search_obj.id,
        "query_status": search_obj.query_status,
        "number_real_estate_found": search_obj.number_real_estate_found,
        "filter": {
            "property_type": search_obj.filter.property_type,
            "transaction_type": search_obj.filter.transaction_type,
            "city": search_obj.filter.city,
            "neighborhood": search_obj.filter.neighborhood,
            "bedroom_quantity": search_obj.filter.bedroom_quantity,
            "suite_quantity": search_obj.filter.suite_quantity,
            "bathroom_quantity": search_obj.filter.bathroom_quantity,
            "garage_slots_quantity": search_obj.filter.garage_slots_quantity,
            "min_price": search_obj.filter.min_price,
            "max_price": search_obj.filter.max_price,
            "min_area": search_obj.filter.min_area,
            "max_area": search_obj.filter.max_area,
        },
    }

    data_out = SearchRetrieveSerializer(data=data_out_dict)
    if not data_out.is_valid():
        raise SerializationError(data_out.errors)

    return data_out.validated_data


def create_search(user: User, data: Dict) -> Search:
    """Create search object"""
    request_user = user
    if request_user.is_anonymous == True:
        request_user = None

    filter_obj = Filter.objects.create(created_by=request_user, **data)
    search_obj = Search.objects.create(created_by=request_user, filter=filter_obj)

    crawl_isc_real_estate_search.delay(search_obj.id)

    return search_obj


def list_search(user: User) -> QuerySet:
    """List search entries"""
    if user.is_anonymous == True:
        return Search.objects.none()

    search_queryset = Search.objects.filter(created_by=user)

    return search_queryset


def get_search(id: str) -> Search:
    return Search.objects.get(id=id)


def list_search_result(search_id: str) -> QuerySet:
    """List real estates with certain search_id"""
    return SearchResultRealEstate.objects.filter(search=search_id)


def serialize_search_result(queryset: List[SearchResultRealEstate]) -> Dict:
    """Convert queryset result to expected serialize format"""
    real_estate_list = []

    for search_result_element in queryset:
        data_out = {
            "id": search_result_element.real_estate.id,
            "property_type": search_result_element.real_estate.property_type,
            "transaction_type": search_result_element.real_estate.transaction_type,
            "city": search_result_element.real_estate.city,
            "neighborhood": search_result_element.real_estate.neighborhood,
            "bedroom_quantity": search_result_element.real_estate.bedroom_quantity,
            "suite_quantity": search_result_element.real_estate.suite_quantity,
            "garage_slots_quantity": search_result_element.real_estate.suite_quantity,
            "price": search_result_element.real_estate.price,
            "condo_price": search_result_element.real_estate.cond_price,
            "area": search_result_element.real_estate.area,
            "area_total": search_result_element.real_estate.area_total,
        }

        real_estate_list.append(data_out)

    list_response_dict = {
        "data": real_estate_list,
        "meta": {
            "total": 0,
            "page": 0,
            "per_page": 0,
            "total_pages": 0,
        },
    }

    serialize = SearchResultListSerializer(data=list_response_dict)
    if not serialize.is_valid():
        raise SerializationError(serialize.errors)

    return serialize.validated_data
