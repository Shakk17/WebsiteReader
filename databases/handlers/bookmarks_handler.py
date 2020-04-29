from sqlite3 import IntegrityError

from databases.database_handler import Database
from helpers.exceptions import BookmarkUrlTaken, BookmarkNameTaken
from helpers.utility import remove_scheme


def db_insert_bookmark(url, name, user):
    url = remove_scheme(url)
    sql = """INSERT INTO bookmarks (url, name, user) 
                VALUES (?, ?, ?)"""
    cur = Database().conn.cursor()
    try:
        cur.execute(sql, (url, name, user))
    except IntegrityError as e:
        if "url" in e.args[0]:
            raise BookmarkUrlTaken
        elif "name" in e.args[0]:
            raise BookmarkNameTaken
    cur.close()


def db_delete_bookmark(url, user):
    url = remove_scheme(url)
    sql = "DELETE FROM bookmarks WHERE url LIKE ? AND user LIKE ?;"
    cur = Database().conn.cursor()
    cur.execute(sql, (url, user))
    cur.close()


def db_get_bookmarks(user):
    sql = """SELECT url, name, user 
                FROM bookmarks WHERE user LIKE ?"""
    cur = Database().conn.cursor()
    cur.execute(sql, (user,))
    rows = cur.fetchall()
    cur.close()
    return rows
