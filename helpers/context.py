from helpers.printer import green
from colorama import Style

from abc import ABC, abstractmethod


def assign_context(name, context):
    if name == "Bookmarks":
        return BookmarksContext(context)
    elif name == "GoogleSearch":
        return GoogleSearchContext(context)
    elif name == "Form":
        return FormContext(context)
    elif name == "Functionality":
        return FunctionalityContext(context)
    elif name == "LinksAll":
        return LinksAllContext(context)
    elif name == "LinksArticle":
        return LinksArticleContext(context)
    elif name == "MainText":
        return MainTextContext(context)
    elif name == "Menu":
        return MenuContext(context)


class Context(ABC):
    """
        An object that keeps track of the current state of the user.
        It is sent and received by the server (as a JSON) in requests and responses to the agent.
    """


class NavigationContext(Context):
    def __init__(self, context):
        self.url = "https://www.google.com"
        # Updates cursor with values received from the context.
        if context is not None:
            self.url = context.get("parameters").get("url")


class BookmarksContext(Context):
    def __init__(self, context):
        self.index = 0
        # Updates cursor with values received from the context.
        if context is not None:
            self.index = context.get("parameters").get("index")
            number = context.get("parameters").get("number")
            if number is not None:
                self.number = number
            name = context.get("parameters").get("name")
            if name is not None:
                self.name = name


class GoogleSearchContext(Context):
    def __init__(self, context):
        self.index = 0
        # Updates cursor with values received from the context.
        if context is not None:
            self.index = context.get("parameters").get("index")
            query = context.get("parameters").get("query")
            if query is not None:
                self.query = query


class FormContext(Context):
    def __init__(self, context):
        self.idx_form = 0
        self.idx_field = 0
        # Updates cursor with values received from the context.
        if context is not None:
            self.idx_form = context.get("parameters").get("idx_form")
            self.idx_field = context.get("parameters").get("idx_field")

            number = context.get("parameters").get("number")
            if number is not None:
                self.number = number

            user_input = context.get("parameters").get("user_input")
            if user_input is not None:
                self.user_input = user_input

            form_parameters = context.get("parameters").get("form_parameters")
            if form_parameters is not None:
                self.form_parameters = form_parameters


class FunctionalityContext(Context):
    def __init__(self, context):
        self.index = 0
        # Updates cursor with values received from the context.
        if context is not None:
            self.index = context.get("parameters").get("index")

            number = context.get("parameters").get("number")
            if number is not None:
                self.number = number


class LinksAllContext(Context):
    def __init__(self, context):
        self.idx_link = 0
        # Updates cursor with values received from the context.
        if context is not None:
            self.index = context.get("parameters").get("index")
            number = context.get("parameters").get("number")
            if number is not None:
                self.number = number


class LinksArticleContext(Context):
    def __init__(self, context):
        self.index = 0
        # Updates cursor with values received from the context.
        if context is not None:
            self.index = context.get("parameters").get("index")
            number = context.get("parameters").get("number")
            if number is not None:
                self.number = number


class MainTextContext(Context):
    def __init__(self, context):
        self.index = 0
        # Updates cursor with values received from the context.
        if context is not None:
            self.index = context.get("parameters").get("index")
            number = context.get("parameters").get("number")
            if number is not None:
                self.number = number


class MenuContext(Context):
    def __init__(self, context):
        self.index = 0
        # Updates cursor with values received from the context.
        if context is not None:
            self.index = context.get("parameters").get("index")
            number = context.get("parameters").get("number")
            if number is not None:
                self.number = number
