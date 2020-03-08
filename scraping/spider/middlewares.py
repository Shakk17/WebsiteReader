# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from helpers.renderer import StaleElementReferenceException
from helpers.renderer import By
from seleniumwire import webdriver

from helpers.helper import get_domain
from scraping.spider.items import UrlItem

from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=500x1024')
options.add_argument(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36")
# Avoid loading images.
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

# HEROKU
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
# LOCAL:
# driver = webdriver.Chrome(options=options)

driver.header_overrides = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7,es;q=0.6,fr;q=0.5,nl;q=0.4,sv;q=0.3",
    "Dnt": "1",
    "Referer": "https://www.google.com/",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}


class SpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of installed downloader middleware will be called
        driver.get(request.url)

        body = driver.page_source

        # Create a string containing all the links in the page, with location.
        # FORMAT: href * text * x_position * y_position $
        string_links = ""

        # Extract all links from the page.
        links = driver.find_elements(By.XPATH, '//a[@href]')
        links_bs4 = BeautifulSoup(body, "lxml").find_all("a")
        links_bs4 = list(filter(lambda x: x.get("href") is not None, links_bs4))

        for i, link in enumerate(links):
            try:
                href = link.get_attribute("href")
                text = link.get_attribute("innerHTML")
                x_position = str(link.location.get('x'))
                y_position = str(link.location.get('y'))
                # True if the element is contained in a list container.
                try:
                    in_list = "li" in [parent.name for parent in links_bs4[i].parents]
                except IndexError:
                    in_list = False

                # If the link links to the same page, discard it.
                hash_position = link.get_attribute("href").find("#")
                if link.get_attribute("href")[:hash_position] == request.url:
                    continue

                # Add the link to the string of bytes to be returned.
                string_links += href + "*" + text + "*" + x_position + "*" + y_position + "*" + str(int(in_list)) + "$"
            except StaleElementReferenceException:
                continue

        # Transform the string to binary code in order to be passed as a parameter.
        bytes_links = string_links.encode(encoding='UTF-8')

        return HtmlResponse(driver.current_url, body=bytes_links, encoding='utf-8', request=request)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Decode the bytes string contained in the response body.
        links = response.body.decode(encoding='UTF-8').split("$")
        # Unpack the string in order to read the fields.
        # FORMAT: href * text * x_position * y_position $
        links = [link.split("*") for link in links]
        links = list(filter(lambda x: len(x) == 5, links))

        # Analyze each link found in the page.
        for (i, link) in enumerate(links):
            url_item = UrlItem()
            url_item["link_url"] = link[0]
            url_item["link_text"] = link[1]
            url_item["x_position"] = link[2]
            url_item["y_position"] = link[3]
            url_item["page_url"] = response.url
            url_item["in_list"] = link[4]
            # We save the link in the DB only if it belongs to the domain.
            if get_domain(response.url) in link[0]:
                # Call pipeline.
                pipeline = spider.crawler.engine.scraper.itemproc
                pipeline.process_item(url_item, self)
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
