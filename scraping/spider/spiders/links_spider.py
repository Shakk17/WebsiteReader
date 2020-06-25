import random

import scrapy
from scrapy import signals

from helpers.printer import green, magenta
from helpers.scraper import scrape_links
from helpers.utility import add_scheme, get_domain, get_time


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
        url = response.url
        self.visited_links.append(url)
        print(magenta(f"{get_time()} ({len(self.visited_links)}) Scraping {response.url}"))

        page_links_items = scrape_links(html=response.body, url=url)

        # Shuffle the links to improve variance.
        random.shuffle(page_links_items)

        # Save all the links in the database.
        for page_link_item in page_links_items:
            yield page_link_item

        print(f"({get_domain(url)} - {len(self.visited_links)}) {len(page_links_items)} links saved.")

        # Analyze each link found in the page.
        for (i, page_link_item) in enumerate(page_links_items):
            link_url = add_scheme(page_link_item["link_url"])

            # If the link has not been visited yet, visit it.
            if link_url not in self.visited_links and self.allowed_domains[0] in link_url:
                yield response.follow(link_url, callback=self.parse)

    def spider_closed(self, spider):
        print(green(f"[CRAWLER] Crawling of {self.start_urls[0]} finished."))
        spider.logger.info('Spider closed: %s', spider.name)
