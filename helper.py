import re
from time import time
import html

import tldextract
from bs4 import BeautifulSoup
from googlesearch import search
from datetime import datetime

from databases.database_handler import Database
from sd_alg.sd_algorithm import SDAlgorithm

from aylienapiclient import textapi

client = textapi.Client("b50e3216", "0ca0c7ad3a293fc011883422f24b8e73")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
# Avoid loading images.
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)


def strip_html_tags(text):
    text = html.unescape(str(text))
    regex = re.compile(r'<[^>]+>')
    return regex.sub('', text)


def get_url_from_google(query):
    start = time()
    result = search(query, tld='com', lang='en', num=1, start=0, pause=0.0)
    for res in result:
        print("Time elapsed for Google Search: %.2f s" % (time() - start))
        return res


def get_domain(url):
    extracted_domain = tldextract.extract(url)
    domain = "{}.{}".format(extracted_domain.domain, extracted_domain.suffix)
    return domain


def get_menu(url):
    """
    Analyze the scraped pages from the url's domain, then returns the 10 most frequent links.
    Returns a list of tuples (text, url) corresponding to the anchors present in the menu.
    """
    # Get menu of domain.
    domain = get_domain(url)
    menu = (Database().analyze_scraping(domain))
    menu = [list(element) for element in menu]

    # Remove tags from text fields.
    for i, element in enumerate(menu):
        menu[i][1] = strip_html_tags(element[1])

    # Remove elements with empty texts.
    menu = list(filter(lambda x: len(x[1]) > 0, menu))

    # Remove not frequent elements.
    highest_freq = menu[0][0]
    menu = list(filter(lambda x: x[0] > highest_freq * 0.10, menu))

    return menu


def go_to_section(url, name=None, number=None):
    """
    Given the name of one of the menu's entries, returns its URL.
    """
    # Get menu.
    menu = get_menu(url)
    menu_strings = [tup[0] for tup in menu]
    menu_anchors = [tup[1] for tup in menu]

    # Check if the parameter is the name of the section or the index.
    if name is not None:
        # Put all the strings to lowercase.
        menu_strings = [string.lower() for string in menu_strings]
        # Return index of string, if present. Otherwise, IndexError.
        index = menu_strings.index(name.lower())
    else:
        index = number - 1

    return menu_anchors[index]


def fix_url(url):
    if not re.match('(?:http|ftp|https)://', url):
        return 'http://{}'.format(url)
    return url


def get_main_container(url, text):
    """
    Given the html_code, returns the element containing the main content of the web page.
    It uses the SD algorithm to analyse the rendered HTML of the web page.
    :return: The HTML element containing the main content of the page.
    """
    '''# Check in the database if the page has already been parsed.
    html_element = Database().has_been_parsed(url)
    # If this is not the first time visiting the page, I just return the text I already have.
    if html_element:
        return BeautifulSoup(html_element, 'lxml')'''

    # First, I render the HTML code of the page.
    rendered_html = render_page(url)

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

    # Seventh, select the deepest element.
    html_element = candidates[0][0]

    # Finally, save it in the database.
    # Database().insert_page(url, html_element.prettify())
    return html_element


def render_page(url):
    """
    Returns the parsed HTML code of the web page reachable at the URL specified. It supports Javascript.
    :param url: URL of the web page to parse.
    :return: The parsed HTML code of the web page.
    """
    start = time()
    try:
        print("Rendering page with Selenium...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
    except Exception:
        print(f"Can't access this website: {url}")
        raise Exception("Error while visiting the page.")

    print(f"Selenium request elapsed time: {(time() - start):.2f} s")

    html = driver.find_element_by_tag_name('html').get_attribute('innerHTML')

    return html


def get_clean_text(url):
    """
    Utilizes Aylien APIs to extract the text from a web page.
    :param url: URL of the web page.
    :return: the text of the web page.
    """
    start = time()
    text = client.Extract({'url': url})
    print(f"Aylien API extract text elapsed time: {(time() - start):.2f}")
    return text.get("article")


def is_action_recent(timestamp, days):
    t1 = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    t2 = datetime.now()
    difference = t2 - t1

    return difference.days < days
