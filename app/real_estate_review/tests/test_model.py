from django.test import TestCase
from django.db.utils import DataError

from real_estate_review.models import RadarRealEstateReview
from radar.models import RadarRealEstate

from user.factories import UserFactory
from radar.factories import RadarRealEstateFactory


class TestRealEstateReviewModels(TestCase):

    def test_radar_real_estate_review_creation_success_min_info(self):
        user = UserFactory.create()
        radar_real_estate = RadarRealEstateFactory.create()

        try:
            RadarRealEstateReview.objects.create(
                created_by=user,
                radar_real_estate=radar_real_estate,
                preference=RadarRealEstate.Preference.LIKE,
                rating=5,
            )
        except Exception as e:
            assert False, f"Failed to create RadarRealEstateReview {e}"

    def test_radar_real_estate_review_creation_success_complete(self):
        user = UserFactory.create()
        radar_real_estate = RadarRealEstateFactory.create()

        try:
            RadarRealEstateReview.objects.create(
                created_by=user,
                radar_real_estate=radar_real_estate,
                preference=RadarRealEstate.Preference.LIKE,
                rating=5,
                good_tags=[RadarRealEstateReview.Tags.AIR_CONDITIONING],
                bad_tags=[RadarRealEstateReview.Tags.COST_BENEFIT],
            )
        except Exception as e:
            assert False, f"Failed to create RadarRealEstateReview {e}"

    def test_radar_real_estate_review_creation_failure_user_notes_too_big(self):
        user = UserFactory.create()
        radar_real_estate = RadarRealEstateFactory.create()

        with self.assertRaises(DataError):
            RadarRealEstateReview.objects.create(
                created_by=user,
                radar_real_estate=radar_real_estate,
                preference=RadarRealEstate.Preference.LIKE,
                rating=5,
                user_notes="a" * 251,
            )
