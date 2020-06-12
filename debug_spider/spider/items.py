from scrapy.item import Item, Field
from scrapy.loader.processors import MapCompose, TakeFirst
from datetime import datetime


class UrlItem(Item):
    page_url = Field()
    link_url = Field()
    link_text = Field()
    x_position = Field()
    y_position = Field()
    in_list = Field()
