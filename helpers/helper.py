from datetime import datetime, timedelta

from databases.crawler_links_handler import db_get_crawler_links
from databases.pages_handler import db_get_page
from databases.text_links_handler import db_get_text_links
from helpers.utility import extract_words


def is_action_recent(timestamp, days=0, minutes=0):
    """
    This method compares a timestamp to the actual date.
    :param timestamp: A string in the format "%Y-%m-%d %H:%M:%S".
    :param days: An integer indicating the number of days defining when an action is recent.
    :param minutes: An integer indicating the number of minutes defining when an action is recent.
    :return: True is the timestamp inserted is a date that happened recently, False otherwise.
    """
    t1 = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    t2 = datetime.now()

    difference = t2 - t1

    recent = difference < timedelta(days=days, minutes=minutes)
    return recent


def update_cursor_index(action, old_idx, step, size):
    """
    This method takes an index as an input, and returns an updated index which value depends on the other parameters.
    :param action: "reset", "next" or "previous".
    :param old_idx: An integer representing the old index to modify.
    :param step: An integer representing the variation of the index.
    :param size: An integer representing the size of the element related to the index.
    :return: An integer representing the new index.
    """
    new_idx = old_idx
    if action == "reset":
        new_idx = 0
    elif action == "next":
        new_idx = new_idx + step if (old_idx + step) < size else 0
    elif action == "previous":
        new_idx = new_idx - step if (old_idx - step) > 0 else 0
    return new_idx
