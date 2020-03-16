from sqlalchemy.orm import sessionmaker
from scraping.spider.models import db_connect, create_table, Link

from helpers.helper import strip_html_tags


# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class SpiderPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.links = []

    def process_item(self, item, spider):
        """
        This method is called for every item pipeline component
        """
        session = self.Session()

        try:
            if len(item) == 6:
                link = Link()
                link.page_url = item["page_url"]
                link.link_url = item["link_url"]
                link.link_text = strip_html_tags(item["link_text"])
                link.x_position = item["x_position"]
                link.y_position = item["y_position"]
                link.in_list = item["in_list"]
                self.links.append(link)
            else:
                session.bulk_save_objects(self.links)
                session.commit()
                self.links = []
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        return item
