import factory

from radar.models import Radar
from search.factories import SearchFactory
from user.factories import UserFactory


class RadarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Radar

    name = "First radar"
    created_by = factory.SubFactory(UserFactory)
    search = factory.SubFactory(SearchFactory)
