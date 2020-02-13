import sqlite3
from datetime import datetime
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

sql_create_links_table = """CREATE TABLE IF NOT EXISTS links (
                                    id integer PRIMARY KEY,
                                    page_url text NOT NULL,
                                    link_url integer,
                                    link_text integer NOT NULL,
                                    x_position integer NOT NULL,
                                    y_position text NOT NULL,
                                    FOREIGN KEY (page_url) REFERENCES websites (domain)
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
            self.create_table(sql_create_links_table)
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
        cur.execute(sql, (record, ))
        # Returns id of the tuple inserted.
        return cur.lastrowid

    def remove_old_website(self, domain):
        # First remove all the tuples in 'links' related to the domain.
        sql = "DELETE FROM links WHERE page_url LIKE ?;"
        cur = self.conn.cursor()
        url = f"%{domain}%"
        cur.execute(sql, (url,))
        # Then remove the tuple in 'websites' containing the domain.
        sql = "DELETE FROM websites WHERE domain LIKE ?;"
        cur = self.conn.cursor()
        cur.execute(sql, (domain,))
        # Returns id of the tuple inserted.
        return cur.lastrowid

    def has_been_crawled(self, domain):
        sql = "SELECT * FROM websites WHERE domain LIKE ? LIMIT 1"
        cur = self.conn.cursor()
        cur.execute(sql, (domain, ))
        rows = cur.fetchall()
        # Returns True is it has been crawled, False otherwise.
        crawled = len(rows) > 0
        if crawled:
            # Check when was the last crawling of the domain.
            query_timestamp = rows[0][1]
            t1 = datetime.strptime(query_timestamp, "%Y-%m-%d %H:%M:%S")
            t2 = datetime.now()
            difference = t2 - t1
            print(f"The domain {domain} was last crawled {difference.days} days ago.")
            if difference.days > 7:
                # It's time to crawl it again!
                self.remove_old_website(domain)
                return False
        return crawled

    def analyze_scraping(self, url):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*), link_text, link_url, "
                    "       round(AVG(NULLIF(x_position, 0))) AS avg_x, round(AVG(NULLIF(y_position, 0))) AS avg_y "
                    "FROM links "
                    "WHERE page_url LIKE ? "
                    "GROUP BY link_url "
                    "HAVING avg_y < 500 "
                    "ORDER BY COUNT(*) DESC "
                    "LIMIT 10", (f"%{url}%", ))

        rows = cur.fetchall()

        result = []

        for row in rows:
            result.append(tuple(row[1:3]))
            print(row)

        return result

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
                    (f"{user}", )
        )

        return result
