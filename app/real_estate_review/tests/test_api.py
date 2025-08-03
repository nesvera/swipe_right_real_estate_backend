from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response

from user.factories import UserFactory
from radar.factories import RadarFactory, RadarRealEstateFactory
from real_estate_review.factories import RadarRealEstateReviewFactory

from real_estate_review.models import RadarRealEstateReview


@patch("rest_framework.throttling.AnonRateThrottle.get_rate", lambda x: "1000/minute")
class RealEstateReviewPublicApiTests(TestCase):
    """ "
    Test endpoint with unauthenticated user
    """

    def test_create_real_estate_review_fail_user_not_authenticated(self):
        client = APIClient()
        url = reverse("real_estate_review:real-estate-review")

        res: Response = client.post(url, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_real_estate_review_fail_user_not_authenticated(self):
        client = APIClient()
        url = reverse(
            "real_estate_review:real-estate-review-id",
            args=["611bd556-6703-4437-b29a-f7279b62a6e6"],
        )

        res: Response = client.patch(url, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


@patch("rest_framework.throttling.UserRateThrottle.get_rate", lambda x: "1000/minute")
class RealEstateReviewPrivateApiTests(TestCase):
    """ "
    Test endpoint with authenticated user
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory.create()

    def test_create_real_estate_review_success(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("real_estate_review:real-estate-review")

        radar = RadarFactory(created_by=self.user)
        radar_real_estate = RadarRealEstateFactory(radar=radar)

        payload = {
            "radar_real_estate": str(radar_real_estate.id),
            "rating": 1,
            "good_tags": ["paint"],
            "bad_tags": ["space"],
            "user_notes": "it is fine",
        }

        res: Response = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        try:
            review_obj = RadarRealEstateReview.objects.get(id=res.data.get("id"))
        except RadarRealEstateReview.DoesNotExist:
            assert False, f"Object was not created in the database"

        self.assertEqual(
            str(review_obj.radar_real_estate.id), payload.get("radar_real_estate")
        )
        self.assertEqual(review_obj.rating, payload.get("rating"))
        self.assertListEqual(review_obj.good_tags, payload.get("good_tags"))
        self.assertListEqual(review_obj.bad_tags, payload.get("bad_tags"))
        self.assertEqual(review_obj.user_notes, payload.get("user_notes"))

    def test_create_real_estate_review_success_min_information(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("real_estate_review:real-estate-review")

        radar = RadarFactory(created_by=self.user)
        radar_real_estate = RadarRealEstateFactory(radar=radar)

        payload = {
            "radar_real_estate": str(radar_real_estate.id),
            "rating": 1,
            "good_tags": [],
            "bad_tags": [],
            "user_notes": "",
        }

        res: Response = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        try:
            review_obj = RadarRealEstateReview.objects.get(id=res.data.get("id"))
        except RadarRealEstateReview.DoesNotExist:
            assert False, f"Object was not created in the database"

        self.assertEqual(
            str(review_obj.radar_real_estate.id), payload.get("radar_real_estate")
        )
        self.assertEqual(review_obj.rating, payload.get("rating"))
        self.assertEqual(len(review_obj.good_tags), 0)
        self.assertEqual(len(review_obj.bad_tags), 0)
        self.assertEqual(len(review_obj.user_notes), 0)

    def test_create_real_estate_review_failure_wrong_radar_real_estate_id(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("real_estate_review:real-estate-review")

        payload = {
            "radar_real_estate": "3b7a8628-0116-417d-8a84-3b27b19306b2",
            "rating": 1,
            "good_tags": ["paint"],
            "bad_tags": ["space"],
            "user_notes": "it is fine",
        }

        res: Response = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_real_estate_review_failure_radar_real_estate_id_from_other_user(
        self,
    ):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("real_estate_review:real-estate-review")

        other_user = UserFactory()
        radar = RadarFactory(created_by=other_user)
        radar_real_estate = RadarRealEstateFactory(radar=radar)

        payload = {
            "radar_real_estate": str(radar_real_estate.id),
            "rating": 1,
            "good_tags": ["paint"],
            "bad_tags": ["space"],
            "user_notes": "it is fine",
        }

        res: Response = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_real_estate_review_failure_wrong_tag(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("real_estate_review:real-estate-review")

        radar = RadarFactory(created_by=self.user)
        radar_real_estate = RadarRealEstateFactory(radar=radar)

        payload = {
            "radar_real_estate": str(radar_real_estate.id),
            "rating": 1,
            "good_tags": ["polenta"],
            "bad_tags": ["polenta"],
            "user_notes": "it is fine",
        }

        res: Response = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("good_tags", res.data)
        self.assertIn("bad_tags", res.data)

    def test_create_real_estate_review_failure_rating_greater_than_5(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("real_estate_review:real-estate-review")

        radar = RadarFactory(created_by=self.user)
        radar_real_estate = RadarRealEstateFactory(radar=radar)

        payload = {
            "radar_real_estate": str(radar_real_estate.id),
            "rating": 6,
            "good_tags": ["paint"],
            "bad_tags": ["space"],
            "user_notes": "it is fine",
        }

        res: Response = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", res.data)

    def test_create_real_estate_review_failure_rating_smaller_than_1(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("real_estate_review:real-estate-review")

        radar = RadarFactory(created_by=self.user)
        radar_real_estate = RadarRealEstateFactory(radar=radar)

        payload = {
            "radar_real_estate": str(radar_real_estate.id),
            "rating": 0,
            "good_tags": ["paint"],
            "bad_tags": ["space"],
            "user_notes": "it is fine",
        }

        res: Response = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", res.data)

    def test_create_real_estate_review_failure_missing_rating(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("real_estate_review:real-estate-review")

        radar = RadarFactory(created_by=self.user)
        radar_real_estate = RadarRealEstateFactory(radar=radar)

        payload = {"radar_real_estate": str(radar_real_estate.id)}

        res: Response = client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", res.data)
        self.assertIn("user_notes", res.data)

    def test_update_real_estate_review_success(self):
        radar = RadarFactory(created_by=self.user)
        radar_real_estate = RadarRealEstateFactory(radar=radar)
        real_estate_review_obj = RadarRealEstateReviewFactory(
            radar_real_estate=radar_real_estate, created_by=self.user
        )

        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse(
            "real_estate_review:real-estate-review-id",
            args=[str(real_estate_review_obj.id)],
        )

        payload = {
            "rating": 3,
            "good_tags": ["paint", "price"],
            "bad_tags": ["space", "closets"],
            "user_notes": "it is fine",
        }

        res: Response = client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        try:
            review_obj = RadarRealEstateReview.objects.get(id=res.data.get("id"))
        except RadarRealEstateReview.DoesNotExist:
            assert False, f"Object was not created in the database"

        self.assertEqual(review_obj.rating, payload.get("rating"))
        self.assertListEqual(review_obj.good_tags, payload.get("good_tags"))
        self.assertListEqual(review_obj.bad_tags, payload.get("bad_tags"))
        self.assertEqual(review_obj.user_notes, payload.get("user_notes"))
