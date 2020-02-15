import scrapy
from helper import get_domain

from scraping.spider.items import UrlItem
from scrapy import signals


class LinksSpider(scrapy.Spider):
    name = "links"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(LinksSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)

        # Get values passed as parameters.
        settings = crawler.settings
        url = settings.get('url')
        # Get the domain from the url.
        domain = get_domain(url)

        spider.allowed_domains = [domain]
        spider.start_urls = [url]

        # Instantiate the class.
        return spider

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visited_links = []

    def parse(self, response):
        # Decode the bytes string contained in the response body.
        links = response.body.decode(encoding='UTF-8').split("$")
        url_item = UrlItem()

        # Analyze each link found in the page.
        for (i, link) in enumerate(links):
            # Unpack the string in order to read the fields.
            # FORMAT: href * text * x_position * y_position $

            fields = link.split("*")

            if len(fields) != 4:
                continue

            url_item["link_url"] = fields[0]
            url_item["link_text"] = fields[1]
            url_item["x_position"] = fields[2]
            url_item["y_position"] = fields[3]
            url_item["page_url"] = response.url

            # If the link has not been visited yet, visit it.
            if fields[0] not in self.visited_links and self.allowed_domains[0] in fields[0]:
                self.visited_links.append(fields[0])
                yield response.follow(fields[0], callback=self.parse)

            # We save the link in the DB only if it belongs to the domain.
            if self.allowed_domains[0] in fields[0]:
                yield url_item
            else:
                yield None

    def spider_closed(self, spider):
        print(f"Scraping of {self.start_urls[0]} finished.")
        spider.logger.info('Spider closed: %s', spider.name)
