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

sql_create_crawler_links_table = """CREATE TABLE IF NOT EXISTS crawler_links (
                                    id integer PRIMARY KEY,
                                    page_url text NOT NULL,
                                    link_url text NOT NULL,
                                    link_text text NOT NULL,
                                    x_position integer NOT NULL,
                                    y_position integer NOT NULL,
                                    in_list integer NOT NULL,
                                    FOREIGN KEY (page_url) REFERENCES websites (domain)
                                );"""

sql_create_pages_table = """CREATE TABLE IF NOT EXISTS pages (
                                    url text PRIMARY KEY,
                                    topic text,
                                    language text,
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

        if self.conn is not None:
            # Create tables.
            self.create_table(sql_create_history_table)
            self.create_table(sql_create_websites_table)
            self.create_table(sql_create_crawler_links_table)
            self.create_table(sql_create_pages_table)
            self.create_table(sql_create_page_links_table)
        else:
            print("Error! cannot create the database connection.")

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    # HISTORY TABLE

    def insert_action(self, action, url):
        """
        This method inserts an action performed by the user into the history table of the database.
        :param action: A string indicating the action performed by the user.
        :param url: The url of the web page related to the action performed by the user.
        """
        sql = '''INSERT INTO history (user, action, url, timestamp)
                    VALUES (?, ?, ?, current_timestamp) '''
        cur = self.conn.cursor()
        record = ("shakk", action, url)
        cur.execute(sql, record)

    def get_previous_action(self, user):
        """
        This method retrieves the second to last action performed by the user.
        Then it deletes the last two actions performed by the user.
        :param user: A string that represents the user name.
        :return: A tuple (action, url) containing the second to last action performed by the user.
        """
        # First, get the second to last action performed.
        cur = self.conn.cursor()
        cur.execute("SELECT action, url FROM history WHERE user LIKE ? ORDER BY id DESC ", (f"{user}",))
        result = cur.fetchall()[1]

        # Then, delete the last two actions performed.
        cur.execute("DELETE from history "
                    "WHERE id IN (SELECT id FROM history WHERE user LIKE ? ORDER BY id DESC LIMIT 2)",
                    (f"{user}",)
                    )
        return result

    # WEBSITES TABLE

    def insert_website(self, domain):
        """
        This method inserts a website into the websites table of the database.
        :param domain: The domain of the website to insert in the database.
        """
        sql = "INSERT INTO websites (domain, last_crawled_on) VALUES (?, current_timestamp)"
        cur = self.conn.cursor()
        record = domain
        cur.execute(sql, (record,))

    def last_time_crawled(self, domain):
        """
        This method returns the timestamp of the last crawl on a website, if it has already been crawled.
        :param domain: A string representing the domain of the website to search.
        :return: The timestamp of the last crawl (if it has been crawled), None otherwise.
        """
        sql = "SELECT * FROM websites WHERE domain LIKE ? LIMIT 1"
        cur = self.conn.cursor()
        cur.execute(sql, (domain,))
        rows = cur.fetchone()
        # Returns True is it has been crawled, False otherwise.
        if rows is not None:
            return rows[1]

    # PAGES TABLE

    def insert_page(self, url, topic, language):
        """
        This method inserts a web page in the pages table of the database.
        :param url: A string representing the URL of the web page.
        :param topic: A string representing the topic of the web page.
        :param language: A string representing the language of the web page.
        """
        sql = """INSERT INTO pages (url, topic, language, last_visit) 
                    VALUES (?, ?, ?, current_timestamp)"""
        cur = self.conn.cursor()
        cur.execute(sql, (url, topic, language))

    def update_page(self, url, clean_text):
        """
        This method updates a page in the pages table of the database.
        :param url: A string representing the URL of the web page to update.
        :param clean_text: A string representing the clear main text of the web page to insert.
        """
        sql = "UPDATE pages SET clean_text=? WHERE url LIKE ?"
        cur = self.conn.cursor()
        cur.execute(sql, (clean_text, url))

    def delete_page(self, url):
        """
        This method deletes a page from the pages table of the database.
        :param url: A string containing the URl of the web page to delete.
        :return: None
        """
        sql = "DELETE FROM pages WHERE url LIKE ?"
        cur = self.conn.cursor()
        cur.execute(sql, (url, ))

    def last_time_visited(self, url):
        """
        This method returns a tuple containing info about the last visit of a web page.
        :param url: A string containing the URL of the web page.
        :return: A tuple (url, topic, summary, language, clear_text, last_visit) or None.
        """
        sql = "SELECT * FROM pages WHERE url LIKE ?"
        cur = self.conn.cursor()
        cur.execute(sql, (url,))
        result = cur.fetchone()
        return result

    # TEXT LINKS TABLE

    def insert_text_link(self, page_url, link_num, link):
        """
        This method inserts a link contained in the main text of a web page into the page_links table of the database.
        :param page_url: A string containing the URL of the web page containing the link.
        :param link_num: A number representing the index of the link to insert between all the other links of the text.
        :param link: A tuple (position, link_text, link_url) containing info about the link.
        :return: None.
        """
        sql = "INSERT INTO text_links (page_url, link_num, position, link_text, link_url) VALUES (?, ?, ?, ?, ?)"
        cur = self.conn.cursor()
        cur.execute(sql, (page_url, link_num, link[0], link[1], link[2]))

    def get_text_link(self, page_url, link_num):
        """
        This method returns a link contained in the main text of a web page.
        :param page_url: A string containing the URL of the web page containing the link.
        :param link_num: A number representing the index of the link to get between all the other links of the text.
        :return: A tuple (link_url) containing the URL of the link requested or None.
        """
        sql = "SELECT link_url FROM text_links WHERE page_url LIKE ? AND link_num = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (page_url, link_num))
        result = cur.fetchone()
        return result

    def get_text_links(self, page_url):
        """
        This method returns all the links contained in the main text of a web page.
        :param page_url: A string containing the URL of the web page.
        :return: An array containing tuples (position, link_text) with all the info about the links of the web page.
        """
        sql = "SELECT position, link_text FROM text_links WHERE page_url LIKE ?"
        cur = self.conn.cursor()
        cur.execute(sql, (page_url,))
        result = cur.fetchall()
        return result

    def delete_text_links(self, url):
        """
        This method deletes all the page links from the page_links table of the database.
        :param url: A string containing the URl of the web page to delete.
        :return: None
        """
        sql = "DELETE FROM text_links WHERE page_url LIKE ?"
        cur = self.conn.cursor()
        cur.execute(sql, (url,))

    # CRAWLER LINKS TABLE

    def remove_old_website(self, domain):
        """
        This method removes the results of a previous crawl of a domain from the database.
        :param domain: A string containing the domain to be un-crawled.
        :return: None
        """
        # First remove all the tuples in 'links' related to the domain.
        sql = "DELETE FROM crawler_links WHERE page_url LIKE ?;"
        cur = self.conn.cursor()
        url = f"%{domain}%"
        cur.execute(sql, (url,))
        # Then remove the tuple in 'websites' containing the domain.
        sql = "DELETE FROM websites WHERE domain LIKE ?;"
        cur = self.conn.cursor()
        cur.execute(sql, (f"%{domain}",))

    def insert_crawler_link(self, page_url, href, text, x_position, y_position, in_list):
        sql = """INSERT INTO crawler_links (page_url, link_url, link_text, x_position, y_position, in_list)
              VALUES (?, ?, ?, ?, ?, ?)"""
        cur = self.conn.cursor()
        cur.execute(sql, (page_url, href, text, x_position, y_position, in_list))

    def get_crawler_links(self, url):
        sql = "SELECT link_text, link_url, y_position, in_list FROM crawler_links WHERE page_url LIKE ?"
        cur = self.conn.cursor()
        cur.execute(sql, (url, ))
        rows = cur.fetchall()
        return rows

    def analyze_scraping(self, domain):
        """
        This method analyses the crawl of a domain and returns its menu links, ordered by number DESC.
        :param domain: A string containing the domain to analyse.
        :return: An array of tuples (number, link_text, link_url, avg_x, avg_y) ordered by number DESC.
        """
        cur = self.conn.cursor()
        sql = """
        SELECT max(times) AS max_times, link_text, link_url, avg_x, avg_y
        FROM (
            SELECT COUNT(*) AS times, link_text, link_url, 
                round(AVG(NULLIF(x_position, 0))) AS avg_x, round(AVG(NULLIF(y_position, 0))) AS avg_y 
            FROM crawler_links
            WHERE page_url LIKE ? AND y_position < 2000
            GROUP BY link_text, link_url
            ORDER BY times DESC
        )
        GROUP BY link_url
        ORDER BY max_times DESC"""
        cur.execute(sql, (f"%{domain}%",))

        rows = cur.fetchall()
        return rows
