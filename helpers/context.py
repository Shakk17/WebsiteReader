def assign_context(name, context):
    if "bookmarks" in name:
        return "bookmarks", BookmarksContext(context)
    elif "googlesearch" in name:
        return "googlesearch", GoogleSearchContext(context)
    elif "form" in name:
        return "form", FormContext(context)
    elif "functionality" in name:
        return "functionality", FunctionalityContext(context)
    elif "links_all" in name:
        return "links_all", LinksAllContext(context)
    elif "links_article" in name:
        return "links_article", LinksArticleContext(context)
    elif "maintext" in name:
        return "maintext", MainTextContext(context)
    elif "menu" in name:
        return "menu", MenuContext(context)


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
