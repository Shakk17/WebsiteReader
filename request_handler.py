from url_parser import UrlParser


def build_response(text_response, url, paragraph):
    print("URL: %s - Paragraph: %d" % (url, paragraph))

    return {
        'fulfillmentText': text_response,
        "outputContexts": [{
            "name": "projects/<Project ID>/agent/sessions/<Session ID>/contexts/web-page",
            "lifespanCount": 1,
            "parameters": {
                "url": url,
                "paragraph": paragraph
            }
        }]
    }


class RequestHandler:
    def __init__(self):
        self.url_parser = UrlParser()

    def get_response(self, request):
        # Get action from request.
        action = request.get('queryResult').get('action')
        print("Action: " + action)

        # Get open-online context from request, if available.
        contexts = request.get("queryResult").get("outputContexts")
        context = next((x for x in contexts if "web-page" in x.get("name")), None)
        # Get context parameters from request, if available.
        context_url = context.get("parameters").get("url")
        context_paragraph = int(context.get("parameters").get("paragraph"))

        if action == "VisitPage":
            return self.visit_page(request)
        elif action == 'GetInfo':
            return self.get_info(context_url)
        elif action == 'GetMenu':
            return self.get_menu(context_url)
        elif action == 'ReadPage':
            return self.read_page(context_url, context_paragraph)

    def visit_page(self, request):
        # Get url from parameters.
        url = request.get("queryResult").get("parameters").get("url")
        # TODO understand what type of page is.
        try:
            self.url_parser.get_soup(url)
            text_response = "%s visited successfully!" % url
        except Exception as ex:
            text_response = ex.args[0]

        # Update url in context.
        return build_response(text_response, url, paragraph=0)

    def get_menu(self, url):
        text_response = self.url_parser.get_menu(url)
        # TODO get elements of menu, how many?
        return build_response(text_response, url=url, paragraph=0)

    def get_info(self, url):
        text_response = self.url_parser.get_info(url)
        return build_response(text_response, url=url, paragraph=0)

    def read_page(self, url, paragraph):
        # todo if page is article, read it. otherwise read main article titles available.
        try:
            text_response = self.url_parser.get_article(url, paragraph)
            paragraph += 1
        except IndexError as err:
            text_response = "End of article."
            paragraph = 0
        return build_response(text_response, url=url, paragraph=paragraph)
