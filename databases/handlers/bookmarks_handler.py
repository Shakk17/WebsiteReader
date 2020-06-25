from databases.models import Bookmark, db_session, engine
from helpers.exceptions import BookmarkUrlTaken, BookmarkNameTaken
from helpers.utility import remove_scheme


def db_insert_bookmark(url, name, user):
    url = remove_scheme(url)
    bookmark = Bookmark(url=url, name=name, user=user)
    session = db_session()
    try:
        session.add(bookmark)
        session.commit()
    except Exception as e:
        if "url" in e.args[0]:
            raise BookmarkUrlTaken
        elif "name" in e.args[0]:
            raise BookmarkNameTaken
    finally:
        session.close()


def db_delete_bookmark(url, user):
    url = remove_scheme(url)
    sql = "DELETE FROM bookmarks WHERE url LIKE :url AND user LIKE :user;"
    engine.connect().execute(sql, url=url, user=user)


def db_get_bookmarks(user):
    sql = """SELECT url, name, user 
                FROM bookmarks WHERE user LIKE :user"""
    rows = engine.connect().execute(sql, user).fetchall()
    return rows
