import threading

import requests
from bs4 import BeautifulSoup

from databases.handlers.page_links_handler import db_delete_all_domain_links
from databases.handlers.pages_handler import db_add_parsed_html_to_page, db_get_page, db_delete_page, db_insert_page, \
    db_add_topic_to_page, db_add_language_to_page
from databases.handlers.search_forms_handler import db_get_search_forms
from databases.handlers.text_links_handler import db_delete_text_links
from databases.handlers.websites_handler import db_delete_website, db_last_time_crawled
from functionality.main_text import extract_main_text
from functionality.search_forms import extract_search_forms
from helpers import helper
from helpers.api import get_topic, get_language
from helpers.browser import scrape_page
from helpers.helper import is_action_recent
from helpers.utility import get_time, get_domain, add_scheme
from scraping.crawler_handler import Crawler


def save_simple_html(url):
    """
    This method requests the HTML code of the web page and saves it in the db.
    For speed purposes, Javascript is not supported.
    """
    url = add_scheme(url)
    print(f"{get_time()} [{url}] SIMPLE HTML code started.")
    html = requests.get(url).text
    print(f"{get_time()} [{url}] SIMPLE HTML code finished.")
    db_insert_page(url, html)


def save_parsed_html(url):
    url = add_scheme(url)
    print(f"{get_time()} [{url}] PARSED HTML code started.")
    parsed_html = scrape_page(url)
    db_add_parsed_html_to_page(url=url, parsed_html=parsed_html)
    # Extract clean main text.
    extract_main_text(url)
    print(f"{get_time()} [{url}] PARSED HTML code finished.")


def analyze_page(url):
    # Check in the database if the web page has already been visited.
    get_new_page = False
    result = db_get_page(url=url)

    # Delete, if present, an obsolete version of the page.
    if result is not None and not helper.is_action_recent(timestamp=result[6], days=0, minutes=40):
        print("Page present, but obsolete.")
        db_delete_page(url=url)
        db_delete_text_links(url=url)
        get_new_page = True

    # If the page is not present in memory.
    if result is None:
        print("Page not present.")
        get_new_page = True

    if get_new_page:
        # Save the info in the DB.
        url = add_scheme(url)
        save_simple_html(url=url)
        db_add_topic_to_page(url, get_topic(url))
        db_add_language_to_page(url, get_language(url))

        # Put a placeholder, and parse the page in the background.
        db_add_parsed_html_to_page(url=url, parsed_html="In progress.")
        threading.Thread(target=save_parsed_html, args=(url, )).start()


def get_info(url):
    """
    This method gets information such as topic, summary and language from the web page.
    If the web page has not been visited recently, Aylien APIs are used to extract the information.
    If the web page has already been visited, the info is retrieved from the database.
    :return: A text response to be shown to the user containing info about the page.
    """
    page = db_get_page(url)
    try:
        title = BeautifulSoup(page[3], 'lxml').title.string
    except AttributeError:
        title = "unknown"
    text_response = (
        f"The title of this page is {title}.\n"
        f"The topic of this web page is {page[1]}. \n"
        f"The language of this web page is {page[2]}. \n"
    )

    # Extract all the search forms present in the page.
    extract_search_forms(url=url)
    search_forms = db_get_search_forms(page_url=url)
    search_forms_text = [x[6] for x in search_forms]
    if len(search_forms_text) > 0:
        text_response += f"There are search forms in this page called: "
        for text in search_forms_text:
            text_response += f"'{text}'; "

    return text_response


def analyze_domain(url):
    # Checks if domain has been already crawled.
    domain = get_domain(url=url)
    to_crawl = False
    last_crawling = db_last_time_crawled(domain)

    # Delete, if present, an obsolete crawling.
    if last_crawling is not None and not is_action_recent(timestamp=last_crawling, days=0, minutes=40):
        db_delete_all_domain_links(domain)
        db_delete_website(domain)
        to_crawl = True

    # If there is no crawling of the domain.
    if last_crawling is None:
        to_crawl = True

    complete_domain = get_domain(url, complete=True)
    # Crawl in the background.
    if to_crawl:
        threading.Thread(target=Crawler(start_url=domain).run, args=()).start()
        # If the URL contains a subdomain, crawl it too.
        if domain != complete_domain:
            threading.Thread(target=Crawler(start_url=complete_domain).run, args=()).start()

    # Check if the homepage of the domain has already been visited.
    page = db_get_page(add_scheme(complete_domain))
    if page[4] is None:
        # Get all the link
        threading.Thread(target=scrape_page, args=(url,)).start()
