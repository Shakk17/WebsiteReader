from sqlalchemy import (
    Integer, String)
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def db_connect(domain_name):
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine("sqlite:///databases/" + domain_name + ".db")


def create_table(engine):
    Base.metadata.create_all(engine)


class URL(Base):
    __tablename__ = "url"

    id = Column(Integer, primary_key=True)
    text = Column('text', String(150))
    url_anchor = Column('url_anchor', String(150))
    found_in_page = Column('found_in_page', String(150))
    x_position = Column('x_position', Integer)
    y_position = Column('y_position', Integer)
