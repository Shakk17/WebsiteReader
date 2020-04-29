from sqlalchemy import (
    Integer, String)
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base

import os
from pathlib import Path

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    path = Path(os.getcwd())
    return create_engine(f"sqlite:///{path.parent}/databases/database.db", connect_args={'timeout': 15})


def create_table(engine):
    Base.metadata.create_all(engine)


class Link(Base):
    __tablename__ = "page_links"

    id = Column(Integer, primary_key=True)
    page_url = Column('page_url', String(200))
    link_url = Column('link_url', String(200))
    link_text = Column('link_text', String(200))
    x_position = Column('x_position', Integer)
    y_position = Column('y_position', Integer)
    in_list = Column('in_list', Integer)

