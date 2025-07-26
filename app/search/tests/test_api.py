"""
Tests for search API
"""

from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from search.models import Filter, Search, SearchResultRealEstate
from real_estate.models import RealEstate, Agency
from user.models import User


def create_search(user: User = None) -> Search:
    filter_obj = Filter.objects.create(
        created_by=user,
        property_type=["apartment", "house"],
        transaction_type=["rent", "buy"],
        city=["xique-xique", "sao paulo"],
        neighborhood=["some-trust", "some-quite"],
        bedroom_quantity=[2],
        suite_quantity=[1],
        bathroom_quantity=[2],
        garage_slots_quantity=[1],
        min_price=100.0,
        max_price=200.0,
        min_area=20.0,
        max_area=30.0,
    )

    search_obj = Search.objects.create(
        created_by=user,
        filter=filter_obj,
    )

    return search_obj


def create_real_estate(search_obj: Search) -> RealEstate:
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
        "thumb_url": [
            "https://some-nice-image1.png",
            "https://some-nice-image2.png",
            "https://some-nice-image3.png",
        ],
    }

    real_estate_obj = RealEstate.objects.create(**model_dict)

    SearchResultRealEstate.objects.create(
        search=search_obj, real_estate=real_estate_obj
    )

    return real_estate_obj


def create_multiple_search(n: int, user: User = None) -> None:
    for _ in range(n):
        create_search(user)


@patch("rest_framework.throttling.AnonRateThrottle.get_rate", lambda x: "1000/minute")
class PublicApiTests(TestCase):
    """
    Test public features where user is not authenticated
    User is able to create searches without being authenticated
    """

    def test_public_create_search_fail_missing_fields_payload(self):
        """User tries to create a search but forget to send some fields"""
        client = APIClient()
        url = reverse("search:search")

        payload = {
            "property_type": ["apartment", "house"],
            "transaction_type": ["rent", "buy"],
            "city": ["xique-xique", "sao paulo"],
            "neighborhood": ["some-trust", "some-quite"],
            "bedroom_quantity": 2,
            "suite_quantity": 1,
            "bathroom_quantity": 2,
            "garage_slots_quantity": 1,
            "min_price": 100.0,
            "max_price": 200.0,
            "min_area": 20.0,
        }

        res = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("max_area", res.data)

    @patch("search.services.crawl_isc_real_estate_search")
    def test_public_create_search_success(self, search_task):
        """User creates a search with success"""
        search_task.delay.return_value = None

        client = APIClient()
        url = reverse("search:search")

        payload = {
            "property_type": ["apartment", "house"],
            "transaction_type": ["rent", "buy"],
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

        res = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertIn("filter", res.data)
        self.assertIn("query_status", res.data)
        self.assertIn("number_real_estate_found", res.data)

        self.assertEqual(
            res.data.get("query_status", None), Search.QueryStatus.NOT_STARTED
        )

    def test_public_list_search(self):
        """Unauthenticated user should get empty list"""
        client = APIClient()
        url = reverse("search:search")

        create_multiple_search(2)

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("data", res.data)
        self.assertIn("meta", res.data)
        self.assertEqual(len(res.data.get("data")), 0)
        self.assertEqual(res.data.get("meta").get("total"), 0)
        self.assertEqual(res.data.get("meta").get("page"), 0)
        self.assertEqual(res.data.get("meta").get("per_page"), 0)
        self.assertEqual(res.data.get("meta").get("total_pages"), 0)

    def test_public_retrieve_fail_id_not_found(self):
        client = APIClient()
        url = reverse("search:search-pk", args=["be6c0d14-72ec-4b95-8c75-93b710868f7d"])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_retrieve_search(self):
        search_obj = create_search()

        client = APIClient()
        url = reverse("search:search-pk", args=[str(search_obj.id)])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("id", res.data)
        self.assertEqual(res.data.get("id"), search_obj.id)

    def test_public_search_result_list_real_estate(self):
        search_obj = create_search()
        real_estate_obj = create_real_estate(search_obj)

        client = APIClient()
        url = reverse("search:search-pk-result", args=[str(search_obj.id)])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("data", res.data)
        self.assertIn("meta", res.data)
        self.assertEqual(len(res.data.get("data")), 1)
        self.assertEqual(res.data.get("data")[0].get("id"), real_estate_obj.id)
        self.assertEqual(res.data.get("meta").get("total"), 0)
        self.assertEqual(res.data.get("meta").get("page"), 0)
        self.assertEqual(res.data.get("meta").get("per_page"), 0)
        self.assertEqual(res.data.get("meta").get("total_pages"), 0)


@patch("rest_framework.throttling.UserRateThrottle.get_rate", lambda x: "1000/minute")
class PrivateApiTest(TestCase):
    """
    Test private usage of endpoints once user is authenticated
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create_user(
            email="myuser@myemail.com", password="securepassword123", name="My user"
        )

    @patch("search.services.crawl_isc_real_estate_search")
    def test_private_create_search_success(self, search_task):
        """User creates a search with success"""
        search_task.delay.return_value = None

        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("search:search")

        payload = {
            "property_type": ["apartment", "house"],
            "transaction_type": ["rent", "buy"],
            "city": ["xique-xique", "sao paulo"],
            "neighborhood": ["some-trust", "some-quite"],
            "bedroom_quantity": 2,
            "suite_quantity": 1,
            "bathroom_quantity": 2,
            "garage_slots_quantity": 1,
            "min_price": 100.0,
            "max_price": 200.0,
            "min_area": 20.0,
            "max_area": 30.0,
        }

        res = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertIn("filter", res.data)
        self.assertIn("query_status", res.data)
        self.assertIn("number_real_estate_found", res.data)

        self.assertEqual(
            res.data.get("query_status", None), Search.QueryStatus.NOT_STARTED
        )

    def test_private_list_search(self):
        """Unauthenticated user should get empty list"""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("search:search")

        create_multiple_search(2, self.user)

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("data", res.data)
        self.assertIn("meta", res.data)
        self.assertEqual(len(res.data.get("data")), 2)
        self.assertIn("id", res.data.get("data")[0])
        self.assertIn("query_status", res.data.get("data")[0])
        self.assertIn("filter", res.data.get("data")[0])
        self.assertIn("property_type", res.data.get("data")[0].get("filter"))
        self.assertEqual(res.data.get("meta").get("total"), 0)
        self.assertEqual(res.data.get("meta").get("page"), 0)
        self.assertEqual(res.data.get("meta").get("per_page"), 0)
        self.assertEqual(res.data.get("meta").get("total_pages"), 0)

    def test_private_retrieve_search(self):
        search_obj = create_search(self.user)

        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("search:search-pk", args=[str(search_obj.id)])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("id", res.data)
        self.assertEqual(res.data.get("id"), search_obj.id)
