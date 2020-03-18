from databases.database_handler import Database


def db_insert_text_link(page_url, link_num, link):
    """
    This method inserts a link contained in the main text of a web page into the page_links table of the database.
    :param page_url: A string containing the URL of the web page containing the link.
    :param link_num: A number representing the index of the link to insert between all the other links of the text.
    :param link: A tuple (position, link_text, link_url) containing info about the link.
    :return: None.
    """
    sql = "INSERT INTO text_links (page_url, link_num, position, link_text, link_url) VALUES (?, ?, ?, ?, ?)"
    Database().conn.cursor().execute(sql, (page_url, link_num, link[0], link[1], link[2]))


def db_get_text_link(page_url, link_num):
    """
    This method returns a link contained in the main text of a web page.
    :param page_url: A string containing the URL of the web page containing the link.
    :param link_num: A number representing the index of the link to get between all the other links of the text.
    :return: A tuple (link_url) containing the URL of the link requested or None.
    """
    sql = "SELECT link_url FROM text_links WHERE page_url LIKE ? AND link_num = ?"
    cur = Database().conn.cursor()
    cur.execute(sql, (page_url, link_num))
    result = cur.fetchone()
    return result


def db_get_text_links(page_url):
    """
    This method returns all the links contained in the main text of a web page.
    :param page_url: A string containing the URL of the web page.
    :return: An array containing tuples (position, link_text) with all the info about the links of the web page.
    """
    sql = "SELECT position, link_text FROM text_links WHERE page_url LIKE ?"
    cur = Database().conn.cursor()
    cur.execute(sql, (page_url,))
    result = cur.fetchall()
    return result


def db_delete_text_links(url):
    """
    This method deletes all the page links from the page_links table of the database.
    :param url: A string containing the URl of the web page to delete.
    :return: None
    """
    sql = "DELETE FROM text_links WHERE page_url LIKE ?"
    Database().conn.cursor().execute(sql, (url,))
