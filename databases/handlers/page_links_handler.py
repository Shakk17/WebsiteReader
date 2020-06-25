from databases.models import PageLink, db_session, engine
from helpers.utility import remove_scheme


def db_delete_all_domain_links(domain):
    """
    This method removes the results of a previous crawl of a domain from the database.
    :param domain: A string containing the domain to be un-crawled.
    :return: None
    """
    url = f"%{domain}%"
    sql = "DELETE FROM page_links WHERE page_url LIKE :url;"
    engine.connect().execute(sql, url=url)


def db_delete_all_page_links(url):
    url = remove_scheme(url)
    sql = "DELETE FROM page_links WHERE page_url LIKE :url;"
    engine.connect().execute(sql, url=url)


def db_insert_page_link(page_url, link_url, link_text, x_position, y_position, in_list, in_nav):
    page_url = remove_scheme(page_url)
    link_url = remove_scheme(link_url)

    page_link = PageLink(page_url=page_url, link_url=link_url, link_text=link_text,
                         x_position=x_position, y_position=y_position, in_list=in_list, in_nav=in_nav)
    session = db_session()
    session.add(page_link)
    session.commit()
    session.close()


def db_get_page_links(url):
    page_url = remove_scheme(url)
    sql = "SELECT link_text, link_url, y_position, in_list, in_nav FROM page_links WHERE page_url LIKE :page_url"
    rows = engine.connect().execute(sql, page_url=page_url).fetchall()
    return rows


def db_get_domain_links(domain):
    page_url = f"%{domain}%"
    sql = "SELECT link_text, link_url, y_position, in_list, in_nav FROM page_links WHERE page_url LIKE :page_url"
    rows = engine.connect().execute(sql, page_url=page_url).fetchall()
    return rows


def get_links_in_list(domain):
    """
    This method analyses the crawl of a domain and returns its menu links, ordered by number DESC.
    :param domain: A string containing the domain to analyse.
    :return: An array of tuples (number, link_text, link_url, avg_x, avg_y) ordered by number DESC.
    """
    page_url = f"%{domain}%"
    sql = """
        SELECT COUNT(*) AS times, link_text, link_url, page_url, in_nav
        FROM page_links
        WHERE page_url LIKE :page_url AND in_list = 1
        GROUP BY link_url
        ORDER BY times DESC
    """
    rows = engine.connect().execute(sql, page_url=page_url).fetchall()
    return rows
