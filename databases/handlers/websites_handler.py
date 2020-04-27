from datetime import datetime

from databases.database_handler import Database


def db_insert_website(domain):
    """
    This method inserts a website into the websites table of the database.
    :param domain: The domain of the website to insert in the database.
    """
    sql = "INSERT INTO websites (domain, last_crawled_on) VALUES (?, ?)"
    Database().conn.navigation().execute(sql, (domain, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def db_delete_website(domain):
    sql = "DELETE FROM websites WHERE domain LIKE ?;"
    Database().conn.navigation().execute(sql, (f"%{domain}",))


def db_last_time_crawled(domain):
    """
    This method returns the timestamp of the last crawl on a website, if it has already been crawled.
    :param domain: A string representing the domain of the website to search.
    :return: The timestamp of the last crawl (if it has been crawled), None otherwise.
    """
    sql = "SELECT * FROM websites WHERE domain LIKE ? LIMIT 1"
    cur = Database().conn.navigation().execute(sql, (domain,))
    rows = cur.fetchone()
    # Returns True is it has been crawled, False otherwise.
    if rows is not None:
        return rows[1]
