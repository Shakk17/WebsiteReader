import sqlite3
from sqlite3 import Error
from datetime import datetime

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

sql_create_crawler_links_table = """CREATE TABLE IF NOT EXISTS crawler_links (
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

sql_create_page_links_table = """CREATE TABLE IF NOT EXISTS text_links (
                                    page_url text NOT NULL,
                                    link_num integer NOT NULL,
                                    position integer NOT NULL,
                                    link_text text NOT NULL,
                                    link_url text NOT NULL,
                                    PRIMARY KEY (page_url, link_num),
                                    FOREIGN KEY (page_url) REFERENCES pages (url)
                                );"""


class Database:
    """
    This class handles all the operations related to the database.
    """
    name = "databases/database.db"
    conn = None

    def __init__(self):
        # Create a database connection.
        try:
            self.conn = sqlite3.connect(self.name, isolation_level=None)
        except Error as e:
            print(e)

    def start(self):
        if self.conn is not None:
            # Create tables.
            self.conn.cursor().execute(sql_create_history_table)
            self.conn.cursor().execute(sql_create_websites_table)
            self.conn.cursor().execute(sql_create_crawler_links_table)
            self.conn.cursor().execute(sql_create_pages_table)
            self.conn.cursor().execute(sql_create_page_links_table)
        else:
            print("Error! Cannot create the database connection.")

    def analyze_scraping(self, domain):
        """
        This method analyses the crawl of a domain and returns its menu links, ordered by number DESC.
        :param domain: A string containing the domain to analyse.
        :return: An array of tuples (number, link_text, link_url, avg_x, avg_y) ordered by number DESC.
        """
        cur = self.conn.cursor()
        sql = """
        SELECT max(times) AS max_times, crawler_links.page_url, link_text, crawler_links.link_url, x_position, y_position
        FROM (
            SELECT COUNT(*) AS times, link_url
            FROM crawler_links
            WHERE page_url LIKE ?
            GROUP BY link_url
            ORDER BY times DESC
        ) counting
        INNER JOIN crawler_links
        ON counting.link_url = crawler_links.link_url
        WHERE crawler_links.page_url LIKE ? and y_position < 2000
        GROUP BY crawler_links.link_url
        ORDER BY max_times DESC"""
        cur.execute(sql, (f"%{domain}%", f"%{domain}"))

        rows = cur.fetchall()
        return rows
