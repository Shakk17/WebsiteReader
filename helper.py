import html
import re
import urllib.parse
from datetime import datetime
from time import time

import tldextract
from aylienapiclient import textapi
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from databases.database_handler import Database

client = textapi.Client("b50e3216", "0ca0c7ad3a293fc011883422f24b8e73")

chrome_options = Options()
chrome_options.add_argument("--headless")

# Avoid loading images.
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# HEROKU
"""chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")"""


def strip_html_tags(text):
    """
    This method takes a string of text, unescapes special characters and removes any HTML tag from it.
    :param text: A string of text.
    :return: A string without escaped characters or HTML tags.
    """
    # Unescape difficult character like &amp;.
    text = html.unescape(str(text))
    # Remove all the html tags.
    regex = re.compile(r'<[^>]+>')
    text = regex.sub('', text)
    # Remove \n and \t.
    text = text.replace("\\n", " ")
    text = text.replace("\\t", " ")
    # Remove spaces at the beginning and at the end of the string.
    text = text.strip()
    return text

def get_urls_from_google(query):
    """
    This method makes a search on Google and returns the first 5 results.
    :param query: A string containing the query to input into Google Search.
    :return: A list containing tuples (title, URL, snippet) of the first 5 results.
    """
    start = time()
    # Perform Google Search.
    api_key = "AIzaSyBxmCvHuuBmno25vybpLHEmVL1sOZusYa0"
    cse_id = "001618926378962890992:ri89cvvqaiw"
    query_service = build(serviceName="customsearch", version="v1", developerKey=api_key)
    query_results = query_service.cse().list(q=query, cx=cse_id).execute().get("items")

    results = [(result.get("title"), result.get("link"), result.get("snippet")) for result in query_results]

    return results


def get_domain(url):
    """
    This method extracts the domain from the URL of a website.
    :param url: A string containing the URL.
    :return: A string containing the domain extracted from the URL.
    """
    extracted_domain = tldextract.extract(url)
    domain = "{}.{}".format(extracted_domain.domain, extracted_domain.suffix)
    return domain


def get_menu(url):
    """
    This method returns all the links belonging to the menu of a web page.
    :param url: A string containing the URL of the web page.
    :return: An array of tuples (number, link_text, link_url, avg_x, avg_y) ordered by number DESC.
    """
    # Get menu of the domain that contains the web page.
    domain = get_domain(url)
    menu = (Database().analyze_scraping(domain))
    menu = [list(element) for element in menu]

    # Remove all the tags from the text fields of the links.
    for i, element in enumerate(menu):
        menu[i][1] = strip_html_tags(element[1])

    # Remove elements of the menu with empty texts.
    menu = list(filter(lambda x: len(x[1]) > 0, menu))

    # Remove elements of the menu that are not frequent.
    highest_freq = menu[0][0]
    threshold = 0.10
    menu = list(filter(lambda x: x[0] > highest_freq * threshold, menu))

    return menu


def get_menu_link(url, number):
    """
    This method returns the URL of a link belonging to the menu of a web page.
    :param url: A string containing the URL of the web page.
    :param number: The position of the link to be retrieved in the list of menu links. 0 is not valid.
                    To get the first element, number has to be 1, not 0.
    :return: A string containing the URL of the link requested.
    """
    # Get all the menu links.
    menu = get_menu(url)
    # Get all the URLs of the menu links.
    menu_anchors = [tup[2] for tup in menu]
    index = number - 1

    return menu_anchors[index]


def fix_url(url):
    """
    This method takes a URL and returns a well-formed URL. If the schema is missing, it will get added.
    :param url: A string containing a URL.
    :return: A string containing a well-formed URL.
    """
    if not re.match('(?:http|ftp|https)://', url):
        return 'http://{}'.format(url)
    return url


def get_main_container(url, text):
    """
    This method takes a web page and its main text, and returns the deepest element (in the DOM tree) containing it.
    :param url: A string containing the URL of the web page.
    :param text: A string containing the main text of the web page.
    :return: The HTML code of the deepest element containing the main text.
    """

    # First, render the HTML code of the page to get the DOM tree. JavaScript is supported.
    rendered_html = render_page(url)

    # Second, get all words composed by 4+ characters from the main text.
    words = re.findall(r'\w+', text)
    words = set([word for word in words if len(word) > 3])

    # Third, get all the elements from the HTML code.
    all_elements = BeautifulSoup(rendered_html, 'lxml').find_all()

    # Fourth, for each element, check how many text words it contains.
    candidates = []
    for element in all_elements:
        element_text = element.get_text()
        counter = 0
        for word in words:
            if word in element_text:
                counter += 1
        # If the element contains at least 75% of the main text words, it is a candidate element.
        if counter > len(words) * 0.75:
            candidates.append((element, counter))

    # Fifth, order the candidates depending on their depth in the DOM tree.
    candidates.sort(key=lambda x: len(list(x[0].parents)), reverse=True)

    # Sixth, select the deepest element in the DOM tree from all the candidates.
    html_element = candidates[0][0]

    return html_element


