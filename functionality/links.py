from databases.handlers.crawler_links_handler import db_get_crawler_links
from helpers.utility import extract_words


def read_links(url):
    links = db_get_crawler_links(url=url)
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


def read_links_article(url):
    links = db_get_crawler_links(url=url)
    texts = []
    new_links = []
    if len(links) > 0:
        # Keep only links with 4 words or more in text.
        links = list(filter(lambda x: len(extract_words(x[0])) > 3, links))
        # Keep only links not contained in lists.
        links = list(filter(lambda x: x[3] == 0, links))
        # Remove duplicates.
        new_links = []
        for link in links:
            if link[0] not in texts:
                new_links.append(link)
                texts.append(link[0])

    return new_links


def get_links_text_response(links, idx_start, num_choices):
    # Get the indexes of the options to be shown to the user
    if idx_start >= len(links):
        idx_start = 0
    idx_end = idx_start + num_choices

    # Get the options that will be shown to the user in the text response.
    strings = [tup[0] for tup in links[idx_start:idx_end]]

    # Format of display -> option n: text
    #                      option n+1: text
    text_response = "You can choose between: \n"
    for i, string in enumerate(strings, start=1):
        text_response += f"{idx_start + i}: {string}. \n"
    text_response += f"\n{min(idx_start + num_choices, len(links))} out of {len(links)} option(s) read."

    return text_response
