from django.test import TestCase
from django.contrib.auth import get_user_model

from search.models import Filter, Search
from user.models import User
from real_estate.models import RealEstate


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