from bs4 import BeautifulSoup
import urllib3

import re


class UrlParser:
    def __init__(self):
        self.http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=5.0, read=5.0))

    def process_url(self, url):
        try:
            response = self.http.request('GET', url)
        except urllib3.exceptions.MaxRetryError:
            print("Can't access this website: %s" % url)
            raise Exception("Error while visiting the page.")
        except urllib3.exceptions.LocationValueError:
            print("Not a valid URL: %s" % url)
            raise Exception("Error while visiting the page.")

        soup = BeautifulSoup(response.data, 'html5lib')
        return soup

    def get_title(self, request):
        return self.soup.title.string

    def get_menu(self, url):
        soup = self.process_url(url)
        # Get all the single text strings inside ul elements of class menu.
        strings = [ul_menu.text for ul_menu in soup.findAll(name="ul", attrs={'class': 'menu'})]
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
