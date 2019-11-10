from bs4 import BeautifulSoup
import urllib3

from dialogflow_helper import DialogFlowHelper

import re


def build_response(text_response, url, paragraph):
    print("URL: %s - Paragraph: %d" % (url, paragraph))

    return {
        'fulfillmentText': text_response,
        "outputContexts": [{
            "name": "projects/<Project ID>/agent/sessions/<Session ID>/contexts/open-online",
            "lifespanCount": 1,
            "parameters": {
                "url": url,
                "paragraph": paragraph
            }
        }]
    }


class OpenReader:
    def __init__(self):
        self.http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=5.0, read=5.0))
        self.response = self.http.request('GET', 'open.online')
        self.soup = BeautifulSoup(self.response.data, 'html5lib')

    def get_response(self, request):
        # Get action from request.
        action = request.get('queryResult').get('action')
        print("Action: " + action)

        # Get open-online context from request, if available.
        contexts = request.get("queryResult").get("outputContexts")
        context = next((x for x in contexts if "open-online" in x.get("name")), None)
        # Get context parameters from request, if available.
        context_url = context.get("name")
        context_paragraph = context.get("paragraph")

        if action == "VisitPage":
            url = request.get("queryResult").get("parameters").get("url")
            # TODO understand what type of page is.

            text_response = "Page visited!"
            return build_response(text_response, url, paragraph=0)
        elif action == 'GetTitle':
            return build_response(self.get_title(request), url=context_url, paragraph=context_paragraph)
        elif action == 'GetMenu':
            # TODO get elements of menu, how many?
            return build_response(self.get_menu(request), url=context_url, paragraph=context_paragraph)
        elif action == 'ReadPage':
            # todo if page is article, read it. otherwise read main article titles available.
            return build_response(self.get_article(request), url=context_url, paragraph=context_paragraph)

    def get_title(self, request):
        return self.soup.title.string

    def get_menu(self, request):
        # Get all the single text strings inside ul elements of class menu.
        strings = [ul_menu.text for ul_menu in self.soup.findAll(name="ul", attrs={'class': 'menu'})]
        strings = [string.split('\n') for string in strings]
        # Flatten list while removing whitespaces.
        strings = [item.strip() for sublist in strings for item in sublist]
        # Filter out empty elements.
        r = re.compile(".*\w+.*")
        strings = list(filter(r.match, strings))
        # Remove duplicates.
        strings = list(set(strings))
        joined_strings = ', '.join(strings)
        print(joined_strings)
        return joined_strings

    def get_article(self, request):
        article_url = request.get('queryResult').get('outputContexts')[0].get('parameters').get('page-url')
        # TODO recognize if page is a section or an article, behavior changes accordingly.

