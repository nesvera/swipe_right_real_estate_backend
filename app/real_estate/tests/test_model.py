from django.test import TestCase

from real_estate.models import RealEstate, RealEstateUpdate
from real_estate_agency.models import Agency


class TestModel(TestCase):
    """Test creation o real estate"""

    def test_create_model_creation(self):
        """Model creation should fail"""
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

        agency = Agency.objects.create(**agency_dict)

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
            "agency": agency,
            "cond_price": 12.0,
            "description": "some nice real estate to be sold",
            "images_url": [
                "https://some-nice-image1.png",
                "https://some-nice-image2.png",
                "https://some-nice-image3.png",
            ]
        }

        RealEstate.objects.create(**model_dict)
