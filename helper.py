import tldextract
from googlesearch import search
from time import time
from databases.database_handler import Database


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
    domain = get_domain(url)
    menu = Database().analyze_scraping(domain)
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
