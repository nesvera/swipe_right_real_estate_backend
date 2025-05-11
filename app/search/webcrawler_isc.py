#!/bin/env python3

import requests
from bs4 import (
    BeautifulSoup,
    element,
)
from typing import Optional, List, Generator, Tuple, Union
import time
import re


class WebsiteISCAgencyInfo:
    name: str = ""
    profile_url: str = ""
    logo_url: str = ""

    def __init__(self, name: str, profile_url: str, logo_url: str):
        self.name = name
        self.profile_url = profile_url
        self.logo_url = logo_url


class WebsiteISCRealEstateInfo:
    code: str = ""
    model: str = ""
    neighborhood: str = ""
    city: str = ""
    summary: str = ""
    url: str = ""
    bedrooms: str = ""
    suite: str = ""
    garage_slots: str = ""
    space: str = ""
    price: str = ""
    agency: WebsiteISCAgencyInfo = None

    def __init__(
        self,
        code: str,
        model: str,
        neighborhood: str,
        city: str,
        summary: str,
        url: str,
        bedrooms: str,
        suite: str,
        garage_slots: str,
        space: str,
        price: str,
        agency: WebsiteISCAgencyInfo,
    ):
        self.code = code
        self.model = model
        self.neighborhood = neighborhood
        self.city = city
        self.summary = summary
        self.url = url
        self.bedrooms = bedrooms
        self.suite = suite
        self.garage_slots = garage_slots
        self.space = space
        self.price = price
        self.agency = agency


class WebsiteISCFilter:
    property_type: List[str] = ""
    transaction_type: List[str] = ""
    city: str = ""
    neighborhood: List[str] = ""
    bedroom_quantity: List[str] = ""
    suite_quantity: List[str] = ""
    garage_slots_quantity: List[str] = ""
    min_price: str = ""
    max_price: str = ""
    min_area: str = ""
    max_area: str = ""

    def __init__(
        self,
        property_type: List[str],
        transaction_type: List[str],
        city: str,
        neighborhood: List[str],
        bedroom_quantity: List[str],
        suite_quantity: List[str],
        garage_slots_quantity: List[str],
        min_price: str,
        max_price: str,
        min_area: str,
        max_area: str,
    ):
        self.property_type = property_type
        self.transaction_type = transaction_type
        self.city = city
        self.neighborhood = neighborhood
        self.bedroom_quantity = bedroom_quantity
        self.suite_quantity = suite_quantity
        self.garage_slots_quantity = garage_slots_quantity
        self.min_price = min_price
        self.max_price = max_price
        self.min_area = min_area
        self.max_area = max_area

    def build_url_path(self) -> str:
        pass


class WebsiteISCPageContent:
    real_estate_list: List[WebsiteISCRealEstateInfo] = []
    total: int = 0
    page: int = 0
    total_pages: int = 0

    def __init__(
        self,
        real_estate_list: List[WebsiteISCRealEstateInfo],
        total: int,
        page: int,
        total_pages: int,
    ):
        self.real_estate_list = real_estate_list
        self.total = total
        self.page = page
        self.total_pages = total_pages


