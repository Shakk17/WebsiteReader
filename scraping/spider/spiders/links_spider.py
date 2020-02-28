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
        # Unpack the string in order to read the fields.
        # FORMAT: href * text * x_position * y_position $
        links = [link.split("*") for link in links]
        links = list(filter(lambda x: len(x) == 4, links))

        # Analyze each link found in the page.
        for (i, link) in enumerate(links):
            # If the link has not been visited yet, visit it.
            if link[0] not in self.visited_links and self.allowed_domains[0] in link[0]:
                self.visited_links.append(link[0])
                yield response.follow(link[0], callback=self.parse)

    def spider_closed(self, spider):
        print(f"Scraping of {self.start_urls[0]} finished.")
        spider.logger.info('Spider closed: %s', spider.name)
