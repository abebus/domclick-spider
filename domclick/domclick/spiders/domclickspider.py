import scrapy
from domclick.items import DomclickItem
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from domclick.http import SeleniumRequest

class DomclickspiderSpider(scrapy.Spider):
    name = "domclickspider"
    allowed_domains = ["domclick.ru"]

    def __init__(self):
        self.driver: Firefox
        self.driver = None

    def start_requests(self):
        req = SeleniumRequest(
            url='https://kazan.domclick.ru/search?deal_type=sale&category=living&offer_type=layout&offer_type=flat&aids=1967&rooms=1&offset=0',
            callback=self.parse_main)
        yield req

    def parse_details(self, response):
        show_telephone = response.css('div[class="telephony_developerContactButton"]')
        button = show_telephone.css('button')
        self.driver.execute_script("arguments[0].click();", button)
        number = show_telephone.css('a').attrib['href']
        developer = response.css('div[class="sc_developerName"]')
        pass

    def parse_main(self, response):
        for flat in response.css('div[data-test="product-snippet"]'):
            a_tag = flat.css('div[data-test="product-snippet-property-offer"]::text').get()
            url = a_tag.attrib['href'].get()
            rooms, area, floor = a_tag.css('span::text').getall()
            price = flat.css('div[data-e2e-id="product-snippet-price-sale"] > p::text').get()
            page = flat.xpath('//ul[contains(@class, "pgnt-list")]/li/div[contains(@class, "pgnt-selected")').get()
            detailed_page = yield from self.parse_details(SeleniumRequest(url))

