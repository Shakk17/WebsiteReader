import os
import pathlib

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

dir_path = pathlib.Path(__file__).parent.absolute()
# Change working directory to the folder of this file.
os.chdir(dir_path)
# Connect to db. Create it if not existing.
engine = create_engine(f"sqlite:///database.db")
# Define session.
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()


def create_tables():
    Base.metadata.create_all(engine)


class PageLink(Base):
    __tablename__ = "page_links"

    id = Column(Integer, primary_key=True)
    page_url = Column('page_url', String(200))
    link_url = Column('link_url', String(200))
    link_text = Column('link_text', String(200))
    x_position = Column('x_position', Integer)
    y_position = Column('y_position', Integer)
    in_list = Column('in_list', Integer)
    in_nav = Column('in_nav', Integer)


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    user = Column('user', String(50))
    action = Column("action", String(50))
    url = Column("url", String(200))
    timestamp = Column("timestamp", String(50))


class Website(Base):
    __tablename__ = "websites"

    domain = Column(String(50), primary_key=True)
    last_crawled_on = Column("last_crawled_on", String(50))


class Page(Base):
    __tablename__ = "pages"

    url = Column('url', String(50), primary_key=True)
    topic = Column('topic', String(50))
    language = Column('language', String(50))
    simple_html = Column('simple_html', String(50))
    parsed_html = Column('parsed_html', String(50))
    clean_text = Column('clean_text', String(50))
    last_visit = Column('last_visit', String(50))


class TextLink(Base):
    __tablename__ = "text_links"

    page_url = Column(String(200), primary_key=True)
    link_num = Column(Integer, primary_key=True)
    position = Column(Integer)
    link_text = Column(String(200))
    link_url = Column(String(200))


class Form(Base):
    __tablename__ = "forms"

    page_url = Column(String(200), primary_key=True)
    form_num = Column(Integer, primary_key=True)
    method = Column(String(200))
    action = Column(String(200))
    input_num = Column(Integer)
    input_name = Column(String(200))
    input_text = Column(String(200))


class Bookmark(Base):
    __tablename__ = "bookmarks"

    url = Column(String(200), primary_key=True)
    name = Column(String(200))
    user = Column(String(200), primary_key=True)
    UniqueConstraint('name', 'user')


class Functionality(Base):
    __tablename__ = "functionality"

    page_url = Column(String(200), primary_key=True)
    type = Column(String(200), primary_key=True)
    name = Column(String(200), primary_key=True)
    link_url = Column(String(200))
    score = Column(Integer)
