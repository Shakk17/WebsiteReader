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

    def is_article(self, url):
        soup = self.get_soup(url)
        # Count number of <article> tags in the page.
        n_articles = soup.find_all(name="article")
        return len(n_articles) < 8

    def get_article(self, url, paragraph):
        soup = self.get_soup(url)
        # Find article div.
        article_div = soup.find_all(name="div", attrs={'class': 'news__content'})[0]
        # If paragraph is available, read it.
        div_paragraphs = article_div.find_all('p')
        string = "%s\n %d paragraph(s) left." % (div_paragraphs[paragraph].text, len(div_paragraphs) - paragraph)
        return string

    def get_section(self, url, article):
        soup = self.get_soup(url)
        # Get all articles in the section.
        articles = soup.find_all(name="article")
        text_response = "Article number %s/%d \n" % (str(article+1), len(articles))
        text_response += articles[article].find(name="h2").text
        print(text_response)
        return text_response

    def get_menu(self, url):
        soup = self.get_soup(url)
        # Get all the ul of class menu.
        ul_lists = [ul_menu for ul_menu in soup.find_all(name="ul", attrs={'class': 'menu'})]
        # Get all the li elements belonging to ul of class menu.
        li_lists = [ul_list.find_all(name="li") for ul_list in ul_lists]
        # Flatten list.
        li_lists = [item for sublist in li_lists for item in sublist]
        # Get anchors.
        a_elements = [li_list.find_all(name="a") for li_list in li_lists]
        # Remove duplicates in list.
        a_elements = list(set(list(a_elements)))
        # todo sends back tuple with text and url of anchor
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

    def go_to_section(self, url, name):
        # Get menu.
        menu = self.get_menu(url)
