from databases.crawler_links_handler import db_get_crawler_links
from helpers.utility import extract_words


def read_links_article(url):
    links = db_get_crawler_links(url=url)
    texts = []
    new_links = []
    if len(links) > 0:
        # Keep only links with 4 words or more in text.
        links = list(filter(lambda x: len(extract_words(x[0])) > 3, links))
        # Keep only links not contained in lists.
        links = list(filter(lambda x: x[3] == 0, links))
        # Order link depending on their y_position.
        links.sort(key=lambda x: x[2])
        # Remove duplicates.
        new_links = []
        for link in links:
            if link[0] not in texts:
                new_links.append(link)
                texts.append(link[0])

    return new_links
