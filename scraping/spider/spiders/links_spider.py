import scrapy
from helper import get_domain

from scraping.spider.items import UrlItem
from scrapy import signals


class LinksSpider(scrapy.Spider):
    name = "links"
    MAX_COUNT = 30
    visited_links = []

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

    def parse(self, response):
        # Decode the bytes string contained in the response body.
        links = response.body.decode(encoding='UTF-8').split("$")
        # Unpack the string in order to read the fields.
        # FORMAT: href * text * x_position * y_position * in_list $
        links = [link.split("*") for link in links]
        links = list(filter(lambda x: len(x) == 5, links))

        # Analyze each link found in the page.
        for (i, link) in enumerate(links):
            # Skip PDF files.
            if link[0].endswith("pdf"):
                continue
            # Stop crawling after a while.
            if len(self.visited_links) > self.MAX_COUNT:
                return
            # If the link has not been visited yet, visit it.
            if link[0] not in self.visited_links and self.allowed_domains[0] in link[0]:
                self.visited_links.append(link[0])
                yield response.follow(link[0], callback=self.parse)

    def spider_closed(self, spider):
        print(f"Scraping of {self.start_urls[0]} finished.")
        spider.logger.info('Spider closed: %s', spider.name)
