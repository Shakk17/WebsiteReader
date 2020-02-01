from scrapy.item import Item, Field
from scrapy.loader.processors import MapCompose, TakeFirst
from datetime import datetime


class UrlItem(Item):
    url_anchor = Field()
    found_in_page = Field()
