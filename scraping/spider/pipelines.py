from helpers.utility import remove_scheme
from databases.models import PageLink, db_session


# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class SpiderPipeline(object):

    def __init__(self):
        self.Session = db_session

    def process_item(self, item, spider):
        """
        This method is called for every item pipeline component
        """
        session = self.Session()

        try:
            link = PageLink()
            link.page_url = remove_scheme(item["page_url"])
            link.link_url = remove_scheme(item["link_url"])
            link.link_text = item["link_text"]
            link.in_list = item["in_list"]
            link.in_nav = item["in_nav"]
            session.add(link)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        return item
