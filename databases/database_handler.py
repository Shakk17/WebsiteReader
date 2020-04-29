import sqlite3
from sqlite3 import Error

sql_create_history_table = """ CREATE TABLE IF NOT EXISTS history (
                                                id integer PRIMARY KEY AUTOINCREMENT,
                                                user text NOT NULL,
                                                action text,
                                                url text,
                                                timestamp text
                                            ); """

sql_create_websites_table = """CREATE TABLE IF NOT EXISTS websites (
                                    domain text PRIMARY KEY,
                                    last_crawled_on text NOT NULL
                                );"""

sql_create_page_links_table = """CREATE TABLE IF NOT EXISTS page_links (
                                    id integer PRIMARY KEY,
                                    page_url text NOT NULL,
                                    link_url text NOT NULL,
                                    link_text text NOT NULL,
                                    x_position integer,
                                    y_position integer,
                                    in_list integer NOT NULL,
                                    FOREIGN KEY (page_url) REFERENCES websites (domain)
                                );"""

sql_create_pages_table = """CREATE TABLE IF NOT EXISTS pages (
                                    url text PRIMARY KEY,
                                    topic text,
                                    language text,
                                    simple_html text,
                                    parsed_html text,
                                    clean_text text,
                                    last_visit text NOT NULL
                                );"""

sql_create_text_links_table = """CREATE TABLE IF NOT EXISTS text_links (
                                    page_url text NOT NULL,
                                    link_num integer NOT NULL,
                                    position integer NOT NULL,
                                    link_text text NOT NULL,
                                    link_url text NOT NULL,
                                    PRIMARY KEY (page_url, link_num),
                                    FOREIGN KEY (page_url) REFERENCES pages (url)
                                );"""

sql_create_forms_table = """CREATE TABLE IF NOT EXISTS forms (
                                    page_url text NOT NULL,
                                    form_num integer NOT NULL,
                                    method text NOT NULL,
                                    action text NOT NULL,
                                    input_num integer NOT NULL,
                                    input_name text NOT NULL,
                                    input_text text NOT NULL,
                                    PRIMARY KEY (page_url, form_num),
                                    FOREIGN KEY (page_url) REFERENCES pages (url)
                                );"""

sql_create_bookmarks_table = """CREATE TABLE IF NOT EXISTS bookmarks (
                                    url text NOT NULL,
                                    name text NOT NULL,
                                    user text NOT NULL,
                                    PRIMARY KEY (url, user),
                                    CONSTRAINT name_user UNIQUE(name, user)
                                );"""

sql_create_functionality_table = """CREATE TABLE IF NOT EXISTS functionality (
                                    page_url text NOT NULL,
                                    type text NOT NULL,
                                    name text NOT NULL,
                                    link_url text,
                                    score integer NOT NULL,
                                    PRIMARY KEY (page_url, type, name)
                                );"""


def analyze_scraping(domain):
    """
    This method analyses the crawl of a domain and returns its menu links, ordered by number DESC.
    :param domain: A string containing the domain to analyse.
    :return: An array of tuples (number, link_text, link_url, avg_x, avg_y) ordered by number DESC.
    """
    cur = Database().conn.cursor()
    sql = """
    SELECT max(times) AS max_times, link_text, page_links.link_url, 
            x_position, y_position, in_list
    FROM (
        SELECT COUNT(*) AS times, link_url
        FROM page_links
        WHERE page_url LIKE ?
        GROUP BY link_url
        ORDER BY times DESC
    ) counting
    INNER JOIN page_links
    ON counting.link_url = page_links.link_url
    WHERE page_links.page_url LIKE ? and page_links.in_list = 1
    GROUP BY page_links.link_url
    ORDER BY max_times DESC"""
    cur.execute(sql, (f"%{domain}%", f"%{domain}"))

    rows = cur.fetchall()
    cur.close()
    return rows


class Database:
    """
    This class handles all the operations related to the database.
    """
    name = "databases/database.db"
    conn = None

    def __init__(self):
        # Create a database connection.
        try:
            self.conn = sqlite3.connect(self.name, timeout=15, isolation_level=None)
        except Error as e:
            print(e)

    def start(self):
        if self.conn is not None:
            # Create tables.
            self.conn.cursor().execute(sql_create_history_table)
            self.conn.cursor().execute(sql_create_websites_table)
            self.conn.cursor().execute(sql_create_page_links_table)
            self.conn.cursor().execute(sql_create_pages_table)
            self.conn.cursor().execute(sql_create_text_links_table)
            self.conn.cursor().execute(sql_create_forms_table)
            self.conn.cursor().execute(sql_create_bookmarks_table)
            self.conn.cursor().execute(sql_create_functionality_table)
        else:
            print("Error! Cannot create the database connection.")
