from sqlalchemy.orm import sessionmaker
from scraping.spider.models import db_connect, create_table, Link

from helper import strip_html_tags


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

    def process_item(self, item, spider):
        """Save quotes in the database
        This method is called for every item pipeline component
        """
        session = self.Session()
        link = Link()
        link.page_url = item["page_url"]
        link.link_url = item["link_url"]
        link.link_text = strip_html_tags(item["link_text"])
        link.x_position = item["x_position"]
        link.y_position = item["y_position"]

        # Do not save the link in the DB if these conditions apply.
        if link.link_text == "" or link.y_position > 1080 or link.y_position == 0:
            session.close()
            return item


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
            session.add(link)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item