def render_page(url):
    """
    This method returns the HTML code of a web page. It uses Selenium, thus it supports Javascript.
    :param url: A string containing the URL of the web page to parse.
    :return: The HTML code of the web page.
    """
    start = time()
    try:
        print("Rendering page with Selenium...")
        # HEROKU:
        # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        # LOCAL:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
    except Exception:
        print(f"Can't access this website: {url}")
        raise Exception("Error while visiting the page.")

    print(f"Selenium request elapsed time: {(time() - start):.2f} s")

    html_code = driver.find_element_by_tag_name('html').get_attribute('innerHTML')

    return html_code


def get_info_from_api(url):
    """
    This method returns info regarding a certain web page by using Aylien APIs.
    :param url: A string containing the URL of the web page.
    :return: A tuple (topic, language) containing info about the web page.
    """
    # This is a combined call to the Aylien APIs.
    combined = client.Combined({
        'url': url,
        'endpoint': ["classify", "language"]
    })

    language = combined.get("results")[0].get("result").get("lang")

    # The topic is returned only if it the level of confidence is over a certain threshold.
    try:
        topic_confidence = combined.get("results")[1].get("result").get("categories")[0].get("confidence")
        if topic_confidence > 0.3:
            topic = combined.get("results")[1].get("result").get("categories")[0].get("label")
        else:
            topic = "unknown"
    except IndexError:
        topic = "unknown"

    return topic, language


def get_clean_text(url):
    """
    This method utilizes an Aylien API to extract the main text from a web page.
    :param url: A string containing the URL of the web page.
    :return: A string containing the main text of the web page.
    """
    start = time()
    text = client.Extract({'url': url})
    print(f"Aylien API extract text elapsed time: {(time() - start):.2f}")
    return text.get("article")


def is_action_recent(timestamp, days):
    """
    This method compares a timestamp to the actual date.
    :param timestamp: A string in the format "%Y-%m-%d %H:%M:%S".
    :param days: An integer indicating the threshold defining when an action is recent.
    :return: True is the timestamp inserted is a date that happened more than "days" days ago, False otherwise.
    """
    t1 = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    t2 = datetime.now()
    difference = t2 - t1

    return difference.days < days


def get_links_positions(container, text, url):
    """
    This is a method that returns the positions of the links in the string containing the main text of a web page.
    :param container: The HTML element containing the main text of the web page.
    :param text: A string containing the main text of the web page.
    :param url: A string containing the URL of the web page.
    :return: A list of tuples (position, text, url).
    """

    # Get all the links present in the container.
    container_links = container.find_all('a')

    # Filter out the links that do not contain a string.
    container_links = list(filter(lambda link: len(link.contents) > 0, container_links))

    # Save the links in an array containing tuples (text, url).
    text_links = [(link.get_text(), link.get("href")) for link in container_links if isinstance(link.contents[0], str)]

    # Sort the links putting the ones with the longest texts first.
    text_links.sort(key=lambda link: len(link[0]), reverse=True)

    # Create a list holding all the positions in the main text.
    links = []

    # For each link in the container, get its position in the clean text.
    positions_taken = []
    for text_link in text_links:
        position = -1

        # Get all the link's text occurrences in the main text.
        indexes = [m.start() for m in re.finditer(f"\\b{re.escape(text_link[0])}\\b", text)]

        # Assign the first position available to the new link.
        for index in indexes:
            if index not in positions_taken:
                position = index
                break

        # Get absolute URL of link.
        link_url = urllib.parse.urljoin(url, text_link[1])

        # Check if the link has a position assigned in the main text and its text is not empty.
        if position >= 0 and text_link[0] != '':
            # Occupy all the positions in the text now occupied by the link's text.
            for x in range(len(text_link[0])):
                positions_taken.append(position + x)

            # Append a tuple (position, text, url) to the links array.
            links.append((position, text_link[0], link_url))

    # Sort links depending on their position in the main text.
    links.sort(key=lambda link: link[0], reverse=False)

    # Add offset to positions in order to point at the end of the link text.
    links = [(link[0] + len(link[1]), link[1], link[2]) for link in links]
    return links


def extract_search_forms(html_code):
    """
    This method searches in the web page if there is an input form used to search something in the page.
    :return: The text of the input form, if present. None otherwise.
    """
    webpage = BeautifulSoup(html_code, "lxml")
    search_input_forms = webpage.find_all(name='input', attrs={"type": "search"})
    text_input_forms = webpage.find_all(name='input', attrs={"type": "text"})
    input_forms = search_input_forms + text_input_forms
    input_forms_text = [x.get("placeholder") for x in input_forms]
    return input_forms_text
