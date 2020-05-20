import threading

import requests
from bs4 import BeautifulSoup

from databases.handlers.page_links_handler import db_delete_all_domain_links
from databases.handlers.pages_handler import db_add_parsed_html_to_page, db_get_page, db_delete_page, db_insert_page, \
    db_add_topic_to_page, db_add_language_to_page
from databases.handlers.forms_handler import db_get_forms
from databases.handlers.text_links_handler import db_delete_text_links
from databases.handlers.websites_handler import db_delete_website, db_last_time_crawled
from functionality.functionality import extract_functionality
from functionality.main_text import extract_main_text
from functionality.forms import extract_forms
from helpers import helper
from helpers.api import get_topic, get_language
from helpers.browser import scrape_page
from helpers.exceptions import PageRequestError
from helpers.helper import is_action_recent
from helpers.utility import get_time, get_domain, add_scheme
from scraping.crawler_handler import Crawler


def get_simple_html(url):
    """
    This method requests the HTML code of the web page.
    For speed purposes, Javascript is not supported.
    """
    url = add_scheme(url)
    print(f"{get_time()} [{url}] SIMPLE HTML code started.")
    try:
        html = requests.get(url).text
    except Exception:
        raise PageRequestError
    print(f"{get_time()} [{url}] SIMPLE HTML code finished.")
    return html


def finish_page_analysis(url):
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
    if result is not None and not helper.is_action_recent(timestamp=result[6], days=1, minutes=40):
        db_delete_page(url=url)
        db_delete_text_links(url=url)
        get_new_page = True

    # If the page is not present in memory.
    if result is None:
        get_new_page = True

    if get_new_page:
        # Save the info in the DB.
        url = add_scheme(url)
        simple_html = get_simple_html(url=url)
        db_insert_page(url=url, simple_html=simple_html)
        db_add_topic_to_page(url=url, topic=get_topic(url))
        db_add_language_to_page(url=url, language=get_language(url))
        # Finish analyse (with rendering) the web page in the background.
        threading.Thread(target=finish_page_analysis, args=(url,)).start()


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
        f"You are now visiting the web page called {title}.\n"
        f"Its topic is {page[1]} and the language is {page[2]}. \n"
    )

    # Extract all the search forms present in the page.
    extract_forms(url=url)
    search_forms = db_get_forms(page_url=url)
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
    if last_crawling is not None and not is_action_recent(timestamp=last_crawling, days=1, minutes=40):
        db_delete_all_domain_links(domain)
        db_delete_website(domain)
        to_crawl = True

    # If there is no crawling of the domain.
    if last_crawling is None:
        to_crawl = True

    # Crawl in the background.
    if to_crawl:
        # threading.Thread(target=Crawler(start_url=domain).run, args=()).start()
        threading.Thread(target=start_crawling, args=(domain,)).start()

    # Analyze the homepage of the website.
    domain = domain + '/'
    analyze_page(domain)


def start_crawling(domain):
    Crawler(start_url=domain).run()
    # Extract functionality from the website.
    extract_functionality(domain)
