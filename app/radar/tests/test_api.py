"""
Tests for search API
"""

from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from user.factories import UserFactory
from search.factories import SearchFactory


class PublicApiTests(TestCase):
    """
    Test endpoint with unauthenticated user
    Endpoint from Radar app are authenticated
    """

    def test_create_radar_fail_user_not_authenticated(self):
        client = APIClient()
        url = reverse("radar:radar")

        res = client.post(url, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_radar_fail_user_not_authenticated(self):
        client = APIClient()
        url = reverse("radar:radar")

        res = client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_radar_fail_user_not_authenticated(self):
        client = APIClient()
        url = reverse("radar:radar-id", args=["611bd556-6703-4437-b29a-f7279b62a6e6"])

        res = client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_radar_fail_user_not_authenticated(self):
        client = APIClient()
        url = reverse("radar:radar-id", args=["611bd556-6703-4437-b29a-f7279b62a6e6"])

        res = client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_radar_real_estate_fail_user_not_authenticated(self):
        client = APIClient()
        url = reverse(
            "radar:radar-real-estate-list",
            args=["611bd556-6703-4437-b29a-f7279b62a6e6"],
        )

        res = client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_real_estate_fail_user_not_authenticated(self):
        client = APIClient()
        url = reverse(
            "radar:radar-real-estate", args=["611bd556-6703-4437-b29a-f7279b62a6e6"]
        )

        res = client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_real_estate_fail_user_not_authenticated(self):
        client = APIClient()
        url = reverse(
            "radar:radar-real-estate", args=["611bd556-6703-4437-b29a-f7279b62a6e6"]
        )

        res = client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiTest(TestCase):
    """
    Test private usage of endpoints once user is authenticated
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory.create()

    def test_create_radar_success(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("radar:radar")

        search = SearchFactory.create(created_by=self.user)

        radar_name = "new radar"
        payload = {"name": radar_name, "search": str(search.id)}

        res = client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertIn("name", res.data)
        self.assertEqual(radar_name, res.data.get("name"))

    def test_create_radar_success_search_anon(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("radar:radar")

        search = SearchFactory.create(created_by=None)

        radar_name = "new radar"
        payload = {"name": radar_name, "search": str(search.id)}

        res = client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertIn("name", res.data)
        self.assertEqual(radar_name, res.data.get("name"))

    def test_create_radar_fail_missing_name(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("radar:radar")

        search = SearchFactory.create(created_by=self.user)

        payload = {"search": str(search.id)}

        res = client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", res.data)

    def test_create_radar_fail_missing_search_id(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("radar:radar")

        radar_name = "new radar"
        payload = {"name": radar_name}

        res = client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("search", res.data)

    def test_create_radar_fail_search_id_not_exist(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("radar:radar")

        radar_name = "new radar"
        payload = {"name": radar_name, "search": "611bd556-6703-4437-b29a-f7279b62a6e6"}

        res = client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_radar_fail_search_id_other_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("radar:radar")

        search_from_other_user = SearchFactory.create()
        SearchFactory.create(created_by=self.user)

        radar_name = "new radar"
        payload = {"name": radar_name, "search": str(search_from_other_user.id)}

        res = client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # test_create_radar
    # test_list_radars
    # test_view_radar
    # test_get_pending_real_estate
    # test_get_liked_real_estate
    # test_get_disliked_real_estate
    # test_get_updated_real_estate
    # test_get_removed_real_estate
    # test_view_radar_real_estate
