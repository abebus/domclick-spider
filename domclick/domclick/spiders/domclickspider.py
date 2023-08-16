'''
Должно работать в ТЕОРИИ. Из-за 403 не могу проверить
'''
import time

import scrapy
from domclick.items import DomclickItem, Details
from undetected_chromedriver import Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from domclick.http import SeleniumRequest
import logging

API_KEY = '3c58cd96-1010-4ea4-96da-2ca75ed5d254'
DOMCLICK_URL = 'https://kazan.domclick.ru/search?deal_type=sale&category=living&offer_type=layout&offer_type=flat&aids=1967&rooms=1&offset=0'


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
        try:
            show_telephone = self.driver.find_element(By.CSS_SELECTOR, 'div[class="telephony_developerContactButton"]')
            button = show_telephone.find_element(By.CSS_SELECTOR, 'button')
        except:
            pass
        try:
            button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-e2e-id="agent-show-number"]')
        except:
            pass
        try:
            self.driver.execute_script("arguments[0].click();", button)
            number = show_telephone.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        except:
            number = None
        try:
            description = self.driver.find_element(By.CSS_SELECTOR, 'div[id="description').text
            realtor = self.driver.find_element(By.CSS_SELECTOR, 'a[data-e2e-id="agent_card_link"]').text
        except:
            description = None
            realtor = None
        return Details(number=number, description=description, realtor=realtor)

    def click_next(self):
        try:
            self.driver.execute_script(r'window.scrollTo(0, document.body.scrollHeight);')
            next_page_button = self.driver.find_element(By.CSS_SELECTOR, 'div[data-e2e-id="paginate-next-btn"]')
            self.driver.execute_script("arguments[0].click();", next_page_button)
        except EC.StaleElementReferenceException:
            self.click_next()

    def do(self, flat):
        logging.info('flats found')
        try:
            a_tag = flat.find_element(By.CSS_SELECTOR, 'a[data-test="product-snippet-property-offer"]')
        except:
            a_tag = None
        try:
            url = a_tag.get_attribute('href')
        except:
            url = None
        try:
            name = ' '.join(list(map(lambda x: x.text, a_tag.find_elements(By.CSS_SELECTOR, 'span'))))
        except:
            name = None
        try:
            address = self.driver.find_element(By.CSS_SELECTOR, 'span[data-e2-id="product-snippet-address"]').text
        except:
            address = None
        try:
            price = flat.find_element(By.CSS_SELECTOR, 'div[data-e2e-id="product-snippet-price-sale"] > p').text
        except:
            price = None
        try:
            page = flat.find_element(By.XPATH,
                                     '//ul[contains(@class, "pgnt-list")]/li/div[contains(@class, "pgnt-selected")]').text
        except:
            page = -1
        try:
            detailed_page = self.parse_details(SeleniumRequest(url=url, callback=None))
        except:
            detailed_page = None
        return address, url, name, price, page, detailed_page

    def parse_main(self, response):
        if self.driver is None:
            self.driver = response.meta['driver']
        while True:
            try:
                self.driver.execute_script(r'window.scrollTo(0, document.body.scrollHeight);')
                button = self.driver.find_element(By.CSS_SELECTOR, 'div[data-e2e-id="next-offers-button"]')
                self.driver.execute_script("arguments[0].click();", button)
            except:
                break

            # WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-e2e-id="next-offers-button"]')))
        # WebDriverWait(self.driver, 20).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e-id="paginate-next-btn"]')))

        for flat in self.driver.find_elements(By.CSS_SELECTOR, 'div[data-test="product-snippet"]'):
            address, url, name, price, page, detailed_page = self.do(flat)
            yield DomclickItem(address=address, url=url, name=name, price=price, page=int(page), details=detailed_page)
            self.click_next()

