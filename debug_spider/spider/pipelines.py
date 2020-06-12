from sqlalchemy.orm import sessionmaker
from spider.models import db_connect, create_table, Link

import tldextract


# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class SpiderPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        # Get values passed as parameters.
        settings = crawler.settings
        url = settings.get('url')
        extracted_domain = tldextract.extract(url)
        domain = "{}.{}".format(extracted_domain.domain, extracted_domain.suffix)

        # Instantiate the pipeline.
        return cls()

    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        return item
