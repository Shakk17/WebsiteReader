from scrapy import cmdline
from scrapy.crawler import CrawlerProcess

from databases.database_handler import Database
from scraping.spider.spiders.links_spider import LinksSpider


class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url

    def run(self):
        process = CrawlerProcess()
        process.crawl(LinksSpider, )
        process.start()
        command = f"scrapy crawl links -s url={self.start_url}"
        cmdline.execute(command.split())
        db = Database()
        db.insert_website(url=self.start_url)


Crawler("http://www.polimi.it/").run()
