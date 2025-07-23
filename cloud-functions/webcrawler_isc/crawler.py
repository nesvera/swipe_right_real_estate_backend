from typing import List
import traceback

from database import (
    fetch_search,
    Search,
    RealEstate,
    get_filter_property_type,
    get_filter_fields,
    set_search_number_real_estate_found,
    set_search_query_status,
    get_real_estate_by_reference_code,
    get_agency_by_profile_url,
    insert_agency,
    insert_real_estate,
    ObjectNotFoundError,
    GenericInsertError
)
from webcrawler_isc import (
    WebsiteISCFilter,
    WebcrawlerISCRealEstate,
    WebsiteISCRealEstateInfo,
)


def create_isc_filter(search_id: str) -> WebsiteISCFilter:

    try:
        filter_fields = get_filter_fields(search_id=search_id)
    except ObjectNotFoundError:
        raise ObjectNotFoundError(f"search ID {search_id} not found")

    # TODO - probably it is better to raise an error instead of given a default
    filter_property_type = filter_fields.get("property_type", [])

    property_type = []
    for pt in filter_property_type:
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

    filter_transaction_type = filter_fields.get("transaction_type", [])

    transaction_type = []
    for tt in filter_transaction_type:
        if tt == RealEstate.TransactionType.BUY:
            transaction_type.append("comprar")
        else:
            transaction_type.append("alugar")

    filter_city = filter_fields.get("city", [])
    city = filter_city[0]

    filter_neighborhood = filter_fields.get("neighborhood", [])
    neighborhood = filter_neighborhood

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

    filter_bedroom_qnt = filter_fields.get("bedroom_quantity", [])
    bedroom_quantity = number_list_to_options(filter_bedroom_qnt)

    filter_suite_qnt = filter_fields.get("suite_quantity", [])
    suite_quantity = number_list_to_options(filter_suite_qnt)

    filter_garage_qnt = filter_fields.get("garage_slots_quantity", [])
    garage_slots_quantity = number_list_to_options(filter_garage_qnt)

    filter_min_price = filter_fields.get("min_price", 0)
    min_price = int(filter_min_price)

    filter_max_price = filter_fields.get("max_price", 0)
    max_price = int(filter_max_price)

    filter_min_area = filter_fields.get("min_area", 0)
    min_area = int(filter_min_area)

    filter_max_area = filter_fields.get("max_area", 0)
    max_area = int(filter_max_area)

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


# TODO - improve error handling
def create_real_estate_object(
    real_estate_info: WebsiteISCRealEstateInfo, search_obj: Search
) -> None:
    print(f"Creating real estate object for code {real_estate_info.code}")
    try:
        agency_obj = get_agency_by_profile_url(
            profile_url=real_estate_info.agency.profile_url
        )
    except ObjectNotFoundError:
        try:
            print(f"Creating agency object for name {real_estate_info.agency.name}")
            insert_agency(
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
        insert_real_estate(
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
            agency=agency_obj.get("id"),
            cond_price=0.0,
            description="",
            thumb_url=real_estate_info.thumb_urls,
            url=real_estate_info.url,
        )
        return None
    except Exception as e:
        print(
            f"Failed to create real estate object for code {real_estate_info.code}. Error: {e}."
        )
        return None


def update_real_estate_object(
    re_object: dict,
    real_estate_info: WebsiteISCRealEstateInfo,
    search_obj: Search,
):
    print(f"Updating ID {re_object.get("id")} - Code {real_estate_info.code}")
    pass


def crawler(request):
    """Entry function for cloud function"""
    search_id = request.args.get("search_id")

    try:
        isc_filter = create_isc_filter(search_id=search_id)
    except ObjectNotFoundError:
        print("Failed to create ISC filter")
        return "failed"

    crawler = WebcrawlerISCRealEstate()
    crawler.set_filter(isc_filter)

    search_obj = Search()

    try:
        for page_content in crawler.crawl():
            if page_content.page == 1:
                set_search_number_real_estate_found(search_id, page_content.total)
                set_search_query_status(search_id, Search.QueryStatus.PARTIAL)

            real_estate_list = page_content.real_estate_list
            for real_estate in real_estate_list:
                print(real_estate.code)
                try:
                    real_estate_obj = get_real_estate_by_reference_code(
                        reference_code=real_estate.code
                    )
                    update_real_estate_object(real_estate_obj, real_estate, search_obj)

                except ObjectNotFoundError:
                    print(f"Reference code {real_estate.code} NOT found.")
                    real_estate_obj = create_real_estate_object(real_estate, search_obj)

                except Exception as e:
                    print(
                        f"Fail to save real estate object code {real_estate.code} - URL {real_estate.url}. Error: {e}."
                    )
                    continue

                try:
                    # SearchResultRealEstate.objects.create(
                    #    search=search_obj, real_estate=real_estate_obj
                    # )
                    # TODO - how to create search result real estate
                    pass

                except Exception as e:
                    print(
                        f"Fail to create search result for real estate code {real_estate.code} - URL {real_estate.url}. Error: {e}."
                    )

    except Exception as e:
        tb = traceback.format_exc()
        print(f"Failure while crawling ISC. Error: {e}. Traceback: {tb}.")
        return

    search_obj.query_status = Search.QueryStatus.FINISHED
    # search_obj.save()
    # TODO - how to update search obj

    return search_id
