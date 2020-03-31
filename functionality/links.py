from databases.handlers.page_links_handler import db_get_page_links, db_get_domain_links
from helpers.utility import extract_words, remove_scheme, get_domain


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


def read_links_best(url):
    url = remove_scheme(url)
    links = db_get_domain_links(domain=get_domain(url))
    if len(links) > 0:
        links = assign_score(links, url)
        # Sort links depending on score.
        links.sort(key=lambda x: x[2], reverse=True)
        links = remove_duplicate_links(links)
        print()

    return links


def assign_score(links, url):
    links_score = []
    homepage_url = get_domain(url, complete=True)
    homepage_links = db_get_page_links(homepage_url)
    # link = (link_text, link_url, y_position, in_list)
    for link in links:
        score = 1
        # TODO: assign score to each link.
        # Assign 1 point if the link is in the homepage, 2 points if positioned on top.
        homepage_links_urls = [link[1] for link in homepage_links]
        try:
            idx = homepage_links_urls.index(link[1])
            score += 1
            if int(homepage_links_urls[idx][2]) < 2000:
                score += 5
        except ValueError:
            pass
        # Assign 1 point if link has text, 2 points if it starts with a capital letter.
        if len(link[0]) > 0:
            score += 1
            if link[0][0].isupper():
                score += 1
        # Assign 50 points if the text contains log or sign.
        if "log" in link[0].lower() or "sign" in link[0].lower():
            score += 50

        links_score.append([link[0], link[1], score])
    # Order links according to score.
    links_score.sort(key=lambda x: x[2], reverse=True)
    # Put together all the links with the same URLs, summing their scores.
    new_links = []
    for link in links_score:
        # Check if the new URL is between the URLs already analyzed.
        urls = [new_link[1] for new_link in new_links]
        try:
            idx = urls.index(link[1])
            new_links[idx][2] += link[2]
        except ValueError:
            new_links.append(link)
    links_score = new_links

    return links_score


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
