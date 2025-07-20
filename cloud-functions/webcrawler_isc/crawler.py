from typing import List
import traceback

from database import (
    fetch_search,
    Search,
    RealEstate,
    get_filter_property_type,
    get_filter_fields,
    set_search_number_real_estate_found,
    set_search_query_status
)
from webcrawler_isc import WebsiteISCFilter, WebcrawlerISCRealEstate


def create_isc_filter(search_id: str) -> WebsiteISCFilter:

    filter_fields = get_filter_fields(search_id=search_id)

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


def crawler(request):
    search_id = request.args.get("search_id")

    isc_filter = create_isc_filter(search_id=search_id)

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
                    # real_estate_obj = RealEstate.objects.get(
                    #    reference_code=real_estate.code
                    # )
                    # update_real_estate_object(real_estate_obj, real_estate, search_obj)
                    # TODO - how to update real estate objects
                    pass

                except RealEstate.DoesNotExist:
                    # real_estate_obj = create_real_estate_object(real_estate, search_obj)
                    # TODO - how to create real estate objects
                    pass

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
