from databases.handlers.page_links_handler import db_get_page_links, get_links_in_list
from helpers.utility import get_domain, strip_html_tags


def get_menu(url):
    """
    This method returns all the links belonging to the navigation menu of a web page.
    :param url: A string containing the URL of the web page.
    :return: An array of tuples (number, link_text, link_url, avg_x, avg_y) ordered by number DESC.
    """
    # Get menu of the domain that contains the web page.
    domain = get_domain(url)
    # Get all domain links contained in lists.
    # link = (times, link_text, link_url, page_url, in_nav)
    domain_links = get_links_in_list(domain)
    domain_links = [list(link) for link in domain_links]
    # homepage_link = (link_text, link_url)
    homepage_links = db_get_page_links(domain)
    homepage_links_urls = [link[1] for link in homepage_links]

    # Remove all the tags from the text fields of the links.
    for i, link in enumerate(domain_links):
        domain_links[i][1] = strip_html_tags(link[1])

    # Remove elements of the menu with empty texts.
    domain_links = list(filter(lambda link: len(link[1]) > 0, domain_links))

    # Apply bonus and malus to each link score.
    for link in domain_links:
        # If text is too long, penalize.
        if len(link[1]) > 20:
            link[0] /= 10
        # If link is also present in homepage, bonus.
        if link[2] in homepage_links_urls:
            link[0] *= 100
        # If link is contained in <nav> element, bonus.
        if link[4] == 1:
            link[0] *= 5

    menu = sorted(domain_links, key=lambda link: link[0], reverse=True)

    # Remove elements of the menu that are not frequent.
    if len(menu) > 0:
        highest_freq = menu[0][0]
        threshold = 0.00
        menu = list(filter(lambda x: x[0] > highest_freq * threshold, menu))

    # Cap the amount of results to 30
    menu = menu[:30]

    return menu
