from datetime import datetime

from databases.database_handler import Database
from helpers.utility import remove_scheme


def db_insert_page(url, simple_html):
    """
    This method inserts a web page in the pages table of the database.
    """
    url = remove_scheme(url)
    sql = """INSERT INTO pages (url, simple_html, last_visit, parsed_html) 
                VALUES (?, ?, ?, ?)"""
    Database().conn.cursor().execute(
        sql, (url, simple_html, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "In progress."))


def db_add_parsed_html_to_page(url, parsed_html):
    url = remove_scheme(url)
    sql = "UPDATE pages SET parsed_html=? WHERE url LIKE ?"
    Database().conn.cursor().execute(sql, (parsed_html, url))


def db_add_topic_to_page(url, topic):
    url = remove_scheme(url)
    sql = "UPDATE pages SET topic=? WHERE url LIKE ?"
    Database().conn.cursor().execute(sql, (topic, url))


def db_add_language_to_page(url, language):
    url = remove_scheme(url)
    sql = "UPDATE pages SET language=? WHERE url LIKE ?"
    Database().conn.cursor().execute(sql, (language, url))


def db_add_clean_text_to_page(url, clean_text):
    """
    This method updates a page in the pages table of the database.
    :param url: A string representing the URL of the web page to update.
    :param clean_text: A string representing the clear main text of the web page to insert.
    """
    url = remove_scheme(url)
    sql = "UPDATE pages SET clean_text=? WHERE url LIKE ?"
    Database().conn.cursor().execute(sql, (clean_text, url))


def db_delete_page(url):
    """
    This method deletes a page from the pages table of the database.
    :param url: A string containing the URl of the web page to delete.
    :return: None
    """
    url = remove_scheme(url)
    sql = "DELETE FROM pages WHERE url LIKE ?"
    Database().conn.cursor().execute(sql, (url,))


def db_get_page(url):
    """
    This method returns a tuple containing info about the last visit of a web page.
    :param url: A string containing the URL of the web page.
    :return: A tuple (url, topic, summary, language, simple_html, parsed_html, clear_text, last_visit) or None.
    """
    url = remove_scheme(url)
    sql = "SELECT * FROM pages WHERE url LIKE ?"
    cur = Database().conn.cursor().execute(sql, (url,))
    result = cur.fetchone()
    return result
