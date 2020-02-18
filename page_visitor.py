from time import time

import requests
from bs4 import BeautifulSoup

from datumbox_wrapper import DatumBox
from helper import get_main_container, get_clean_text, is_action_recent
from databases.database_handler import Database


class PageVisitor:
    def __init__(self, url, quick_download=True):
        self.url = url
        self.html_code = None
        if quick_download:
            self.html_code = self.get_quick_html()
        self.datumbox = DatumBox(api_key="3670edf305888ab66dc6d9756d0f8498")

    def get_quick_html(self):
        print("Requesting HTML web page with requests...")
        start = time()
        html = requests.get(self.url)
        print(f"Quick HTML request elapsed time: {(time() - start):.2f} s")

        return html.text

    def get_info(self):
        """
        Returns text containing information about the type of the web page analyzed.
        """
        text_response = f"The title of this page is {BeautifulSoup(self.html_code, 'lxml').title.string}.\n"
        print("Extracting text...")
        start = time()

        # Extract text from HTML code.
        text = self.datumbox.text_extract(text=self.html_code)

        # Get topic from text extracted.
        topic = self.datumbox.topic_classification(text=text)
        print(f"TOPIC: {topic}")
        text_response += f"The topic of this web page is {topic}. \n"

        # Detect language.
        language = self.datumbox.detect_language(text=text)
        print(f"LANGUAGE: {language}")
        text_response += f"The language of this web page is {language}. \n"

        print(f"Info retrieval elapsed time: {(time() - start):.2f} s")

        return text_response

    def get_sentences(self, idx_paragraph):
        """
        Returns the text contained in the paragraph indicated in the request.
        """
        # Extract text from HTML code.
        text = get_main_content(self.url).get_text()
        # Split up the sentences.
        split_text = text.split('.')

        # If we reached the end of the text, raise IndexError and reset the counter.
        if idx_paragraph > len(split_text):
            raise IndexError

        string = ""
        for text in split_text[idx_paragraph:idx_paragraph + 2]:
            string += f"{text}."

        string += f"\n{min(idx_paragraph + 2, len(split_text))} out of {len(split_text)} sentence(s) read."
        return string

    def analyze_page(self):
        # Check if page has already been visited recently.
        result = Database().last_time_visited(url=self.url)
        if result is None or not is_action_recent(timestamp=result[1], days=1):
            # If not, I get the clean text from it.
            text = get_clean_text(url=self.url)
        else:
            text = result[0]

        # Given the extracted text, get its main container.
        container = get_main_container(url=self.url, text=text)

        # Get all the links from the container.
        links = container.find_all('a')

        # For each link, if their link_text is present in the text, add [link n] after them.
        for link in links:
            # Get the text of the link.
            text_link = link.contents[0]
            if not isinstance(text_link, str):
                continue
            position = text.find(text_link)
            if position >= 0 and text_link != '':
                position += len(text_link)
                text = f"{text[:position]} [LINK n]{text[position:]}"

        # Save the text in the DB.
        Database().insert_page(url=self.url, clean_text=text)
        return

# print(PageVisitor("https://en.wikipedia.org/wiki/Google_Stadia").get_main_content().text)
