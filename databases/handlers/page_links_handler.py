from databases.database_handler import Database
from helpers.utility import remove_scheme


def db_delete_all_domain_links(domain):
    """
    This method removes the results of a previous crawl of a domain from the database.
    :param domain: A string containing the domain to be un-crawled.
    :return: None
    """
    sql = "DELETE FROM crawler_links WHERE page_url LIKE ?;"
    cur = Database().conn.cursor()
    url = f"%{domain}%"
    cur.execute(sql, (url,))


def db_delete_all_page_links(url):
    url = remove_scheme(url)

    sql = "DELETE FROM crawler_links WHERE page_url LIKE ?;"
    Database().conn.cursor().execute(sql, (url,))


def db_insert_page_link(page_url, link_url, link_text, x_position, y_position, in_list):
    page_url = remove_scheme(page_url)
    link_url = remove_scheme(link_url)

    sql = """INSERT INTO crawler_links (page_url, link_url, link_text, x_position, y_position, in_list) 
                VALUES (?, ?, ?, ?, ?, ?)"""
    Database().conn.cursor().execute(sql, (page_url, link_url, link_text, x_position, y_position, in_list))


def db_get_page_links(url):
    url = remove_scheme(url)
    sql = "SELECT link_text, link_url, y_position, in_list FROM crawler_links WHERE page_url LIKE ?"
    cur = Database().conn.cursor().execute(sql, (url,))
    rows = cur.fetchall()
    return rows


def db_get_domain_links(domain):
    url = f"%{domain}%"
    sql = "SELECT link_text, link_url, y_position, in_list FROM crawler_links WHERE page_url LIKE ?"
    cur = Database().conn.cursor().execute(sql, (url,))
    rows = cur.fetchall()
    return rows
