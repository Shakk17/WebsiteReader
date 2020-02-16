from time import time
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from datumbox_wrapper import DatumBox
from sd_alg.sd_algorithm import SDAlgorithm


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

        print(f"Selenium request elapsed time: {(time() - start):.2f} s")

        html = driver.find_element_by_tag_name('html').get_attribute('innerHTML')

        return html

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

        print(f"Info retrieval elapsed time: {(time() - start):.2f} s")

        return text_response

    def get_sentences(self, idx_paragraph):
        """
        Returns the text contained in the paragraph indicated in the request.
        """
        # Extract text from HTML code.
        text = self.get_main_content().text
        # Split up the sentences.
        split_text = text.split('.')

        # If we reached the end of the text, raise IndexError and reset the counter.
        if idx_paragraph > len(split_text):
            raise IndexError

        string = ""
        for text in split_text[idx_paragraph:idx_paragraph+3]:
            string += f"{text}."

        string += f"\n{min(idx_paragraph + 3, len(split_text))} out of {len(split_text)} sentence(s) read."
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
        """
        Given the URL present in PageVisitor, returns the element containing the main content of the web page.
        It uses the SD algorithm to analyse the rendered HTML of the web page.
        :return: The HTML element containing the main content of the page.
        """
        # First, render page and get DOM tree.
        rendered_html = self.render_page()

        # Second, extract text from HTML code.
        # text = self.datumbox.text_extract(text=rendered_html)
        text = SDAlgorithm(rendered_html).analyze_page()

        # Third, get all words from text composed by 4+ characters.
        words = re.findall(r'\w+', text)
        words = set([word for word in words if len(word) > 3])

        # Fourth, get all the elements from the HTML code.
        all_elements = BeautifulSoup(rendered_html, 'lxml').find_all()

        # Fifth, for each element, check how many text words it contains.
        candidates = []
        for element in all_elements:
            element_text = element.get_text()
            counter = 0
            for word in words:
                if word in element_text:
                    counter += 1
            # If the element contains at least 75% of the words, it is a candidate element.
            if counter > len(words) * 0.75:
                candidates.append((element, counter))

        # Sixth, order the candidates depending on their depth in the DOM tree.
        candidates.sort(key=lambda x: len(list(x[0].parents)), reverse=True)

        return candidates[0][0]

# print(PageVisitor("https://en.wikipedia.org/wiki/Google_Stadia").get_main_content().text)