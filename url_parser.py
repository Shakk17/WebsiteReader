from bs4 import BeautifulSoup
import urllib3

import re


class UrlParser:
    def __init__(self):
        self.http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=5.0, read=5.0))

    def get_soup(self, url):
        try:
            response = self.http.request('GET', url)
        except urllib3.exceptions.MaxRetryError:
            print("Can't access this website: %s" % url)
            raise Exception("Error while visiting the page.")
        except urllib3.exceptions.LocationValueError:
            print("Not a valid URL: %s" % url)
            raise Exception("Error while visiting the page.")

        soup = BeautifulSoup(response.data, 'html.parser')
        return soup

    def get_info(self, url):
        soup = self.get_soup(url)
        # todo get info about the page.
        return soup.title.string

    def get_menu(self, url):
        soup = self.get_soup(url)
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

    def get_article(self, url, paragraph):
        # TODO recognize if page is a section or an article, behavior changes accordingly.
        soup = self.get_soup(url)
        # Find article div.
        article_div = soup.findAll(name="div", attrs={'class': 'news__content'})[0]
        # If paragraph is available, read it.
        div_paragraphs = article_div.findAll('p')
        string = "%s\n %d paragraph(s) left." % (div_paragraphs[paragraph].text, len(div_paragraphs) - paragraph)
        return string
