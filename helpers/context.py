def assign_context(name, context):
    if name == "bookmarks":
        return BookmarksContext(context)
    elif name == "googlesearch":
        return GoogleSearchContext(context)
    elif name == "form":
        return FormContext(context)
    elif name == "functionality":
        return FunctionalityContext(context)
    elif name == "links_all":
        return LinksAllContext(context)
    elif name == "links_article":
        return LinksArticleContext(context)
    elif name == "maintext":
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
            except Exception:
                self.url = "https://www.google.com"


class BookmarksContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except Exception:
                self.index = 0

            try:
                self.number = int(context.get("parameters").get("number"))
            except Exception:
                pass

            try:
                self.name = context.get("parameters").get("name")
            except Exception:
                pass


class GoogleSearchContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except Exception:
                self.index = 0
            try:
                self.query = context.get("parameters").get("query")
            except Exception:
                pass


class FormContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.idx_form = int(context.get("parameters").get("idx_form"))
            except Exception:
                self.idx_form = 0
            try:
                self.idx_field = int(context.get("parameters").get("idx_field"))
            except Exception:
                self.idx_field = 0

            try:
                self.number = int(context.get("parameters").get("number"))
            except Exception:
                pass

            try:
                self.user_input = context.get("parameters").get("user_input")
            except Exception:
                pass

            try:
                self.form_parameters = context.get("parameters").get("form_parameters")
            except Exception:
                pass


class FunctionalityContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except Exception:
                self.index = 0

            try:
                self.number = int(context.get("parameters").get("number"))
            except Exception:
                pass


class LinksAllContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except Exception:
                self.index = 0
            try:
                self.number = int(context.get("parameters").get("number"))
            except Exception:
                pass


class LinksArticleContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except Exception:
                self.index = 0
            try:
                self.number = int(context.get("parameters").get("number"))
            except Exception:
                pass


class MainTextContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except Exception:
                self.index = 0
            try:
                self.number = int(context.get("parameters").get("number"))
            except Exception:
                pass


class MenuContext(Context):
    def __init__(self, context):
        # Updates cursor with values received from the context.
        if context is not None:
            try:
                self.index = int(context.get("parameters").get("index"))
            except Exception:
                self.index = 0
            try:
                self.number = int(context.get("parameters").get("number"))
            except Exception:
                pass
