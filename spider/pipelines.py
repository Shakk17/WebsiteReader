from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from spider.models import db_connect, create_table, URL

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
        return cls(url=domain)

    def __init__(self, url):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect(url)
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save quotes in the database
        This method is called for every item pipeline component
        """
        session = self.Session()
        url = URL()
        url.text = item["text"]
        url.url_anchor = item["url_anchor"]
        url.found_in_page = item["found_in_page"]
        url.x_position = item["x_position"]
        url.y_position = item["y_position"]

        ''' check whether the author exists
        exist_author = session.query(Author).filter_by(name=author.name).first()
        if exist_author is not None:  # the current author exists
            quote.author = exist_author
        else:
            quote.author = author '''

        '''# check whether the current quote has tags or not
        if "tags" in item:
            for tag_name in item["tags"]:
                tag = Tag(name=tag_name)
                # check whether the current tag already exists in the database
                exist_tag = session.query(Tag).filter_by(name=tag.name).first()
                if exist_tag is not None:  # the current tag exists
                    tag = exist_tag
                quote.tags.append(tag)'''

        try:
            session.add(url)

            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item
