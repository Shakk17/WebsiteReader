from databases.handlers.functionality_handler import db_insert_functionality_link, db_get_functionality
from databases.handlers.page_links_handler import db_get_domain_links, db_get_page_links
from functionality.links import remove_duplicate_links
from helpers.utility import get_domain


def extract_functionality(domain):
    best_links = read_links_best(domain)
    # link = (link_text, link_url, score)
    for link in best_links:
        db_insert_functionality_link(page_url=domain, name=link[0], link_url=link[1], score=link[2])


def read_links_best(domain):
    links = db_get_domain_links(domain=domain)
    if len(links) > 0:
        links = assign_score(links, domain)
        # Sort links depending on score.
        links.sort(key=lambda x: x[2], reverse=True)
        links = remove_duplicate_links(links)

    return links


def assign_score(links, url):
    links_score = []
    homepage_url = get_domain(url)
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
            # TODO: index error: string index out of range:
            '''# if int(homepage_links_urls[idx][2]) < 2000:
               # score += 5'''
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


def get_functionality(url):
    domain = get_domain(url)
    links = db_get_functionality(page_url=domain)
    return links
