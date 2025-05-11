import traceback

from celery import shared_task
from uuid import UUID
from typing import List, Optional


from search.models import Search, SearchResultRealEstate
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
) -> Optional[RealEstate]:
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
            return None

    property_type = extract_property_type_from_url(real_estate_info.url)
    transaction_type = extract_transaction_type_from_url(real_estate_info.url)
    price = convert_values_to_float(real_estate_info.price)
    area = convert_values_to_float(real_estate_info.space)

    bedrooms = real_estate_info.bedrooms
    if len(bedrooms) == 0:
        bedrooms = 0

    suites = real_estate_info.suite
    if len(suites) == 0:
        suites = 0

    garage_slots = real_estate_info.garage_slots
    if len(garage_slots) == 0:
        garage_slots = 0

    try:
        re_obj = RealEstate(
            reference_code=real_estate_info.code,
            property_type=property_type,
            transaction_type=transaction_type,
            city=real_estate_info.city,
            neighborhood=real_estate_info.neighborhood,
            bedroom_quantity=bedrooms,
            suite_quantity=suites,
            bathroom_quantity=0,
            garage_slots_quantity=garage_slots,
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
        return re_obj
    except Exception as e:
        print(
            f"Failed to create real estate object for code {real_estate_info.code}. Error: {e}."
        )
        return None


def update_real_estate_object(
    re_object: RealEstate,
    real_estate_info: WebsiteISCRealEstateInfo,
    search_obj: Search,
):
    print(f"Updating ID {re_object.id} - Code {real_estate_info.code}")
    pass


def create_isc_filter(search_obj: Search) -> WebsiteISCFilter:
    # convert filter description from model definition to ISC definition
    property_type = []
    for pt in search_obj.filter.property_type:
        if pt == RealEstate.PropertyType.APARTMENT:
            property_type.append("apartamento")
        elif pt == RealEstate.PropertyType.HOUSE:
            property_type.append("casa")
        elif pt == RealEstate.PropertyType.TERRAIN:
            property_type.append("terreno")
        elif pt == RealEstate.PropertyType.OFFICE:
            property_type.append("sala-escritorio")
        elif pt == RealEstate.PropertyType.WAREHOUSE:
            property_type.append("galpao")
        elif pt == RealEstate.PropertyType.RURAL:
            property_type.append("imovel-rural")
        else:
            property_type.append("casa")

    transaction_type = []
    for tt in search_obj.filter.transaction_type:
        if tt == RealEstate.TransactionType.BUY:
            transaction_type.append("comprar")
        else:
            transaction_type.append("alugar")

    city = search_obj.filter.city[0]
    neighborhood = search_obj.filter.neighborhood

    def number_list_to_options(number_list: List[int]) -> List[str]:
        # isc accepts a list of strings with numbers up to 4, and then 5+
        options = []
        for n in number_list:
            if n < 5 and n not in options:
                options.append(str(n))
                continue
            elif n >= 5 and "5+" not in options:
                options.append("5+")
                continue
            else:
                continue

        return options

    bedroom_quantity = number_list_to_options(search_obj.filter.bedroom_quantity)
    suite_quantity = number_list_to_options(search_obj.filter.suite_quantity)
    garage_slots_quantity = number_list_to_options(
        search_obj.filter.garage_slots_quantity
    )
    min_price = int(search_obj.filter.min_price)
    max_price = int(search_obj.filter.max_price)
    min_area = int(search_obj.filter.min_area)
    max_area = int(search_obj.filter.max_area)

    isc_filter = WebsiteISCFilter(
        property_type=property_type,
        transaction_type=transaction_type,
        city=city,
        neighborhood=neighborhood,
        bedroom_quantity=bedroom_quantity,
        suite_quantity=suite_quantity,
        garage_slots_quantity=garage_slots_quantity,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
    )
    return isc_filter


@shared_task(queue="default")
def crawl_isc_real_estate_search(search_id: UUID) -> None:
    try:
        search_obj = Search.objects.get(id=search_id)
    except Search.DoesNotExist:
        print(f"Search object does not exist. ID: {search_id}.")
        return

    webcrawler_filter = create_isc_filter(search_obj)

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
                    real_estate_obj = RealEstate.objects.get(
                        reference_code=real_estate.code
                    )
                    update_real_estate_object(real_estate_obj, real_estate, search_obj)

                except RealEstate.DoesNotExist:
                    real_estate_obj = create_real_estate_object(real_estate, search_obj)

                except Exception as e:
                    print(
                        f"Fail to save real estate object code {real_estate.code} - URL {real_estate.url}. Error: {e}."
                    )
                    continue

                try:
                    SearchResultRealEstate.objects.create(
                        search=search_obj, real_estate=real_estate_obj
                    )
                except Exception as e:
                    print(
                        f"Fail to create search result for real estate code {real_estate.code} - URL {real_estate.url}. Error: {e}."
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
