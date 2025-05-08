import traceback

from celery import shared_task
from uuid import UUID


from search.models import Search
from search.webcrawler_isc import (
    WebsiteISCFilter,
    WebcrawlerISCRealEstate,
    WebsiteISCRealEstateInfo,
)

from real_estate.models import RealEstate, Agency


def extract_property_type_from_url(real_estate_url: str) -> RealEstate.PropertyType:
    url_parts = real_estate_url.split("/")
    if len(url_parts) < 5:
        return RealEstate.PropertyType.APARTMENT

    property_type = url_parts[5]
    if property_type == "apartamento":
        return RealEstate.PropertyType.APARTMENT
    elif property_type == "casa":
        return RealEstate.PropertyType.HOUSE
    elif property_type == "terreno":
        return RealEstate.PropertyType.TERRAIN
    elif property_type == "sala-escritorio":
        return RealEstate.PropertyType.OFFICE
    elif property_type == "galpao":
        return RealEstate.PropertyType.WAREHOUSE
    elif property_type == "imovel-rural":
        return RealEstate.PropertyType.RURAL
    else:
        return RealEstate.PropertyType.HOUSE


def extract_transaction_type_from_url(
    real_estate_url: str,
) -> RealEstate.TransactionType:
    url_parts = real_estate_url.split("/")
    if len(url_parts) < 4:
        return RealEstate.TransactionType.BUY

    property_type = url_parts[4]
    if property_type == "comprar":
        return RealEstate.TransactionType.BUY
    else:
        return RealEstate.TransactionType.RENT


def convert_values_to_float(value: str) -> float:
    tmp_value = value.replace(".", "")
    tmp_value = tmp_value.replace(",", ".")
    try:
        tmp_value = float(tmp_value)
    except:
        print(f"Fail to convert to float {value}")
        tmp_value = 0.0

    return tmp_value


def create_real_estate_object(
    real_estate_info: WebsiteISCRealEstateInfo, search_obj: Search
):
    print(f"Creating real estate object for code {real_estate_info.code}")
    try:
        agency_obj = Agency.objects.get(profile_url=real_estate_info.agency.profile_url)
    except Agency.DoesNotExist:
        try:
            print(f"Creating agency object for name {real_estate_info.agency.name}")
            agency_obj = Agency(
                name=real_estate_info.agency.name,
                logo_url=real_estate_info.agency.logo_url,
                profile_url=real_estate_info.agency.profile_url,
                creci="",
                city="",
                address_street="",
                address_number="",
                contact_number_1="",
                contact_number_2="",
                contact_whatsapp="",
            )
            agency_obj.save()

        except Exception as e:
            print(
                f"Failed to create agency object for name {real_estate_info.agency.name}. Error: {e}."
            )
            return

    property_type = extract_property_type_from_url(real_estate_info.url)
    transaction_type = extract_transaction_type_from_url(real_estate_info.url)
    price = convert_values_to_float(real_estate_info.price)
    area = convert_values_to_float(real_estate_info.space)

    try:
        re_obj = RealEstate(
            reference_code=real_estate_info.code,
            property_type=property_type,
            transaction_type=transaction_type,
            city=real_estate_info.city,
            neighborhood=real_estate_info.neighborhood,
            bedroom_quantity=int(real_estate_info.bedrooms),
            suite_quantity=int(real_estate_info.suite),
            bathroom_quantity=0,
            garage_slots_quantity=int(real_estate_info.garage_slots),
            price=price,
            area=area,
            area_total=area,
            available=True,
            agency=agency_obj,
            cond_price=0.0,
            description="",
            images_url=[],
            url=real_estate_info.url,
        )
        re_obj.save()
    except Exception as e:
        print(
            f"Failed to create real estate object for code {real_estate_info.code}. Error: {e}."
        )


def update_real_estate_object(
    re_object: RealEstate,
    real_estate_info: WebsiteISCRealEstateInfo,
    search_obj: Search,
):
    print(f"Updating ID {re_object.id} - Code {real_estate_info.code}")
    pass


@shared_task(queue="default")
def crawl_isc_real_estate_search(search_id: UUID) -> None:
    try:
        search_obj = Search.objects.get(id=search_id)
    except Search.DoesNotExist:
        print(f"Search object does not exist. ID: {search_id}.")
        return

    # TODO - needs to convert from server filter to ISC filter
    webcrawler_filter = WebsiteISCFilter(
        property_type=["apartamento", "casa", "terreno"],
        transaction_type=["comprar", "alugar"],
        city="blumenau",
        neighborhood=["agua-verde", "bom-retiro", "centro", "fidelis"],
        bedroom_quantity=["3", "4", "5+"],
        suite_quantity=["1", "4", "5+"],
        garage_slots_quantity=["1", "4", "5+"],
        min_price=500000,
        max_price=1200000,
        min_area=35,
        max_area=95,
    )

    crawler = WebcrawlerISCRealEstate()
    crawler.set_filter(webcrawler_filter)

    try:
        for page_content in crawler.crawl():
            if page_content.page == 1:
                search_obj.number_real_estate_found = page_content.total
                search_obj.query_status = Search.QueryStatus.PARTIAL
                search_obj.save()

            real_estate_list = page_content.real_estate_list
            for real_estate in real_estate_list:
                try:
                    obj = RealEstate.objects.get(reference_code=real_estate.code)
                    update_real_estate_object(obj, real_estate, search_obj)

                except RealEstate.DoesNotExist:
                    create_real_estate_object(real_estate, search_obj)

                except Exception as e:
                    print(
                        f"Fail to save real estate object code {real_estate.code} - URL {real_estate.url}. Error: {e}."
                    )

    except Exception as e:
        tb = traceback.format_exc()
        print(f"Failure while crawling ISC. Error: {e}. Traceback: {tb}.")
        return

    search_obj.query_status = Search.QueryStatus.FINISHED
    search_obj.save()


@shared_task
def crawl_isc_real_estate_get_details():
    pass


@shared_task
def crawl_isc_agency_get_details():
    pass
