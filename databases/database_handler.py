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
                                    FOREIGN KEY (page_url) REFERENCES websites (domain)
                                );"""

sql_create_pages_table = """CREATE TABLE IF NOT EXISTS pages (
                                    url text PRIMARY KEY,
                                    clean_text text,
                                    last_visit text NOT NULL
                                );"""

sql_create_page_links_table = """CREATE TABLE IF NOT EXISTS page_links (
                                    page_url text NOT NULL,
                                    link_num integer NOT NULL,
                                    position integer NOT NULL,
                                    link_text text NOT NULL,
                                    link_url text NOT NULL,
                                    PRIMARY KEY (page_url, link_num),
                                    FOREIGN KEY (page_url) REFERENCES pages (url)
                                );"""


class Database:
    name = "databases/database.db"
    conn = None

    def __init__(self):
        # Create a database connection.
        self.create_connection()

        if self.conn is not None:
            # Create tables.
            self.create_table(sql_create_history_table)
            self.create_table(sql_create_websites_table)
            self.create_table(sql_create_crawler_links_table)
            self.create_table(sql_create_pages_table)
            self.create_table(sql_create_page_links_table)
        else:
            print("Error! cannot create the database connection.")

    def create_connection(self):
        try:
            self.conn = sqlite3.connect(self.name, isolation_level=None)
        except Error as e:
            print(e)

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def insert_action(self, action, url):
        sql = '''INSERT INTO history (user, action, url, timestamp)
                    VALUES (?, ?, ?, current_timestamp) '''
        cur = self.conn.cursor()
        record = ("shakk", action, url)
        cur.execute(sql, record)
        # Returns id of the tuple inserted.
        return cur.lastrowid

    def insert_website(self, domain):
        sql = "INSERT INTO websites (domain, last_crawled_on) VALUES (?, current_timestamp)"
        cur = self.conn.cursor()
        record = domain
        cur.execute(sql, (record,))
        # Returns id of the tuple inserted.
        return cur.lastrowid

    def insert_page(self, url, clean_text):
        sql = "INSERT INTO pages (url, clean_text, last_visit) VALUES (?, ?, current_timestamp)"
        cur = self.conn.cursor()
        cur.execute(sql, (url, clean_text))
        # Returns id of the tuple inserted.
        return cur.lastrowid

    def insert_page_link(self, page_url, link_num, link):
        sql = "INSERT INTO page_links (page_url, link_num, position, link_text, link_url) VALUES (?, ?, ?, ?, ?)"
        cur = self.conn.cursor()
        cur.execute(sql, (page_url, link_num, link[0], link[1], link[2]))
        # Returns id of the tuple inserted.
        return cur.lastrowid

    def get_page_link(self, page_url, link_num):
        sql = "SELECT link_url FROM page_links WHERE page_url LIKE ? AND link_num = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (page_url, link_num))
        result = cur.fetchone()
        return result

    def get_page_links(self, page_url):
        sql = "SELECT position, link_text FROM page_links WHERE page_url LIKE ?"
        cur = self.conn.cursor()
        cur.execute(sql, (page_url, ))
        result = cur.fetchall()
        return result

    def remove_old_website(self, domain):
        # First remove all the tuples in 'links' related to the domain.
        sql = "DELETE FROM crawler_links WHERE page_url LIKE ?;"
        cur = self.conn.cursor()
        url = f"%{domain}%"
        cur.execute(sql, (url,))
        # Then remove the tuple in 'websites' containing the domain.
        sql = "DELETE FROM websites WHERE domain LIKE ?;"
        cur = self.conn.cursor()
        cur.execute(sql, (domain,))
        # Returns id of the tuple inserted.
        return cur.lastrowid

    def last_time_crawled(self, domain):
        sql = "SELECT * FROM websites WHERE domain LIKE ? LIMIT 1"
        cur = self.conn.cursor()
        cur.execute(sql, (domain,))
        rows = cur.fetchall()
        # Returns True is it has been crawled, False otherwise.
        if len(rows) == 0:
            return None
        return rows[0][1]

    def last_time_visited(self, url):
        sql = "SELECT clean_text, last_visit FROM pages WHERE url LIKE ?"
        cur = self.conn.cursor()
        cur.execute(sql, (url,))
        rows = cur.fetchall()
        if len(rows) > 0:
            return rows[0]
        else:
            return None

    def analyze_scraping(self, domain):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*), link_text, link_url, "
                    "       round(AVG(NULLIF(x_position, 0))) AS avg_x, round(AVG(NULLIF(y_position, 0))) AS avg_y "
                    "FROM crawler_links "
                    "WHERE page_url LIKE ? AND y_position < 1000 "
                    "GROUP BY link_url "
                    "ORDER BY COUNT(*) DESC ", (f"%{domain}%",))

        rows = cur.fetchall()
        return rows

    def get_previous_action(self, user):
        # First, get the second to last action performed.
        cur = self.conn.cursor()
        cur.execute("SELECT action, url "
                    "FROM history "
                    "WHERE user LIKE ? "
                    "ORDER BY id DESC ",
                    (f"{user}",)
                    )

        result = cur.fetchall()[1]

        # Then, delete the last two actions performed.
        cur.execute("DELETE from history "
                    "WHERE id IN (SELECT id FROM history WHERE user LIKE ? ORDER BY id DESC LIMIT 2)",
                    (f"{user}",)
                    )

        return result
