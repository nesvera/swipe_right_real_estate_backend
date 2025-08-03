import factory

from real_estate_review.models import RadarRealEstateReview

from user.factories import UserFactory
from radar.factories import RadarRealEstateFactory

from radar.models import RadarRealEstate
from real_estate_review.models import RadarRealEstateReview


class RadarRealEstateReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RadarRealEstateReview

    created_by = factory.SubFactory(UserFactory)
    radar_real_estate = factory.SubFactory(RadarRealEstateFactory)
    rating = 1
    preference = RadarRealEstate.Preference.LIKE
    good_tags = [RadarRealEstateReview.Tags.CEILING]
    bad_tags = [RadarRealEstateReview.Tags.BALCONY]
    user_notes = "Nice place"
