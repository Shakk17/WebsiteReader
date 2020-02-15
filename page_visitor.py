from time import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from datumbox_wrapper import DatumBox


class PageVisitor:
    def __init__(self, url):
        self.url = url
        self.html_code = self.get_quick_html()
        self.soup = BeautifulSoup(self.html_code, 'lxml')
        self.datumbox = DatumBox(api_key="3670edf305888ab66dc6d9756d0f8498")

    def render_page(self):
        """
        Parses the web page specifies as URL in the class. It supports Javascript.
        Returns html code of the web page.
        """
        start = time()
        try:
            print("Rendering page with Selenium...")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(self.url)
        except Exception:
            print("Can't access this website: %s" % self.url)
            raise Exception("Error while visiting the page.")

        print("Request time: %.2f s" % (time() - start))

        html = driver.find_element_by_tag_name('html').get_attribute('innerHTML')

        return html

    def get_quick_html(self):
        print("Requesting HTML web page with requests...")
        start = time()
        html = requests.get(self.url)
        print("Request time: %.2f s" % (time() - start))

        return html.text

    def get_info(self):
        """
        Returns text containing information about the type of the web page analyzed.
        """
        text_response = f"The title of this page is {self.soup.title.string}.\n"
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

        print("Extraction time: %.2f s" % (time() - start))

        return text_response

    def get_article(self, idx_paragraph):
        """
        Returns the text contained in the paragraph indicated in the request.
        """
        # Extract text from HTML code.
        text = self.datumbox.text_extract(text=self.html_code)
        # Split up the sentences.
        split_text = text.split('.')
        string = ""
        for text in split_text[idx_paragraph:idx_paragraph+3]:
            string += f"{text}."
        string += f"\n{len(split_text) - idx_paragraph} sentence(s) left."
        return string

    def get_section(self, idx_article):
        """
        Returns a tuple (text, url) corresponding to the next article preview to be visualized.
        """
        articles = self.soup.find_all(name="article")
        text_response = "Article number %s/%d \n" % (str(idx_article + 1), len(articles))
        text_response += articles[idx_article].find(name="h2").text
        link = articles[idx_article].find(name='a').attrs["href"]
        print(text_response)
        return text_response, link

    def get_main_content(self):
        # First, render page and get DOM tree.
        rendered_html = self.html_code

        # Second, extract text from HTML code.
        text = self.datumbox.text_extract(text=rendered_html)

        # Third, get some substrings from the extracted text.
        n_substrings = 10
        substring_len = 4
        substrings = []
        for i in range(n_substrings):
            start_index = int(len(text) / n_substrings * i)
            end_index = int(start_index + substring_len)
            substrings.append(text[start_index:end_index])

        # Fourth, get all the elements from the HTML code.
        all_elements = BeautifulSoup(rendered_html, 'lxml').find_all()

        # Fifth, for each element, check if it contains all the substrings.
        candidates = []
        for element in all_elements:
            element_text = element.get_text()
            counter = 0
            for substring in substrings:
                if substring in element_text:
                    counter += 1
            # If the element contains at least half the substrings, it is a candidate element.

            if counter > n_substrings / 2:
                # Now I select the deepest element between the candidates.
                candidates.append(element)

        candidates.sort(key=lambda x: len(list(x.parents)), reverse=True)

        print()

PageVisitor("http://www.floriandaniel.it/").get_main_content()