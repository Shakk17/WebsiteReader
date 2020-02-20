import threading
from time import time

import requests
from bs4 import BeautifulSoup

from datumbox_wrapper import DatumBox, get_language_string
from helper import get_main_container, get_clean_text, is_action_recent, get_links_positions, get_info_from_api
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
        start = time()

        # Check in the database if the web page has already been visited.
        result = Database().last_time_visited(url=self.url)
        if result is None or not is_action_recent(timestamp=result[5], days=1):
            print("Calling Aylien API to extract information...")

            # Get info from the Aylien API.
            topic, summary, language_code = get_info_from_api(url=self.url)
            language = get_language_string(language_code)

            # Save the info in the DB.
            Database().insert_page(url=self.url, topic=topic, summary=summary, language=language)

            # Analyze page.
            threading.Thread(target=self.analyze_page, args=()).start()
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

    def get_sentences(self, idx_paragraph):
        """
        Returns the text contained in the paragraph indicated in the request.
        """
        # Extract text from the database, if present.
        last_time_visited = Database().last_time_visited(url=self.url)
        if last_time_visited is None:
            raise FileNotFoundError

        text = last_time_visited[0]

        # Add the links to the text.
        links_positions = Database().get_page_links(page_url=self.url)
        for i, link in enumerate(links_positions, start=0):
            start_link = links_positions[i][0]
            if i < 10:
                string_offset = i * len(f"[LINK {i}]")
            elif i < 100:
                string_offset = 9 * len(f"[LINK 1]") + (i-9) * len(f"[LINK {i+1}]")
            else:
                string_offset = 9 * len(f"[LINK 1]") + 90 * len(f"[LINK 10]") + (i-99) * len(f"[LINK {i+1}]")
            offset = start_link + string_offset
            text = f"{text[:offset]}[LINK {i+1}]{text[offset:]}"

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
        text = get_clean_text(url=self.url)

        # Given the extracted text, get its main container.
        container = get_main_container(url=self.url, text=text)

        # Get all positions from the container's links.
        # link = position, text, url
        links = get_links_positions(container=container, text=text, url=self.url)

        # Save the text in the DB.
        Database().update_page(url=self.url, clean_text=text)

        # Save the links in the DB.
        for i, link in enumerate(links, start=1):
            Database().insert_page_link(page_url=self.url, link_num=i, link=link)
        return

# print(PageVisitor("https://en.wikipedia.org/wiki/Google_Stadia").get_main_content().text)
