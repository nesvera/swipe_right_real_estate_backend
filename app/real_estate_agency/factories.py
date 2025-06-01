import factory

from real_estate_agency.models import Agency


class AgencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Agency

    name = "Nice imobiliaria"
    creci = "012345"
    city = "Blumenau"
    address_street = "Street"
    address_number = "123"
    contact_number_1 = "1111111"
    contact_number_2 = "2222222"
    contact_whatsapp = "3333333"
    logo_url = "https://niceimobiliaria.com/logo.png"
    profile_url = "https://niceimobiliaria.com"
