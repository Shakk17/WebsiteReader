import scrapy
from scrapy import signals

from helpers.helper import get_domain
from helpers.printer import magenta


class LinksSpider(scrapy.Spider):
    name = "links"
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
            link_url = link[0]

            # Skip PDF files.
            if link_url[-3:] in ["pdf", "jpg", "png"]:
                continue

            # If the link has not been visited yet, visit it.
            if link_url not in self.visited_links and self.allowed_domains[0] in link_url:
                yield response.follow(link_url, callback=self.parse)

    def spider_closed(self, spider):
        print(magenta(f"[CRAWLER] Crawling of {self.start_urls[0]} finished."))
        spider.logger.info('Spider closed: %s', spider.name)
