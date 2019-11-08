from bs4 import BeautifulSoup
import urllib3

import re


def build_response(response):

    return {
        'fulfillmentText': response,
    }


class OpenReader:
    def __init__(self):
        self.http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=5.0, read=5.0))
        self.response = self.http.request('GET', 'https://www.independent.co.uk/')
        self.soup = BeautifulSoup(self.response.data, 'html5lib')

    def get_response(self, request):
        action = request.get('queryResult').get('action')
        print("Action: " + action)

        if action == 'GetTitle':
            return build_response(self.get_title())
        elif action == 'GetMenu':
            return build_response(self.get_menu())

    def get_title(self):
        return self.soup.title.string

    def get_menu(self):
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

