from django.test import SimpleTestCase

from search.webcrawler_isc import WebsiteISCFilter, WebcrawlerISCRealEstate


class TestWebCrawlerISC(SimpleTestCase):

    def test_url_generation_1(self):
        isc_filter = WebsiteISCFilter(
            property_type=["apartamento", "casa", "terreno"],
            transaction_type=["comprar", "alugar"],
            city="blumenau",
            neighborhood=["agua-verde", "bom-retiro", "centro", "fidelis"],
            bedroom_quantity=["1"],
            suite_quantity=["1"],
            garage_slots_quantity=["1"],
            min_price=500000,
            max_price=600000,
            min_area=35,
            max_area=85,
        )

        crawler = WebcrawlerISCRealEstate()
        crawler.set_filter(isc_filter)

        expected_url = "https://www.imoveis-sc.com.br/blumenau/comprar+alugar/apartamento+casa+terreno/agua-verde_bom-retiro_centro_fidelis/quartos/1?valor=500000-600000&area=35-85&suites=1&vagas=1"
        self.assertEqual(crawler.url, expected_url)

    def test_url_generation_2(self):
        isc_filter = WebsiteISCFilter(
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
        crawler.set_filter(isc_filter)

        expected_url = "https://www.imoveis-sc.com.br/blumenau/comprar+alugar/apartamento+casa+terreno/agua-verde_bom-retiro_centro_fidelis/quartos/3,4,5+?valor=500000-1200000&area=35-95&suites=1%2C4%2C5%2B&vagas=1%2C4%2C5%2B"
        self.assertEqual(crawler.url, expected_url)
