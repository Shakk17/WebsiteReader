from databases.handlers.page_links_handler import db_get_page_links
from helpers.helper import update_cursor_index, show_element
from helpers.utility import extract_words, remove_scheme


def read_links(url):
    url = remove_scheme(url)
    links = db_get_page_links(url=url)
    links = remove_duplicate_links(links)
    return links


def read_links_article(url):
    url = remove_scheme(url)
    links = db_get_page_links(url=url)
    if len(links) > 0:
        # Keep only links with 4 words or more in text.
        links = list(filter(lambda x: len(extract_words(x[0])) > 3, links))
        # Keep only links not contained in lists.
        links = list(filter(lambda x: x[3] == 0, links))
        # Remove duplicates.
        links = remove_duplicate_links(links)

    return links


def remove_duplicate_links(links):
    texts = []
    new_links = []
    if len(links) > 0:
        # Remove duplicates.
        new_links = []
        for link in links:
            if link[0] not in texts:
                new_links.append(link)
                texts.append(link[0])
    return new_links


def get_links_text_response(url, links_type, action, idx_start, num_choices):
    links = []
    if links_type == "all":
        links = read_links(url=url)
    elif links_type == "article":
        links = read_links_article(url=url)

    idx_start = update_cursor_index(action, old_idx=idx_start, step=num_choices, size=len(links))

    # Get the options that will be shown to the user in the text response.
    strings = [tup[0] for tup in links]

    if len(links) > 0:
        # Format of display -> option n: text
        #                      option n+1: text
        text_response = show_element(strings, idx_start, num_choices)
    else:
        text_response = "No links available at the moment."

    return text_response, idx_start
