from helpers.printer import green
from colorama import Style


class Cursor:
    """
    An object that keeps track of the current state of the user.
    It is sent and received by the server (as a JSON) in requests and responses to the agent.
    """

    def __init__(self, cursor_context):
        self.url = "https://www.google.com"
        # Number that indicates the paragraph to read in the current article.
        self.idx_sentence = 0
        # Number that indicates the article to read in the current section.
        self.idx_menu = 0
        # Number of GoogleSearch result to show.
        self.idx_search_result = 0
        # Index of next link to read in the page.
        self.idx_link = 0
        # Index of next link (article mode) to read in the page.
        self.idx_link_article = 0
        # Index of next link (best mode) to read in the page.
        self.idx_link_best = 0
        # Index of the form to write into.
        self.idx_form = 0
        self.idx_field = 0
        # Bookmarks.
        self.idx_bookmarks = 0

        # Updates cursor with values received from the context.
        if cursor_context is not None:
            if cursor_context.get("parameters") is not None:
                for key, value in cursor_context.get("parameters").items():
                    if not key.endswith("original"):
                        try:
                            value = int(value)
                        except Exception:
                            pass
                        setattr(self, key, value)

    def __repr__(self):
        return (green(
            f"{Style.BRIGHT}+++ CURSOR +++{Style.NORMAL}\n"
            f"\tURL: {self.url}\n"
            f"\tIdx sentence: {self.idx_sentence}\n"
            f"\tIdx menu: {self.idx_menu}\n"
            f"\tIdx search result: {self.idx_search_result}\n"
            f"\tIdx link: {self.idx_link}\n"
            f"\tIdx link article: {self.idx_link_article}\n"
            f"\tIdx link best: {self.idx_link_best}\n"
            f"\tIdx form: {self.idx_form}\n"
            f"\tIdx field: {self.idx_field}\n"
            f"\tIdx bookmarks: {self.idx_bookmarks}\n"
        ))

    def reset_indexes(self):
        self.idx_search_result = 0
        self.idx_sentence = 0
        self.idx_menu = 0
        self.idx_link = 0
        self.idx_link_article = 0
        self.idx_link_best = 0
        self.idx_form = 0
        self.idx_field = 0
        self.idx_bookmarks = 0

