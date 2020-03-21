from databases.database_handler import analyze_scraping
from helpers.utility import get_domain, strip_html_tags, extract_words


def get_menu(url):
    """
    This method returns all the links belonging to the menu of a web page.
    :param url: A string containing the URL of the web page.
    :return: An array of tuples (number, link_text, link_url, avg_x, avg_y) ordered by number DESC.
    """
    # Get menu of the domain that contains the web page.
    domain = get_domain(url)
    menu = analyze_scraping(domain)
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


def get_menu_text_response(menu, idx_start, num_choices):
    # Get the indexes of the options to be shown to the user
    if idx_start >= len(menu):
        idx_start = 0
    idx_end = idx_start + 10

    # Get the options that will be shown to the user in the text response.
    strings = [tup[1] for tup in menu[idx_start:idx_end]]

    # Format of display -> option n: text
    #                      option n+1: text
    text_response = "You can choose between: \n"
    for i, string in enumerate(strings, start=1):
        text_response += f"{idx_start + i}: {string}. \n"
    text_response += f"\n{min(idx_start + num_choices, len(menu))} out of {len(menu)} option(s) read."

    return text_response
