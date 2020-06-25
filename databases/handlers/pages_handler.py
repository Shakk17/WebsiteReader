from datetime import datetime

from sqlalchemy.exc import IntegrityError

from databases.models import Page, db_session, engine
from helpers.utility import remove_scheme


def db_insert_page(url, simple_html):
    """
    This method inserts a web page in the pages table of the database.
    """
    url = remove_scheme(url)
    page = Page(url=url, simple_html=simple_html,
                last_visit=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), parsed_html="In progress.")
    session = db_session()
    try:
        session.add(page)
        session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()


def db_add_parsed_html_to_page(url, parsed_html):
    url = remove_scheme(url)
    sql = "UPDATE pages SET parsed_html=:parsed_html WHERE url LIKE :url"
    engine.connect().execute(sql, parsed_html=parsed_html, url=url)


def db_add_topic_to_page(url, topic):
    url = remove_scheme(url)
    sql = "UPDATE pages SET topic=:topic WHERE url LIKE :url"
    engine.connect().execute(sql, topic=topic, url=url)


def db_add_language_to_page(url, language):
    url = remove_scheme(url)
    sql = "UPDATE pages SET language=:language WHERE url LIKE :url"
    engine.connect().execute(sql, language=language, url=url)


def db_add_clean_text_to_page(url, clean_text):
    """
    This method updates a page in the pages table of the database.
    :param url: A string representing the URL of the web page to update.
    :param clean_text: A string representing the clear main text of the web page to insert.
    """
    url = remove_scheme(url)
    sql = "UPDATE pages SET clean_text=:clean_text WHERE url LIKE :url"
    engine.connect().execute(sql, clean_text=clean_text, url=url)


def db_delete_page(url):
    """
    This method deletes a page from the pages table of the database.
    :param url: A string containing the URl of the web page to delete.
    :return: None
    """
    url = remove_scheme(url)
    sql = "DELETE FROM pages WHERE url LIKE :url"
    engine.connect().execute(sql, url=url)


def db_get_page(url):
    """
    This method returns a tuple containing info about the last visit of a web page.
    :param url: A string containing the URL of the web page.
    :return: A tuple (url, topic, summary, language, simple_html, parsed_html, clear_text, last_visit) or None.
    """
    url = remove_scheme(url)
    sql = "SELECT * FROM pages WHERE url LIKE :url"
    result = engine.connect().execute(sql, url=url).fetchone()
    return result
