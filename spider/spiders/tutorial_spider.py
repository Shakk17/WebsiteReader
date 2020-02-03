import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider

from spider.items import UrlItem


class QuotesSpider(scrapy.Spider):
    name = "urls"
    allowed_domains = ["polimi.it"]
    start_urls = ['https://www.polimi.it/']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visited_links = []

    def parse(self, response):
        le = LinkExtractor()
        links = le.extract_links(response)
        url_item = UrlItem()

        # Analyze each link found in the page.
        for link in links:
            url_item["text"] = link.text
            url_item["url_anchor"] = link.url
            url_item["found_in_page"] = response.url

            # If the link has not been visited yet, visit it.
            if link.url not in self.visited_links and self.allowed_domains[0] in link.url:
                self.visited_links.append(link.url)
                yield response.follow(link.url, callback=self.parse)

            # We save the link in the DB only if it belongs to the domain.
            if self.allowed_domains[0] in link.url:
                yield url_item
            else:
                yield None

