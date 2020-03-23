import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from databases.handlers.pages_handler import db_update_page, db_get_page
from databases.handlers.text_links_handler import db_insert_text_link, db_get_text_links
from helpers.api import get_text_from_aylien_api


def extract_main_text(url):
    """
    This method uses an Aylien API to extract the main text (and its links) from a web page.
    After the extraction, text and links of the web page are saved in the database.
    """
    # Get the main text of the web page.
    text = get_text_from_aylien_api(url=url)

    # Given the extracted main text, get its main HTML container.
    container = get_main_container(url=url, text=text)

    # Retrieve all the links from the HTML element that contains the main text.
    # link = position, text, url
    links = get_links_positions_in_main_text(container=container, text=text, url=url)

    # Save the main text in the DB.
    db_update_page(url=url, clean_text=text)

    # Save the links in the DB.
    for i, link in enumerate(links, start=1):
        db_insert_text_link(page_url=url, link_num=i, link=link)


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


def get_links_positions_in_main_text(container, text, url):
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
        link_url = urljoin(url, text_link[1])

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


def get_main_text_sentences(url, idx_sentence, n_sentences):
    """
    This method returns a number of sentences from the main text of the web page.
    :param url: String containing the URL of the page.
    :param idx_sentence: The index of the first sentence to be retrieved.
    :param n_sentences: The number of sentences to be retrieved.
    :return: A string containing some sentences from the main text of the web page.
    """
    # Check if the text is actually present in the database.
    page = db_get_page(url=url)
    if page is None:
        raise FileNotFoundError

    # Get the text from the database.
    text = page[5]
    # Check that the web page has already been analyzed.
    if text is None:
        raise FileNotFoundError

    # Add the links indicators to the text to be returned.
    links_positions = db_get_text_links(page_url=url)
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
