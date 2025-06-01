import factory

from search.models import Search, Filter
from user.factories import UserFactory
from real_estate.models import RealEstate


class FilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Filter

    created_by = factory.SubFactory(UserFactory)
    property_type = [RealEstate.PropertyType.APARTMENT]
    transaction_type = [RealEstate.TransactionType.BUY]
    city = ["Blumenau"]
    neighborhood = ["Victor konder"]
    bedroom_quantity = [1]
    suite_quantity = [1]
    bathroom_quantity = [1]
    garage_slots_quantity = [1]
    min_price = 1000.00
    max_price = 10000.00
    min_area = 75.0
    max_area = 78.0


class SearchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Search

    created_by = factory.SubFactory(UserFactory)
    filter = factory.SubFactory(FilterFactory)
    query_status = Search.QueryStatus.NOT_STARTED
