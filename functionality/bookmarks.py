from databases.handlers.bookmarks_handler import db_insert_bookmark, db_delete_bookmark, db_get_bookmarks
from helpers.exceptions import BookmarkUrlTaken, BookmarkNameTaken


def insert_bookmark(url, name):
    try:
        db_insert_bookmark(url=url, name=name, user="shakk")
        text_response = "Bookmark inserted!"
    except BookmarkUrlTaken:
        text_response = "You already bookmarked this page!"
    except BookmarkNameTaken:
        text_response = "You already used this name for another bookmark!"
    return text_response


def delete_bookmark(url, user):
    db_delete_bookmark(url, user)
    text_response = "Bookmark deleted!"
    return text_response


def get_bookmarks(user):
    bookmarks = db_get_bookmarks(user)
    return bookmarks
