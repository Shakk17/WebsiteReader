from url_parser import UrlParser


def build_response(text_response, url, paragraph=0, article=0):
    print("URL: %s - Paragraph: %d" % (url, paragraph))

    return {
        'fulfillmentText': text_response,
        "outputContexts": [{
            "name": "projects/<Project ID>/agent/sessions/<Session ID>/contexts/web-page",
            "lifespanCount": 1,
            "parameters": {
                "url": url,
                "paragraph": paragraph,
                "article": article
            }
        }]
    }


class RequestHandler:
    def __init__(self):
        self.url_parser = None

    def get_response(self, request):
        # Get action from request.
        action = request.get('queryResult').get('action')
        print("Action: " + action)

        # Get open-online context from request, if available.
        contexts = request.get("queryResult").get("outputContexts")
        context = next((x for x in contexts if "web-page" in x.get("name")), None)

        # Get context parameters from request, if available.
        try:
            # URL is either in parameters or in context.
            url = context.get("parameters").get("url")
        except TypeError:
            url = request.get("queryResult").get("parameters").get("url")
        try:
            context_paragraph = int(context.get("parameters").get("paragraph"))
            context_article = int(context.get("parameters").get("article"))
        except TypeError:
            context_paragraph = 0
            context_article = 0

        # Initiate UrlParser.
        self.url_parser = UrlParser(url=url)

        if action == "VisitPage":
            return self.visit_page()
        elif action == 'GetInfo':
            return self.get_info()
        elif action == 'GetMenu':
            return self.get_menu()
        elif action == 'ReadPage':
            return self.read_page(context_paragraph, context_article)
        elif action == "GoToSection":
            return self.go_to_section(context.get("parameters").get("section-name"))

    def visit_page(self):
        try:
            text_response = "%s visited successfully!" % self.url_parser.url
            # Understand what type of page is.
            if self.url_parser.is_article():
                text_response += "\nThis page is an article."
            else:
                text_response += "\nThis page is a section."

        except Exception as ex:
            text_response = ex.args[0]

        # Update url in context.
        return build_response(text_response, url=self.url_parser.url)

    def get_menu(self):
        menu = self.url_parser.get_menu()
        strings = [tup[1] for tup in menu]
        text_response = '-'.join(strings)
        # TODO get elements of menu, how many?
        return build_response(text_response, url=self.url_parser.url)

    def get_info(self):
        text_response = self.url_parser.get_info()
        return build_response(text_response, url=self.url_parser.url)

    def read_page(self, paragraph, article):
        # If page is article, read it. otherwise read main article titles available.
        if self.url_parser.is_article():
            try:
                text_response = self.url_parser.get_article(paragraph)
                paragraph += 1
            except IndexError as err:
                text_response = "End of article."
                paragraph = 0
        else:
            try:
                text_response = self.url_parser.get_section(article)
                article += 1
            except IndexError as err:
                text_response = "End of section."
                article = 0
        return build_response(text_response, url=self.url_parser.url, paragraph=paragraph, article=article)

    def go_to_section(self, name):
        try:
            new_url = self.url_parser.go_to_section(name)
            self.url_parser = UrlParser(new_url)
            return self.visit_page()
        except ValueError:
            return "Wrong input."
