from datetime import datetime

from sqlalchemy import text

from databases.models import History, db_session, engine
from helpers.utility import remove_scheme


def db_insert_action(action, url):
    """
    This method inserts an action performed by the user into the history table of the database.
    :param action: A string indicating the action performed by the user.
    :param url: The url of the web page related to the action performed by the user.
    """
    url = remove_scheme(url)
    session = db_session()
    history = History(user="shakk", action=action, url=url, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    session.add(history)
    session.commit()
    session.close()


def db_delete_last_action(user):
    sql = "DELETE FROM history WHERE id = (SELECT MAX(id) FROM history) and user LIKE :user"
    engine.connect().execute(sql, user=user)


def db_get_last_action(user):
    """
    This method retrieves the second to last action performed by the user.
    Then it deletes the last two actions performed by the user.
    :param user: A string that represents the user name.
    :return: A tuple (action, url) containing the second to last action performed by the user.
    """
    sql = text("SELECT action, url FROM history WHERE user LIKE :user ORDER BY id DESC")
    result = engine.connect().execute(sql, user=user).fetchone()
    return result
