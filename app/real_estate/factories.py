import factory

from real_estate.models import RealEstate
from real_estate_agency.factories import AgencyFactory


class RealEstateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RealEstate

    reference_code = "A123"
    property_type = RealEstate.PropertyType.APARTMENT
    transaction_type = RealEstate.TransactionType.BUY
    city = "Blumenau"
    neighborhood = "Victor Konder"
    bedroom_quantity = 1
    suite_quantity = 1
    bathroom_quantity = 2
    garage_slots_quantity = 1
    price = 10000.0
    area = 75.0
    area_total = 85.0
    available = True
    agency = factory.SubFactory(AgencyFactory)
    cond_price = 200.0
    description = "small apartment"
    images_url = []
    url = "https://apt1.com"
