import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor

from spider.items import UrlItem


class QuotesSpider(scrapy.Spider):
    name = "urls"
    allowed_domains = ["toscrape.com"]
    start_urls = ['http://quotes.toscrape.com/']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visited_links = []

    def parse(self, response):
        le = LinkExtractor()
        links = le.extract_links(response)
        url_item = UrlItem()

        for link in links:
            url_item["text"] = link.text
            url_item["url_anchor"] = link.url
            url_item["found_in_page"] = response.url

            if link.url not in self.visited_links:
                self.visited_links.append(link.url)
                yield response.follow(link.url, callback=self.parse)

            yield url_item

