import threading

import requests
from bs4 import BeautifulSoup

from databases.crawler_links_handler import db_delete_all_domain_crawler_links, db_get_crawler_links
from databases.pages_handler import db_add_parsed_html_to_page, db_get_page, db_delete_page, db_insert_page, db_update_page
from databases.text_links_handler import db_delete_text_links, db_insert_text_link, db_get_text_links
from databases.websites_handler import db_delete_website, db_last_time_crawled
from helpers import helper
from helpers.api import get_text_from_aylien_api
from helpers.browser import scrape_page
from helpers.helper import is_action_recent
from helpers.utility import extract_words, get_time, get_domain, add_schema
from scraping.crawler_handler import Crawler


class PageVisitor:
    """
    An object that holds the HTML code (no JS support to be loaded quicker) of a web page.
    """

    def __init__(self, url, quick_download=True):
        self.url = url
        self.html_code = None
        if quick_download:
            self.html_code = self.get_simple_html()

    def get_simple_html(self):
        """
        This method returns the HTML code of the web page.
        For speed purposes, Javascript is not supported.
        :return: The HTML code of the web page.
        """
        print(f"{get_time()} [{self.url}] SIMPLE HTML code get started.")
        html = requests.get(self.url).text
        print(f"{get_time()} [{self.url}] SIMPLE HTML code get finished.")

        return html

    def save_parsed_html(self):
        print(f"{get_time()} [{self.url}] PARSED HTML code get started.")
        parsed_html = scrape_page(self.url)
        db_add_parsed_html_to_page(url=self.url, parsed_html=parsed_html)
        print(f"{get_time()} [{self.url}] PARSED HTML code get finished.")

    def analyze_page(self):
        print(f"{get_time()} [{self.url}] Analysis started.")

        # Check in the database if the web page has already been visited.
        result = db_get_page(url=self.url)
        get_new_page = False
        # Delete, if present, an obsolete version of the page.
        if result is not None and not helper.is_action_recent(timestamp=result[6], days=0, minutes=1):
            print("Page present, but obsolete.")
            db_delete_page(url=self.url)
            db_delete_text_links(url=self.url)
            get_new_page = True
        # If the page is not present in memory.
        if result is None:
            print("Page not present.")
            get_new_page = True

        if get_new_page:
            # Get info from the Aylien API.
            topic = "unknown"
            language = "unknown"
            # Save the info in the DB.
            db_insert_page(url=self.url, topic=topic, language=language, simple_html=self.html_code)
            db_add_parsed_html_to_page(url=self.url, parsed_html="In progress.")

            # Parse the page in the background.
            threading.Thread(target=self.extract_content, args=()).start()

        print(f"{get_time()} [{self.url}] Analysis finished.")

    def extract_content(self):
        print("[EXTRACT CONTENT] Start.")
        # Render the page and save it in the database.
        self.save_parsed_html()
        # Extract the main text by using external APIs and parsed html code.
        self.extract_main_text()
        print("[EXTRACT CONTENT] Finish.")

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
        db_update_page(url=self.url, clean_text=text)

        # Save the links in the DB.
        for i, link in enumerate(links, start=1):
            db_insert_text_link(page_url=self.url, link_num=i, link=link)

    def get_info(self):
        """
        This method gets information such as topic, summary and language from the web page.
        If the web page has not been visited recently, Aylien APIs are used to extract the information.
        If the web page has already been visited, the info is retrieved from the database.
        :return: A text response to be shown to the user containing info about the page.
        """
        page = db_get_page(self.url)
        text_response = (
            f"The title of this page is {BeautifulSoup(self.html_code, 'lxml').title.string}.\n"
            f"The topic of this web page is {page[1]}. \n"
            f"The language of this web page is {page[2]}. \n"
        )

        # Extract all the search forms present in the page.
        search_form = self.extract_search_forms()
        if len(search_form) > 0:
            text_response += f"There are search forms in this page called {search_form}"

        return text_response

    def analyze_domain(self):
        # Checks if domain has been already crawled.
        domain = get_domain(url=self.url)
        to_crawl = False
        last_crawling = db_last_time_crawled(domain)

        # Delete, if present, an obsolete crawling.
        if last_crawling is not None and not is_action_recent(timestamp=last_crawling, days=0, minutes=1):
            db_delete_all_domain_crawler_links(domain)
            db_delete_website(domain)
            to_crawl = True

        # If there is no crawling of the domain.
        if last_crawling is None:
            to_crawl = True

        # Crawl in the background.
        if to_crawl:
            threading.Thread(target=Crawler(start_url=domain).run, args=()).start()
            # If the URL contains a subdomain, crawl it too.
            complete_domain = get_domain(self.url, complete=True)
            if domain != complete_domain:
                threading.Thread(target=Crawler(start_url=complete_domain).run, args=()).start()

        # Check if the homepage of the domain has already been visited.
        page = db_get_page(add_schema(domain))
        if page[4] is None:
            # Get all the link
            threading.Thread(target=scrape_page, args=(self.url,)).start()



























    def get_sentences(self, idx_sentence, n_sentences):
        """
        This method returns a number of sentences from the main text of the web page.
        :param idx_sentence: The index of the first sentence to be retrieved.
        :param n_sentences: The number of sentences to be retrieved.
        :return: A string containing some sentences from the main text of the web page.
        """
        # Check if the text is actually present in the database.
        last_time_visited = db_get_page(url=self.url)
        if last_time_visited is None:
            raise FileNotFoundError

        # Get the text from the database.
        text = last_time_visited[3]
        # Check that the web page has already been analyzed.
        if text is None:
            raise FileNotFoundError

        # Add the links indicators to the text to be returned.
        links_positions = db_get_text_links(page_url=self.url)
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

    def read_links(self, url):
        links = db_get_crawler_links(url=url)
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
