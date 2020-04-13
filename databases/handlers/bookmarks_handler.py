from sqlite3 import IntegrityError

from databases.database_handler import Database
from helpers.exceptions import BookmarkUrlTaken, BookmarkNameTaken
from helpers.utility import remove_scheme


def db_insert_bookmark(url, name, user):
    url = remove_scheme(url)
    sql = """INSERT INTO bookmarks (url, name, user) 
                VALUES (?, ?, ?)"""
    try:
        Database().conn.cursor().execute(sql, (url, name, user))
    except IntegrityError as e:
        if "url" in e.args[0]:
            raise BookmarkUrlTaken
        elif "name" in e.args[0]:
            raise BookmarkNameTaken


def db_get_bookmarks(user):
    sql = """SELECT url, name, user 
                FROM bookmarks WHERE user LIKE ?"""
    cur = Database().conn.cursor().execute(sql, (user,))
    rows = cur.fetchall()
    return rows
