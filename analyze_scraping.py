import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def select_task_by_priority(conn, priority):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), text, url_anchor FROM url GROUP BY url_anchor ORDER BY COUNT(*) DESC", ())

    rows = cur.fetchall()

    for row in rows:
        print(row)


def main():
    database = r"databases/open.online.db"

    # create a database connection
    conn = create_connection(database)
    with conn:
        select_task_by_priority(conn, 1)


if __name__ == '__main__':
    main()
