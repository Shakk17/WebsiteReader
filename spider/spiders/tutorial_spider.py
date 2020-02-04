import scrapy
import tldextract
from scrapy.linkextractors import LinkExtractor

from spider.items import UrlItem


class QuotesSpider(scrapy.Spider):
    name = "urls"
    allowed_domains = ["polimi.it"]
    start_urls = ['https://www.polimi.it/']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Get values passed as parameters.
        settings = crawler.settings
        url = settings.get('url')
        # Get the domain from the url.
        extracted_domain = tldextract.extract(url)
        domain = "{}.{}".format(extracted_domain.domain, extracted_domain.suffix)

        cls.allowed_domains = [domain]
        cls.start_urls = [url]

        # Instantiate the class.
        return cls()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visited_links = []

    def parse(self, response):
        # Decode the bytes string contained in the response body.
        links = response.body.decode(encoding='UTF-8').split("$")
        url_item = UrlItem()

        # Analyze each link found in the page.
        for link in links:
            # Unpack the string in order to read the fields.
            # FORMAT: href * text * x_position * y_position $
            fields = link.split("*")
            url_item["url_anchor"] = url_anchor = fields[0]
            url_item["text"] = text = fields[1]
            url_item["x_position"] = x_position = fields[2]
            url_item["y_position"] = y_position = fields[3]
            url_item["found_in_page"] = response.url

            # If the link has not been visited yet, visit it.
            if url_anchor not in self.visited_links and self.allowed_domains[0] in url_anchor:
                self.visited_links.append(url_anchor)
                yield response.follow(url_anchor, callback=self.parse)

            # We save the link in the DB only if it belongs to the domain.
            if self.allowed_domains[0] in url_anchor:
                yield url_item
            else:
                yield None
