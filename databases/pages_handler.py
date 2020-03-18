from datetime import datetime

from databases.database_handler import Database


def db_insert_page(url, topic, language, simple_html):
    """
    This method inserts a web page in the pages table of the database.
    """
    sql = """INSERT INTO pages (url, topic, language, simple_html, last_visit) 
                VALUES (?, ?, ?, ?, ?)"""
    Database().conn.cursor().execute(
        sql, (url, topic, language, simple_html, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def db_add_parsed_html_to_page(url, parsed_html):
    sql = "UPDATE pages SET parsed_html=? WHERE url LIKE ?"
    Database().conn.cursor().execute(sql, (parsed_html, url))


def db_update_page(url, clean_text):
    """
    This method updates a page in the pages table of the database.
    :param url: A string representing the URL of the web page to update.
    :param clean_text: A string representing the clear main text of the web page to insert.
    """
    sql = "UPDATE pages SET clean_text=? WHERE url LIKE ?"
    Database().conn.cursor().execute(sql, (clean_text, url))


def db_delete_page(url):
    """
    This method deletes a page from the pages table of the database.
    :param url: A string containing the URl of the web page to delete.
    :return: None
    """
    sql = "DELETE FROM pages WHERE url LIKE ?"
    Database().conn.cursor().execute(sql, (url,))


def db_get_page(url):
    """
    This method returns a tuple containing info about the last visit of a web page.
    :param url: A string containing the URL of the web page.
    :return: A tuple (url, topic, summary, language, simple_html, parsed_html, clear_text, last_visit) or None.
    """
    sql = "SELECT * FROM pages WHERE url LIKE ?"
    cur = Database().conn.cursor().execute(sql, (url,))
    result = cur.fetchone()
    return result