class WebcrawlerISCRealEstate:
    base_url = "https://www.imoveis-sc.com.br"

    def __init__(self):
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,pt;q=0.8,pt-BR;q=0.7",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        self.session = requests.session()

    def set_filter(self, filter: WebsiteISCFilter):
        self.filter = filter
        self._build_url()

    def _build_url(self):
        path = ""
        path += f"{self.filter.city}/"

        for i, city in enumerate(self.filter.transaction_type):
            if i != 0:
                path += "+"

            path += city

        path += "/"

        for i, property_type in enumerate(self.filter.property_type):
            if i != 0:
                path += "+"

            path += property_type

        path += "/"

        for i, neighborhood in enumerate(self.filter.neighborhood):
            if i != 0:
                path += "_"

            path += neighborhood

        tmp_path = ""
        for i, bedroom_qnt in enumerate(self.filter.bedroom_quantity):
            if i != 0:
                tmp_path += ","

            tmp_path += bedroom_qnt

        if tmp_path != "0":
            path += "/quartos/"
            path += tmp_path

        path += "?"
        path += f"valor={self.filter.min_price}-{self.filter.max_price}"
        path += "&"
        path += f"area={self.filter.min_area}-{self.filter.max_area}"

        tmp_path = ""
        for i, suites_qnt in enumerate(self.filter.suite_quantity):
            if i != 0:
                tmp_path += "%2C"

            if suites_qnt == "5+":
                tmp_path += "5%2B"
            else:
                tmp_path += suites_qnt

        if tmp_path != "0":
            path += "&"
            path += "suites="
            path += tmp_path

        tmp_path = ""
        for i, garare_slots_qnt in enumerate(self.filter.garage_slots_quantity):
            if i != 0:
                tmp_path += "%2C"

            if garare_slots_qnt == "5+":
                tmp_path += "5%2B"
            else:
                tmp_path += garare_slots_qnt

        if tmp_path != "0":
            path += "&"
            path += "vagas="
            path += tmp_path

        self.url = f"{self.base_url}/{path}"
        print(f"Webcrawler url: {self.url}")

    def crawl(
        self,
    ) -> Generator[WebsiteISCPageContent]:
        self.page = 1
        self.page_last = -1
        self.real_estate_count = -1
        self.real_estate_list = []

        while True:
            response = self.make_request()

            if self.page_last == -1 or self.real_estate_count == -1:
                [self.real_estate_count, self.page_last] = (
                    self.get_total_and_last_page_number(response)
                )

            print(f"Querying page {self.page} of {self.page_last}")

            tmp_real_estate_list = self.extract_info(response)

            if tmp_real_estate_list is None:
                tmp_real_estate_list = []

            print(f"Page: {self.page} - Real estate count: {len(tmp_real_estate_list)}")

            page_content = WebsiteISCPageContent(
                real_estate_list=tmp_real_estate_list,
                total=self.real_estate_count,
                page=self.page,
                total_pages=self.page_last,
            )

            yield page_content

            self.page += 1

            if self.page > self.page_last:
                break

            time.sleep(0.3)

    def get_total_and_last_page_number(
        self,
        page_content: str = "",
    ) -> Tuple[int, int]:
        total_number_real_estate = 0
        total_number_pages = 0

        soup = BeautifulSoup(
            page_content,
            "html.parser",
        )

        header_data = soup.find("div", class_="header-data")
        if header_data:
            count_span = header_data.find("span", class_="lista-imovel-count")
            total_number_real_estate = int(count_span.text.strip()) if count_span else 0
        else:
            total_number_real_estate = 0

        # get total number of pages
        navigation_div = soup.find(
            "div",
            class_="navigation",
        )

        if navigation_div:
            navigation_div = navigation_div.get_text(strip=True)
            match = re.search(
                r"de \d+",
                navigation_div,
            )

            if match:
                page_str = match.group()
                page_str = page_str.split(" ")[1]
                total_number_pages = int(page_str)
            else:
                total_number_pages = 1

        else:
            total_number_pages = 1

        return [total_number_real_estate, total_number_pages]

    def make_request(self) -> Optional[str]:
        url = self.url
        if self.page > 1:
            url += f"&page={self.page}"

        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
        except Exception as e:
            print(f"Error to get {url}. Error: ", e)
            return None

        if response.status_code != 200:
            print(f"Get request not succeed. Reason: {response.text}")
            return None

        return response.text

    def extract_info(
        self,
        page: str = "",
    ) -> List[WebsiteISCRealEstateInfo]:
        soup = BeautifulSoup(
            page,
            "html.parser",
        )
        imoveis_soup = soup.find_all(
            "div",
            class_="imovel-data",
        )

        if len(imoveis_soup) == 0:
            return None

        real_estate_list = []
        for imovel_tag in imoveis_soup:
            model = self.get_model(imovel_tag)
            code = self.get_code(imovel_tag)
            neighborhood = self.get_neighborhood(imovel_tag)
            city = self.get_city(imovel_tag)
            summary = self.get_summary(imovel_tag)
            url = self.get_url(imovel_tag)
            bedrooms = self.get_bedrooms(imovel_tag)
            suite = self.get_suite(imovel_tag)
            garage_slots = self.get_garage_slots(imovel_tag)
            space = self.get_space(imovel_tag)
            price = self.get_price(imovel_tag)
            agency = self.get_agency_info(imovel_tag)

            imovel_info = WebsiteISCRealEstateInfo(
                code=code,
                model=model,
                neighborhood=neighborhood,
                city=city,
                summary=summary,
                url=url,
                bedrooms=bedrooms,
                suite=suite,
                garage_slots=garage_slots,
                space=space,
                price=price,
                agency=agency,
            )

            real_estate_list.append(imovel_info)

        return real_estate_list

    def get_model(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            model = snnipet.find(
                "meta",
                itemprop="model",
            ).get("content")
        except:
            return ""

        return model

    def get_code(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            code = snnipet.find(
                "meta",
                itemprop="sku",
            ).get("content")
        except:
            return ""

        return code

    def get_neighborhood(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            neighboor = (
                snnipet.find(
                    "div",
                    class_="imovel-extra",
                )
                .find("strong")
                .text
            )
            neighboor = neighboor.split(",")[1]
            neighboor = neighboor.strip()
        except:
            return ""

        return neighboor

    def get_city(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            city = (
                snnipet.find(
                    "div",
                    class_="imovel-extra",
                )
                .find("strong")
                .text
            )
            city = city.split(",")[0]
            city = city.strip()
        except:
            return ""

        return city

    def get_summary(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            summary = snnipet.find(
                "meta",
                itemprop="name",
            ).get("content")
        except:
            return ""

        return summary

    def get_url(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            url = snnipet.find("a").get("href")
        except:
            return ""

        return url

    def get_bedrooms(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            beedrooms_li = snnipet.find(
                "i",
                class_="mdi-bed-king-outline",
            ).find_parent("li")
            beedrooms = beedrooms_li.find("strong").text
        except:
            return ""

        return beedrooms

    def get_suite(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            suite_li = snnipet.find(
                "i",
                class_="mdi-shower",
            ).find_parent("li")
            suite = suite_li.find("strong").text
        except:
            return ""

        return suite

    def get_garage_slots(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            gararge_slot_li = snnipet.find(
                "i",
                class_="mdi-car",
            ).find_parent("li")
            gararge_slot = gararge_slot_li.find("strong").text
        except:
            return ""

        return gararge_slot

    def get_space(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            space_slot_li = snnipet.find(
                "i",
                class_="mdi-arrow-expand",
            ).find_parent("li")
            space_slot = space_slot_li.find("strong").text
        except:
            return ""

        return space_slot

    def get_price(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        try:
            price = snnipet.find(
                "meta",
                itemprop="lowprice",
            ).get("content")
        except:
            return ""

        return price

    def get_agency_info(
        self,
        snnipet: element.Tag = "",
    ) -> str:
        agent_tag = snnipet.find("a", class_="imovel-anunciante")

        if agent_tag:
            link = agent_tag.get("href")

            title = agent_tag.get("title")
            title = re.sub(r"\s*-\s*\d+(\.\d+)?$", "", title)

            style = agent_tag.get("style", "")
            match = re.search(r"url\((.*?)\)", style)
            image_url = match.group(1) if match else None

            agency = WebsiteISCAgencyInfo(title, link, image_url)
            return agency

        else:
            return None


class WebcrawlerISCAgencyDetailsInfo:
    creci: str = ""
    phone_numbers: List[str] = []

    def __init__(self, creci: str, phone_numbers: List[str]):
        self.creci = creci
        self.phone_numbers = phone_numbers


class WebcrawlerISCAgencyDetails:
    def __init__(self):
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,pt;q=0.8,pt-BR;q=0.7",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        self.session = requests.session()

    def crawl(self, url: str) -> WebcrawlerISCAgencyDetailsInfo:
        self.url = url
        page_content = self.make_request()

        soup = BeautifulSoup(page_content, "html.parser")

        creci = self.get_creci(soup)
        phone_numbers = self.get_contact_numbers(soup)

        info = WebcrawlerISCAgencyDetailsInfo(creci, phone_numbers)
        return info

    def make_request(self) -> Union[str, None]:
        try:
            response = self.session.get(self.url, headers=self.headers, timeout=10)
        except Exception as e:
            print(f"Error to get {self.url}. Error: ", e)
            return None

        if response.status_code != 200:
            print(f"Get request to {self.url} succeed. Reason: {response.text}")
            return None

        return response.text

    def get_creci(self, page_soup) -> Union[str, None]:

        title_tag = page_soup.find("h1", class_="title")
        if title_tag is None:
            return None

        # Step 2: Extract the CRECI number from the span inside the title
        creci_span = title_tag.find("span", string=re.compile(r"CRECI:"))
        if creci_span is None:
            return None

        match = re.search(r"CRECI:\s*(\d+)", creci_span.text)
        if match:
            creci_number = match.group(1)
            return creci_number
        else:
            return None

    def get_contact_numbers(self, page_soup) -> List[str]:
        phone_links = page_soup.find_all("a", href=re.compile(r"^tel:\+"))
        if phone_links is None:
            return []

        phone_numbers = []
        for phone in phone_links:
            number = phone["href"]
            number = number.replace("tel:", "")
            phone_numbers.append(number)

        return phone_numbers


class WebcrawlerISCRealEstateDetailsInfo:
    images: List[str] = []
    condo_price: str = ""

    def __init__(self, images: List[str], condo_price: str):
        self.images = images
        self.condo_price = condo_price


class WebcrawlerISCRealEstateDetails:

    def __init__(self):
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,pt;q=0.8,pt-BR;q=0.7",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        self.session = requests.session()

    def crawl(self, url: str) -> WebcrawlerISCRealEstateDetailsInfo:
        self.url = url
        page_content = self.make_request()

        soup = BeautifulSoup(page_content, "html.parser")

        images = self.get_images(soup)
        condo_price = self.get_condo_price(soup)

        info = WebcrawlerISCRealEstateDetailsInfo(images, condo_price)

        return info

    def make_request(self) -> Union[str, None]:
        try:
            response = self.session.get(self.url, headers=self.headers, timeout=10)
        except Exception as e:
            print(f"Error to get {self.url}. Error: ", e)
            return None

        if response.status_code != 200:
            print(f"Get request to {self.url} succeed. Reason: {response.text}")
            return None

        return response.text

    def get_images(self, page_soup) -> List[str]:

        image_div = page_soup.find("div", class_="visualizar-galeria")
        if image_div is None:
            return []

        image_links = []
        for img in image_div.find_all("img"):
            # Check for both src and data-src attributes
            src = img.get("src") or img.get("data-src")
            if src:
                image_links.append(src)

        return image_links

    def get_condo_price(self, page_soup) -> Union[str, None]:
        price_div = page_soup.find("div", class_="visualizar-preco has-extra")

        if price_div is None:
            return 0.0

        if price_div:
            span_value = price_div.find("span").get_text(strip=True)
            return span_value
