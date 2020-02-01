import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor

from spider.items import UrlItem


class QuotesSpider(scrapy.Spider):
    name = "urls"
    allowed_domains = ["toscrape.com"]
    start_urls = ['http://quotes.toscrape.com/']

    links = []

    def parse(self, response):
        urls = response.css('a::attr(href)')

        le = LinkExtractor()
        links = le.extract_links(response)
        url_item = UrlItem()

        for link in links:
            url_item["url_anchor"] = link.url
            url_item["found_in_page"] = response.url
            # go to the author page and pass the current collected quote info
            yield url_item
