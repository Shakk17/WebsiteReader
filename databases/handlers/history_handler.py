from datetime import datetime

from databases.database_handler import Database
from helpers.utility import remove_scheme


def db_insert_action(action, url):
    """
    This method inserts an action performed by the user into the history table of the database.
    :param action: A string indicating the action performed by the user.
    :param url: The url of the web page related to the action performed by the user.
    """
    url = remove_scheme(url)
    sql = '''INSERT INTO history (user, action, url, timestamp)
                VALUES (?, ?, ?, ?) '''
    cur = Database().conn.cursor()
    record = ("shakk", action, url, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cur.execute(sql, record)


def db_delete_last_action(user):
    sql = "DELETE FROM history WHERE id = (SELECT MAX(id) FROM history) and user LIKE ?"
    Database().conn.cursor().execute(sql, (user, ))


def db_get_last_action(user):
    """
    This method retrieves the second to last action performed by the user.
    Then it deletes the last two actions performed by the user.
    :param user: A string that represents the user name.
    :return: A tuple (action, url) containing the second to last action performed by the user.
    """
    # First, get the second to last action performed.
    sql = "SELECT action, url FROM history WHERE user LIKE ? ORDER BY id DESC"
    cur = Database().conn.cursor().execute(sql, (user, ))
    result = cur.fetchone()
    return result
