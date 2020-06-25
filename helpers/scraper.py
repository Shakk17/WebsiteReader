from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException

from helpers.utility import add_scheme, strip_html_tags, get_domain
from scraping.spider.items import PageLinkItem


def scrape_links(html, url):
    # Extract all links from the page.
    links = BeautifulSoup(html, "lxml").find_all("a")
    links = list(filter(lambda x: x.get("href") is not None, links))

    page_links_items = []
    for i, link in enumerate(links):
        try:
            href = add_scheme(urljoin(url, link.get("href")))
            text = strip_html_tags(link.text)
            # True if the element is contained in a list container.
            try:
                in_list = "li" in [parent.name for parent in links[i].parents]
            except IndexError:
                in_list = False

            # True if the element is contained in a nav container.
            try:
                in_nav = "nav" in [parent.name for parent in links[i].parents]
            except IndexError:
                in_nav = False

            # Skip PDF files.
            if href[-3:] in ["pdf", "jpg", "png"]:
                continue

            # If the link links to the same page, discard it.
            hash_position = href.find("/#")
            if href[:hash_position] == add_scheme(url):
                continue

            # Link is okay, send it to pipeline.
            page_link_item = PageLinkItem()
            page_link_item["link_url"] = href
            page_link_item["link_text"] = text
            page_link_item["page_url"] = url
            page_link_item["in_list"] = in_list
            page_link_item["in_nav"] = in_nav

            # We save the link in the DB only if it belongs to the domain.
            if get_domain(url) in href:
                page_links_items.append(page_link_item)
        except StaleElementReferenceException:
            continue

    return page_links_items
