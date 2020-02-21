import threading
from time import time

import requests
from bs4 import BeautifulSoup

from databases.database_handler import Database
from datumbox_wrapper import get_language_string
from helper import get_main_container, get_clean_text, is_action_recent, get_links_positions, get_info_from_api


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
        print("Requesting HTML web page with requests...")
        start = time()
        html = requests.get(self.url)
        print(f"Quick HTML request elapsed time: {(time() - start):.2f} s")

        return html.text

    def get_info(self):
        """
        This method gets information such as topic, summary and language from the web page.
        If the web page has not been visited recently, Aylien APIs are used to extract the information.
        If the web page has already been visited, the info is retrieved from the database.
        :return: A text response to be shown to the user containing info about the page.
        """
        start = time()

        # Check in the database if the web page has already been visited.
        result = Database().last_time_visited(url=self.url)
        action_recent = is_action_recent(timestamp=result[5], days=1)
        if result is None or not action_recent:
            print("Calling Aylien API to extract information...")

            # Get info from the Aylien API.
            topic, summary, language_code = get_info_from_api(url=self.url)
            language = get_language_string(language_code)

            if not action_recent:
                Database().delete_page(url=self.url)
                Database().delete_page_links(url=self.url)

            # Save the info in the DB.
            Database().insert_page(url=self.url, topic=topic, summary=summary, language=language)

            # Analyze the page in the background.
            threading.Thread(target=self.extract_main_text, args=()).start()
        else:
            topic, summary, language = result[1], result[2], result[3]

        text_response = (
            f"The title of this page is {BeautifulSoup(self.html_code, 'lxml').title.string}.\n"
            f"The topic of this web page is {topic}. \n"
            f"The summary of this web page is {summary}. \n"
            f"The language of this web page is {language}. \n"
        )
        print(f"TOPIC: {topic}")
        print(f"SUMMARY: {summary}")
        print(f"LANGUAGE: {language}")

        print(f"Info retrieval elapsed time: {(time() - start):.2f} s")

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
        text = last_time_visited[4]

        # Add the links indicators to the text to be returned.
        links_positions = Database().get_page_links(page_url=self.url)
        for i, link in enumerate(links_positions, start=0):
            # For each link in the main text, get the exact position in the main string.
            start_link = links_positions[i][0]

            # These offsets are necessary because the indicators [LINK n] need to be considered when calculating
            # the position of the next indicator in the string.
            if i < 10:
                string_offset = i * len(f"[LINK {i}]")
            elif i < 100:
                string_offset = 9 * len(f"[LINK 1]") + (i-9) * len(f"[LINK {i+1}]")
            else:
                string_offset = 9 * len(f"[LINK 1]") + 90 * len(f"[LINK 10]") + (i-99) * len(f"[LINK {i+1}]")

            # Add the indicator [LINK n] to the main string.
            offset = start_link + string_offset
            text = f"{text[:offset]}[LINK {i+1}]{text[offset:]}"

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
        text = get_clean_text(url=self.url)

        # Given the extracted main text, get its main HTML container.
        container = get_main_container(url=self.url, text=text)

        # Retrieve all the links from the HTML element that contains the main text.
        # link = position, text, url
        links = get_links_positions(container=container, text=text, url=self.url)

        # Save the main text in the DB.
        Database().update_page(url=self.url, clean_text=text)

        # Save the links in the DB.
        for i, link in enumerate(links, start=1):
            Database().insert_page_link(page_url=self.url, link_num=i, link=link)
