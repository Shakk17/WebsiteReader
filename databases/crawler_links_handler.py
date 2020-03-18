from databases.database_handler import Database


def db_delete_all_domain_crawler_links(domain):
    """
    This method removes the results of a previous crawl of a domain from the database.
    :param domain: A string containing the domain to be un-crawled.
    :return: None
    """
    sql = "DELETE FROM crawler_links WHERE page_url LIKE ?;"
    cur = Database().conn.cursor()
    url = f"%{domain}%"
    cur.execute(sql, (url,))


def db_delete_all_url_crawler_links(url):
    sql = "DELETE FROM crawler_links WHERE page_url LIKE ?;"
    Database().conn.cursor().execute(sql, (url,))


def db_insert_crawler_link(page_url, link_url, link_text, x_position, y_position, in_list):
    sql = """INSERT INTO crawler_links (page_url, link_url, link_text, x_position, y_position, in_list) 
                VALUES (?, ?, ?, ?, ?, ?)"""
    Database().conn.cursor().execute(sql, (page_url, link_url, link_text, x_position, y_position, in_list))


def db_get_crawler_links(url):
    sql = "SELECT link_text, link_url, y_position, in_list FROM crawler_links WHERE page_url LIKE ?"
    cur = Database().conn.cursor().execute(sql, (url,))
    rows = cur.fetchall()
    return rows
