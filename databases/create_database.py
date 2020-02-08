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
                                    url text PRIMARY KEY,
                                    last_crawled_on text NOT NULL
                                );"""

sql_create_links_table = """CREATE TABLE IF NOT EXISTS links (
                                    id integer PRIMARY KEY,
                                    page_url text NOT NULL,
                                    link_url integer,
                                    link_text integer NOT NULL,
                                    x_position integer NOT NULL,
                                    y_position text NOT NULL,
                                    FOREIGN KEY (page_url) REFERENCES websites (url)
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

    def save_action_in_db(self, action, url):
        sql = ''' INSERT INTO history
                    (user, action, url, timestamp)
                    VALUES
                    (?, ?, ?, current_timestamp) '''
        cur = self.conn.cursor()
        record = ("shakk", action, url)
        cur.execute(sql, record)
        # Returns id of the tuple inserted.
        print(cur.lastrowid)
        return cur.lastrowid
