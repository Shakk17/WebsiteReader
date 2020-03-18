import re
import urllib.parse
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from databases.database_handler import Database
from databases.pages_handler import db_get_page
from helpers.utility import strip_html_tags, get_domain, extract_words


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

    # Remove elements with more than 3 words.
    menu = list(filter(lambda x: len(extract_words(x[1])) < 4, menu))

    # Remove elements of the menu that are not frequent.
    highest_freq = menu[0][0]
    threshold = 0.00
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


def get_main_container(url, text):
    """
    This method takes a web page and its main text, and returns the deepest element (in the DOM tree) containing it.
    :param url: A string containing the URL of the web page.
    :param text: A string containing the main text of the web page.
    :return: The HTML code of the deepest element containing the main text.
    """

    # First, get the parsed HTML code from the database.
    page = db_get_page(url=url)
    rendered_html = page[4]

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
    try:
        html_element = candidates[0][0]
    except IndexError:
        # If error, returns the whole page.
        html_element = all_elements[0]

    return html_element


def is_action_recent(timestamp, days=0, minutes=0):
    """
    This method compares a timestamp to the actual date.
    :param timestamp: A string in the format "%Y-%m-%d %H:%M:%S".
    :param days: An integer indicating the number of days defining when an action is recent.
    :param minutes: An integer indicating the number of minutes defining when an action is recent.
    :return: True is the timestamp inserted is a date that happened recently, False otherwise.
    """
    t1 = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    t2 = datetime.now()

    difference = t2 - t1

    recent = difference < timedelta(days=days, minutes=minutes)
    return recent


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


def update_cursor_index(action, old_idx, step, size):
    """
    This method takes an index as an input, and returns an updated index which value depends on the other parameters.
    :param action: "reset", "next" or "previous".
    :param old_idx: An integer representing the old index to modify.
    :param step: An integer representing the variation of the index.
    :param size: An integer representing the size of the element related to the index.
    :return: An integer representing the new index.
    """
    new_idx = old_idx
    if action == "reset":
        new_idx = 0
    elif action == "next":
        new_idx = new_idx + step if (old_idx + step) < size else 0
    elif action == "previous":
        new_idx = new_idx - step if (old_idx - step) > 0 else 0
    return new_idx
