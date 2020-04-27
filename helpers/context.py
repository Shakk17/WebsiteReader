def assign_context(name, context):
    if name == "bookmarks":
        return BookmarksContext(context)
    elif name == "googleSearch":
        return GoogleSearchContext(context)
    elif name == "form":
        return FormContext(context)
    elif name == "functionality":
        return FunctionalityContext(context)
    elif name == "linksAll":
        return LinksAllContext(context)
    elif name == "linksArticle":
        return LinksArticleContext(context)
    elif name == "mainText":
        return MainTextContext(context)
    elif name == "menu":
        return MenuContext(context)


class Context:
    """
        An object that keeps track of the current state of the user.
        It is sent and received by the server (as a JSON) in requests and responses to the agent.
    """

    def get_dict(self):
        return vars(self)


class NavigationContext(Context):

    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.url = context.get("parameters").get("url")
            except AttributeError:
                self.url = "https://www.google.com"


class BookmarksContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except AttributeError:
                self.index = 0

            try:
                self.number = int(context.get("parameters").get("number"))
            except AttributeError:
                pass

            try:
                self.name = context.get("parameters").get("name")
            except AttributeError:
                pass


class GoogleSearchContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except AttributeError:
                self.index = 0
            try:
                self.query = context.get("parameters").get("query")
            except AttributeError:
                pass


class FormContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.idx_form = int(context.get("parameters").get("idx_form"))
            except AttributeError:
                self.idx_form = 0
            try:
                self.idx_field = int(context.get("parameters").get("idx_field"))
            except AttributeError:
                self.idx_field = 0

            try:
                self.number = int(context.get("parameters").get("number"))
            except AttributeError:
                pass

            try:
                self.user_input = context.get("parameters").get("user_input")
            except AttributeError:
                pass

            try:
                self.form_parameters = context.get("parameters").get("form_parameters")
            except AttributeError:
                pass


class FunctionalityContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except AttributeError:
                self.index = 0

            try:
                self.number = int(context.get("parameters").get("number"))
            except AttributeError:
                pass


class LinksAllContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except AttributeError:
                self.index = 0
            try:
                self.number = int(context.get("parameters").get("number"))
            except AttributeError:
                pass


class LinksArticleContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except AttributeError:
                self.index = 0
            try:
                self.number = int(context.get("parameters").get("number"))
            except AttributeError:
                pass


class MainTextContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except AttributeError:
                self.index = 0
            try:
                self.number = int(context.get("parameters").get("number"))
            except AttributeError:
                pass


class MenuContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except AttributeError:
                self.index = 0
            try:
                self.number = int(context.get("parameters").get("number"))
            except AttributeError:
                pass
