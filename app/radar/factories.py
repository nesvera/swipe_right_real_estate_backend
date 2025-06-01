import factory

from radar.models import Radar, RadarRealEstate
from search.factories import SearchFactory
from user.factories import UserFactory
from real_estate.factories import RealEstateFactory


class RadarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Radar

    name = "First radar"
    created_by = factory.SubFactory(UserFactory)
    search = factory.SubFactory(SearchFactory)


class RadarRealEstateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RadarRealEstate

    radar = factory.SubFactory(RadarFactory)
    real_estate = factory.SubFactory(RealEstateFactory)
    preference = RadarRealEstate.Preference.PENDING
