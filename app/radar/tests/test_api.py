"""
Tests for search API
"""

from unittest.mock import patch
from datetime import datetime, timezone

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from user.factories import UserFactory
from search.factories import SearchFactory
from radar.models import Radar, RadarRealEstate
from radar.factories import RadarFactory, RadarRealEstateFactory
from real_estate.factories import RealEstateFactory


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

    def test_list_radar_success(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("radar:radar")

        radar = RadarFactory.create(created_by=self.user)

        res = client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("data", res.data)
        self.assertIn("meta", res.data)
        self.assertEqual(len(res.data.get("data")), 1)
        self.assertEqual(res.data.get("data", {})[0].get("name"), radar.name)

    def test_list_radar_does_not_return_other_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("radar:radar")

        # create one radar for another user
        RadarFactory.create()

        res = client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("data", res.data)
        self.assertIn("meta", res.data)
        self.assertEqual(len(res.data.get("data")), 0)

    def test_retrieve_radar_success(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory(created_by=self.user)
        real_estate_1 = RealEstateFactory()
        RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate_1,
            preference=RadarRealEstate.Preference.LIKE,
        )
        real_estate_2 = RealEstateFactory()
        RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate_2,
            preference=RadarRealEstate.Preference.DISLIKE,
        )
        real_estate_3 = RealEstateFactory()
        RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate_3,
            preference=RadarRealEstate.Preference.PENDING,
        )
        real_estate_4 = RealEstateFactory()
        RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate_4,
            removed_at=datetime.now(timezone.utc),
        )

        url = reverse("radar:radar-id", args=[str(radar.id)])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("id", res.data)
        self.assertIn("name", res.data)
        self.assertIn("filter", res.data)
        self.assertIn("real_estate", res.data)
        self.assertEqual(radar.id, res.data.get("id"))
        self.assertEqual(radar.name, res.data.get("name"))
        self.assertEqual(res.data.get("real_estate", {}).get("like_count"), 1)
        self.assertEqual(res.data.get("real_estate", {}).get("dislike_count"), 1)
        self.assertEqual(res.data.get("real_estate", {}).get("pending_count"), 1)
        self.assertEqual(res.data.get("real_estate", {}).get("removed_count"), 1)

        # TODO - this is meme since the value is hardcoded
        self.assertEqual(res.data.get("real_estate", {}).get("added_count"), 0)

    def test_retrieve_fail_id_not_exist(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("radar:radar-id", args=["611bd556-6703-4437-b29a-f7279b62a6e6"])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_fail_id_other_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory()

        url = reverse("radar:radar-id", args=[str(radar.id)])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_success(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory.create(created_by=self.user)

        url = reverse("radar:radar-id", args=[str(radar.id)])

        res = client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        radar_queryset = Radar.objects.all()
        self.assertEqual(len(radar_queryset), 0)

    def test_delete_fail_id_not_exist(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("radar:radar-id", args=["611bd556-6703-4437-b29a-f7279b62a6e6"])

        res = client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_fail_id_other_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory()

        url = reverse("radar:radar-id", args=[str(radar.id)])

        res = client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_radar_real_estate_success_default_preference_pending(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory(created_by=self.user)
        real_estate = RealEstateFactory()
        radar_real_estate_pending = RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate,
            preference=RadarRealEstate.Preference.PENDING,
        )
        RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate,
            preference=RadarRealEstate.Preference.DISLIKE,
        )

        url = reverse("radar:radar-real-estate-list", args=[str(radar.id)])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("data", res.data)
        self.assertIn("meta", res.data)

        data_list = res.data.get("data", [])

        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0].get("id"), radar_real_estate_pending.id)

    def test_list_radar_real_estate_fail_id_not_found(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        RadarFactory()

        url = reverse(
            "radar:radar-real-estate-list",
            args=["611bd556-6703-4437-b29a-f7279b62a6e6"],
        )

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_radar_real_estate_fail_id_other_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory()

        url = reverse("radar:radar-real-estate-list", args=[str(radar.id)])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_radar_real_estate_success_preference_like(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory(created_by=self.user)
        real_estate = RealEstateFactory()
        radar_real_estate_like = RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate,
            preference=RadarRealEstate.Preference.LIKE,
        )
        RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate,
            preference=RadarRealEstate.Preference.PENDING,
        )

        url = reverse(
            "radar:radar-real-estate-list",
            args=[str(radar.id)],
            query={"preference": "like"},
        )

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("data", res.data)
        self.assertIn("meta", res.data)

        data_list = res.data.get("data", [])

        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0].get("id"), radar_real_estate_like.id)

    def test_list_radar_real_estate_success_preference_dislike(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory(created_by=self.user)
        real_estate = RealEstateFactory()
        radar_real_estate_dislike = RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate,
            preference=RadarRealEstate.Preference.DISLIKE,
        )
        RadarRealEstateFactory(
            radar=radar,
            real_estate=real_estate,
            preference=RadarRealEstate.Preference.PENDING,
        )

        url = reverse(
            "radar:radar-real-estate-list",
            args=[str(radar.id)],
            query={"preference": "dislike"},
        )

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("data", res.data)
        self.assertIn("meta", res.data)

        data_list = res.data.get("data", [])

        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0].get("id"), radar_real_estate_dislike.id)

    def test_retrieve_radar_real_estate_success(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory(created_by=self.user)
        real_estate = RealEstateFactory()
        radar_real_estate = RadarRealEstateFactory(radar=radar, real_estate=real_estate)

        url = reverse("radar:radar-real-estate", args=[str(radar_real_estate.id)])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("id", res.data)
        self.assertIn("preference", res.data)
        self.assertEqual(radar_real_estate.id, res.data.get("id"))
        self.assertEqual(radar_real_estate.preference, res.data.get("preference"))

    def test_retrieve_radar_real_estate_fail_id_not_found(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse(
            "radar:radar-real-estate", args=["611bd556-6703-4437-b29a-f7279b62a6e6"]
        )

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_radar_real_estate_fail_id_other_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory()
        real_estate = RealEstateFactory()
        radar_real_estate = RadarRealEstateFactory(radar=radar, real_estate=real_estate)

        url = reverse("radar:radar-real-estate", args=[str(radar_real_estate.id)])

        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("radar.services.datetime")
    def test_update_radar_real_estate_success(self, patched_datetime):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory(created_by=self.user)
        real_estate = RealEstateFactory()
        radar_real_estate = RadarRealEstateFactory(radar=radar, real_estate=real_estate)

        url = reverse("radar:radar-real-estate", args=[str(radar_real_estate.id)])

        preference = RadarRealEstate.Preference.LIKE
        payload = {"preference": preference}

        viewed_time_str = "09/19/22 13:55:26"
        viewed_time = datetime.strptime(viewed_time_str, "%m/%d/%y %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        patched_datetime.now.return_value = viewed_time

        res = client.patch(url, payload)

        radar_real_estate.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("id", res.data)
        self.assertIn("preference", res.data)
        self.assertEqual(radar_real_estate.id, res.data.get("id"))
        self.assertEqual(radar_real_estate.preference, preference)
        self.assertEqual(radar_real_estate.viewed_at, viewed_time)

    def test_update_radar_real_estate_fail_id_not_found(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse(
            "radar:radar-real-estate", args=["611bd556-6703-4437-b29a-f7279b62a6e6"]
        )

        preference = RadarRealEstate.Preference.LIKE
        payload = {"preference": preference}

        res = client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_radar_real_estate_fail_id_other_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory()
        real_estate = RealEstateFactory()
        radar_real_estate = RadarRealEstateFactory(radar=radar, real_estate=real_estate)

        url = reverse("radar:radar-real-estate", args=[str(radar_real_estate.id)])

        preference = RadarRealEstate.Preference.LIKE
        payload = {"preference": preference}

        res = client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_radar_real_estate_fail_invalid_preference(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        radar = RadarFactory(created_by=self.user)
        real_estate = RealEstateFactory()
        radar_real_estate = RadarRealEstateFactory(radar=radar, real_estate=real_estate)

        url = reverse("radar:radar-real-estate", args=[str(radar_real_estate.id)])

        payload = {"preference": "gostei"}

        res = client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("preference", res.data)
