from requests_html import HTMLSession
from bs4 import BeautifulSoup

from time import time


class UrlParser:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup(url)

    def get_soup(self, url):
        start = time()
        try:
            session = HTMLSession()
            response = session.get(url=url)
        except Exception:
            print("Can't access this website: %s" % url)
            raise Exception("Error while visiting the page.")

        print("Request time: %.2f s" % (time() - start))

        response.html.arender()
        soup = BeautifulSoup(response.html.html, 'lxml')
        response.close()
        session.close()
        return soup

    def get_info(self):
        text_response = "The title of this page is %s.\n" % self.soup.title.string
        if self.is_article():
            text_response += "This page is an article!"
        else:
            text_response += "This page is a section!"
        return text_response

    def is_article(self):
        # Count number of <article> tags in the page.
        n_articles = self.soup.find_all(name="article")
        return len(n_articles) < 8

    def get_article(self, paragraph):
        # Find article div.
        article_div = self.soup.find_all(name="div", attrs={'class': 'news__content'})[0]
        # If paragraph is available, read it.
        div_paragraphs = article_div.find_all('p')
        string = "%s\n %d paragraph(s) left." % (div_paragraphs[paragraph].text, len(div_paragraphs) - paragraph)
        return string

    def get_section(self, idx_article):
        # Get all articles in the section.
        articles = self.soup.find_all(name="article")
        text_response = "Article number %s/%d \n" % (str(idx_article + 1), len(articles))
        text_response += articles[idx_article].find(name="h2").text
        link = articles[idx_article].find(name='a').attrs["href"]
        print(text_response)
        return text_response, link

    def get_menu(self):
        # Get all the ul of class menu.
        ul_lists = [ul_menu for ul_menu in self.soup.find_all(name="ul", attrs={'class': 'menu'})]
        # Get all the li elements belonging to ul of class menu.
        li_lists = [ul_list.find_all(name="li") for ul_list in ul_lists]
        # Flatten list.
        li_lists = [item for sublist in li_lists for item in sublist]
        # Get anchors.
        a_elements = [li_list.find(name="a") for li_list in li_lists]
        # Remove duplicates in list.
        a_elements = list(set(a_elements))
        # Sends back tuple with url and text of anchor.
        elements = [(elem.attrs["href"], elem.text) for elem in a_elements]
        return elements

    def go_to_section(self, name):
        # Get menu.
        menu = self.get_menu()
        menu_anchors = [tup[0] for tup in menu]
        menu_strings = [tup[1] for tup in menu]
        # Put all the strings to lowercase.
        menu_strings = [string.lower() for string in menu_strings]
        # Return index of string, if present. Otherwise IndexError.
        index = menu_strings.index(name.lower())
        return menu_anchors[index]
