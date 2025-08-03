from django.test import TestCase

from radar.models import Radar, RadarRealEstate
from radar.factories import RadarFactory
from user.factories import UserFactory
from user.models import User
from search.factories import SearchFactory
from real_estate.factories import RealEstateFactory


class TestModel(TestCase):

    def test_radar_creation(self):
        user = UserFactory.create()
        search = SearchFactory.create(created_by=user)

        Radar.objects.create(name="new radar", created_by=user, search=search)

    def test_radar_real_estate_creation(self):
        radar = RadarFactory.create()
        real_estate = RealEstateFactory.create()

        RadarRealEstate(radar=radar, real_estate=real_estate)
