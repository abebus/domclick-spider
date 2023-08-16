'''
Должно работать в ТЕОРИИ. Из-за 403 не могу проверить
'''

import scrapy
from domclick.items import DomclickItem, Details
from undetected_chromedriver import Chrome
from domclick.http import SeleniumRequest
from urllib.parse import urlencode
import logging

API_KEY = '3c58cd96-1010-4ea4-96da-2ca75ed5d254'
DOMCLICK_URL = 'https://kazan.domclick.ru/search?deal_type=sale&category=living&offer_type=layout&offer_type=flat&aids=1967&rooms=1&offset=0'

def get_scrapeops_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url
class DomclickspiderSpider(scrapy.Spider):
    name = "domclickspider"

    def __init__(self):
        self.driver: Chrome
        self.driver = None

    def start_requests(self):
        req = SeleniumRequest(
            url=DOMCLICK_URL,
            callback=self.parse_main)
        yield req

    def parse_details(self, response):
        if self.driver is None:
            self.driver = response.meta['driver']
        show_telephone = response.css('div[class="telephony_developerContactButton"]')
        button = show_telephone.css('button')
        self.driver.execute_script("arguments[0].click();", button)
        number = show_telephone.css('a').attrib['href'].get()
        description = response.css('div[id="description"]::text').get()
        realtor = response.css('a[data-e2e-id="agent_card_link"]::text').get()
        yield Details(number=number, description=description, realtor=realtor)

    def parse_main(self, response):
        if self.driver is None:
            self.driver = response.meta['driver']
        for flat in response.css('div[data-test="product-snippet"]'):
            logging.info('flats found')
            a_tag = flat.css('div[data-test="product-snippet-property-offer"]::text').get()
            url = a_tag.attrib['href'].get()
            rooms, area, floor = a_tag.css('span::text').getall()
            name = ' '.join((rooms, area, floor))
            price = flat.css('div[data-e2e-id="product-snippet-price-sale"] > p::text').get()
            page = flat.xpath('//ul[contains(@class, "pgnt-list")]/li/div[contains(@class, "pgnt-selected")').get()
            detailed_page = yield from self.parse_details(SeleniumRequest(url))
            yield DomclickItem(url=url, name=name, price=price, page=int(page), details=detailed_page)
            next_page_button = response.css('div[data-e2e-id="paginate-next-btn"]')
            self.driver.execute_script("arguments[0].click();", next_page_button)
        else:
            logging.info('NO flats found')