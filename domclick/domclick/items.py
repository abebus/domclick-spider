# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass

@dataclass
class Details:
    number: str
    description: str
    realtor: str

@dataclass
class DomclickItem:
    url: str
    name: str
    price: str
    address: str
    page: int
    details: Details
