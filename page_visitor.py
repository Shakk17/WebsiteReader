import threading
from time import time

import requests
from bs4 import BeautifulSoup

from databases.database_handler import Database
from datumbox_wrapper import get_language_string
from helpers import helper
from helpers.api import get_info_from_aylien_api, get_text_from_aylien_api
from helpers.utility import extract_words


class PageVisitor:
    """
    An object that holds the HTML code (no JS support to be loaded quicker) of a web page.
    """

    def __init__(self, url, quick_download=True):
        self.url = url
        self.html_code = None
        if quick_download:
            self.html_code = self.get_quick_html()

    def get_quick_html(self):
        """
        This method returns the HTML code of the web page.
        For speed purposes, Javascript is not supported.
        :return: The HTML code of the web page.
        """
        print("[WEB PAGE] Getting HTML code (requests).")
        start = time()
        html = requests.get(self.url)
        print(f"[WEB PAGE] Quick HTML request elapsed time: {(time() - start):.2f} s")

        return html.text

    def get_info(self):
        """
        This method gets information such as topic, summary and language from the web page.
        If the web page has not been visited recently, Aylien APIs are used to extract the information.
        If the web page has already been visited, the info is retrieved from the database.
        :return: A text response to be shown to the user containing info about the page.
        """
        start = time()
        print("[WEB PAGE] Extracting information.")

        # Check in the database if the web page has already been visited.
        result = Database().last_time_visited(url=self.url)

        # If there is already info about the web page, but it's not recent, delete it.
        if result is not None and not helper.is_action_recent(timestamp=result[4], days=0, minutes=30):
            Database().delete_page(url=self.url)
            Database().delete_text_links(url=self.url)

        if result is None:
            # Get info from the Aylien API.
            topic = "unknown"
            language = "unknown"

            # Save the info in the DB.
            Database().insert_page(url=self.url, topic=topic, language=language)

            # Analyze the page in the background.
            threading.Thread(target=self.extract_main_text, args=()).start()
        else:
            topic, language = result[1], result[2]

        search_form = self.extract_search_forms()

        text_response = (
            f"The title of this page is {BeautifulSoup(self.html_code, 'lxml').title.string}.\n"
            f"The topic of this web page is {topic}. \n"
            f"The language of this web page is {language}. \n"
        )

        if len(search_form) > 0:
            text_response += f"There are search forms in this page called {search_form}"

        print(f"[WEB PAGE] Info retrieval: {(time() - start):.2f} s")

        return text_response

    def get_sentences(self, idx_sentence, n_sentences):
        """
        This method returns a number of sentences from the main text of the web page.
        :param idx_sentence: The index of the first sentence to be retrieved.
        :param n_sentences: The number of sentences to be retrieved.
        :return: A string containing some sentences from the main text of the web page.
        """
        # Check if the text is actually present in the database.
        last_time_visited = Database().last_time_visited(url=self.url)
        if last_time_visited is None:
            raise FileNotFoundError

        # Get the text from the database.
        text = last_time_visited[3]
        # Check that the web page has already been analyzed.
        if text is None:
            raise FileNotFoundError

        # Add the links indicators to the text to be returned.
        links_positions = Database().get_text_links(page_url=self.url)
        for i, link in enumerate(links_positions, start=0):
            # For each link in the main text, get the exact position in the main string.
            start_link = links_positions[i][0]

            # These offsets are necessary because the indicators [LINK n] need to be considered when calculating
            # the position of the next indicator in the string.
            if i < 10:
                string_offset = i * len(f"[LINK {i}]")
            elif i < 100:
                string_offset = 9 * len(f"[LINK 1]") + (i - 9) * len(f"[LINK {i + 1}]")
            else:
                string_offset = 9 * len(f"[LINK 1]") + 90 * len(f"[LINK 10]") + (i - 99) * len(f"[LINK {i + 1}]")

            # Add the indicator [LINK n] to the main string.
            offset = start_link + string_offset
            text = f"{text[:offset]}[LINK {i + 1}]{text[offset:]}"

        # Split up the main text in sentences.
        split_text = text.split('.')

        # Once the end of the main text has been reached, raise IndexError.
        if idx_sentence > len(split_text):
            raise IndexError

        # Add only the requested sentences to the text to be returned.
        string = ""
        for text in split_text[idx_sentence:idx_sentence + n_sentences]:
            string += f"{text}."

        # Let the user know about how long it will take to finish the reading of the main text.
        string += f"\n{min(idx_sentence + n_sentences, len(split_text))} out of {len(split_text)} sentence(s) read."
        return string

    def extract_main_text(self):
        """
        This method uses an Aylien API to extract the main text (and its links) from a web page.
        After the extraction, text and links of the web page are saved in the database.
        """
        # Get the main text of the web page.
        text = get_text_from_aylien_api(url=self.url)

        # Given the extracted main text, get its main HTML container.
        container = helper.get_main_container(url=self.url, text=text)

        # Retrieve all the links from the HTML element that contains the main text.
        # link = position, text, url
        links = helper.get_links_positions(container=container, text=text, url=self.url)

        # Save the main text in the DB.
        Database().update_page(url=self.url, clean_text=text)

        # Save the links in the DB.
        for i, link in enumerate(links, start=1):
            Database().insert_text_link(page_url=self.url, link_num=i, link=link)

    def read_links(self, url):
        links = Database().get_crawler_links(url=url)
        texts = []
        new_links = []
        if len(links) > 0:
            # Keep only links with 4 words or more in text.
            links = list(filter(lambda x: len(extract_words(x[0])) > 3, links))
            # Keep only links not contained in lists.
            links = list(filter(lambda x: x[3] == 0, links))
            # Order link depending on their y_position.
            links.sort(key=lambda x: x[2])
            # Remove duplicates.
            new_links = []
            for link in links:
                if link[0] not in texts:
                    new_links.append(link)
                    texts.append(link[0])

        return new_links

    def extract_search_forms(self):
        """
        This method searches in the web-page if there is an input form used to search something in the page.
        :return: The text of the input form, if present. None otherwise.
        """
        webpage = BeautifulSoup(self.html_code, "lxml")
        search_input_forms = webpage.find_all(name='input', attrs={"type": "search"})
        text_input_forms = webpage.find_all(name='input', attrs={"type": "text"})
        input_forms = search_input_forms + text_input_forms
        input_forms_text = [x.get("placeholder") for x in input_forms]
        return input_forms_text
