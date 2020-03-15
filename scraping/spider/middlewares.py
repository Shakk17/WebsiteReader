# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By

from helpers.helper import get_domain
from helpers.printer import magenta
from helpers.renderer import get_firefox_browser
from helpers.renderer import StaleElementReferenceException
from scraping.spider.items import UrlItem


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
        # Called for each request that goes through the downloader middleware.

        spider.visited_links.append(request.url)
        print(magenta(f"({len(spider.visited_links)}) Scraping {request.url}"))

        browser = get_firefox_browser()
        browser.get(request.url)
        body = browser.page_source
        url = browser.current_url

        # Extract all links from the page.
        links = browser.find_elements(By.XPATH, '//a[@href]')
        links_bs4 = BeautifulSoup(body, "lxml").find_all("a")
        links_bs4 = list(filter(lambda x: x.get("href") is not None, links_bs4))

        # Create a string containing all the links in the page, with location.
        # FORMAT: href * text * x_position * y_position $
        string_links = ""

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

        return HtmlResponse(url, body=bytes_links, encoding='utf-8', request=request)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Decode the bytes string contained in the response body.
        links = response.body.decode(encoding='UTF-8').split("$")
        # Unpack the string in order to read the fields.
        # FORMAT: href * text * x_position * y_position $
        links = [link.split("*") for link in links]
        links = list(filter(lambda x: len(x) == 5, links))

        num_links = 0
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
                num_links += 1
                # Call pipeline.
                pipeline = spider.crawler.engine.scraper.itemproc
                pipeline.process_item(url_item, self)

        print(f"({len(spider.visited_links)}) {num_links} links saved.")
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
        print(magenta(f"[CRAWLER] Crawling of {spider.start_urls[0]} started."))
        spider.logger.info('Spider opened: %s' % spider.name)
