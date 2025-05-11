from django.test import TestCase
from django.contrib.auth import get_user_model

from search.models import Filter, Search, SearchResultRealEstate
from user.models import User
from real_estate.models import RealEstate, Agency


class TestModel(TestCase):
    """Test models from search app"""

    def test_model_creation_with_user_authenticated(self):
        user_dict = {
            "email": "myuser@myemail.com",
            "password": "Securepassword123$",
            "name": "My user",
        }
        user_obj = get_user_model().objects.create_user(**user_dict)

        filter_dict = {
            "created_by": user_obj,
            "property_type": [
                RealEstate.PropertyType.APARTMENT,
                RealEstate.PropertyType.HOUSE,
            ],
            "transaction_type": [
                RealEstate.TransactionType.BUY,
                RealEstate.TransactionType.RENT,
            ],
            "city": ["xique-xique", "sao paulo"],
            "neighborhood": ["some-trust", "some-quite"],
            "bedroom_quantity": [2],
            "suite_quantity": [1],
            "bathroom_quantity": [2],
            "garage_slots_quantity": [1],
            "min_price": 100.0,
            "max_price": 200.0,
            "min_area": 20.0,
            "max_area": 30.0,
        }
        filter_obj = Filter.objects.create(**filter_dict)

        search_dict = {
            "created_by": user_obj,
            "filter": filter_obj,
        }
        Search.objects.create(**search_dict)

    def test_model_creation_without_user_authenticated(self):
        filter_dict = {
            "property_type": [
                RealEstate.PropertyType.APARTMENT,
                RealEstate.PropertyType.HOUSE,
            ],
            "transaction_type": [
                RealEstate.TransactionType.BUY,
                RealEstate.TransactionType.RENT,
            ],
            "city": ["xique-xique", "sao paulo"],
            "neighborhood": ["some-trust", "some-quite"],
            "bedroom_quantity": [2],
            "suite_quantity": [1],
            "bathroom_quantity": [2],
            "garage_slots_quantity": [1],
            "min_price": 100.0,
            "max_price": 200.0,
            "min_area": 20.0,
            "max_area": 30.0,
        }
        filter_obj = Filter.objects.create(**filter_dict)

        search_dict = {
            "filter": filter_obj,
        }
        Search.objects.create(**search_dict)

    def test_model_creation_search_result_real_estate(self):
        filter_dict = {
            "property_type": [
                RealEstate.PropertyType.APARTMENT,
                RealEstate.PropertyType.HOUSE,
            ],
            "transaction_type": [
                RealEstate.TransactionType.BUY,
                RealEstate.TransactionType.RENT,
            ],
            "city": ["xique-xique", "sao paulo"],
            "neighborhood": ["some-trust", "some-quite"],
            "bedroom_quantity": [2],
            "suite_quantity": [1],
            "bathroom_quantity": [2],
            "garage_slots_quantity": [1],
            "min_price": 100.0,
            "max_price": 200.0,
            "min_area": 20.0,
            "max_area": 30.0,
        }
        filter_obj = Filter.objects.create(**filter_dict)

        search_dict = {
            "filter": filter_obj,
        }
        search_obj = Search.objects.create(**search_dict)

        agency_dict = {
            "name": "blah",
            "creci": "12345",
            "city": "texas",
            "address_street": "street1",
            "address_number": "123",
            "contact_number_1": "1234",
            "contact_number_2": "4321",
            "contact_whatsapp": "4444",
            "logo_url": "https://someplace",
        }

        agency_obj = Agency.objects.create(**agency_dict)

        model_dict = {
            "reference_code": "0001",
            "property_type": RealEstate.PropertyType.APARTMENT,
            "transaction_type": RealEstate.TransactionType.BUY,
            "city": "texas",
            "neighborhood": "some-neighborhood",
            "bedroom_quantity": 2,
            "suite_quantity": 1,
            "bathroom_quantity": 2,
            "garage_slots_quantity": 1,
            "price": 100.0,
            "area": 50.0,
            "area_total": 55.0,
            "available": True,
            "agency": agency_obj,
            "cond_price": 12.0,
            "description": "some nice real estate to be sold",
            "images_url": [
                "https://some-nice-image1.png",
                "https://some-nice-image2.png",
                "https://some-nice-image3.png",
            ],
        }

        real_estate_obj = RealEstate.objects.create(**model_dict)

        SearchResultRealEstate.objects.create(
            search=search_obj, real_estate=real_estate_obj
        )
