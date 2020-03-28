from aylienapiclient import textapi
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

from datumbox_wrapper import get_language_string
from helpers.browser import get_quick_html
from helpers.printer import yellow
from helpers.utility import get_time, add_scheme

from urllib.parse import quote

aylien_client = textapi.Client("b50e3216", "0ca0c7ad3a293fc011883422f24b8e73")


def get_urls_from_google(query):
    """
    This method makes a search on Google and returns the first 5 results.
    :param query: A string containing the query to input into Google Search.
    :return: A list containing tuples (title, URL, snippet) of the first 5 results.
    """
    print(yellow(f"{get_time()} [GOOGLE API] Search started."))

    # Perform Google Search.
    api_key = "AIzaSyBxmCvHuuBmno25vybpLHEmVL1sOZusYa0"
    cse_id = "001618926378962890992:ri89cvvqaiw"
    query_service = build(serviceName="customsearch", version="v1", developerKey=api_key)
    query_results = query_service.cse().list(q=query, cx=cse_id).execute().get("items")

    # Get results.
    results = [(result.get("title"), result.get("link"), result.get("snippet")) for result in query_results]

    print(yellow(f"{get_time()} [GOOGLE API] Search finished."))
    return results


def get_language(url):
    """
    This method returns info regarding a certain web page by using Aylien APIs.
    :param url: A string containing the URL of the web page.
    :return: A tuple (topic, language) containing info about the web page.
    """
    print(yellow(f"{get_time()} [AYLIEN API] Language extraction started."))

    try:
        # This is a combined call to the Aylien APIs.
        language = aylien_client.Language({'url': url})
    except TimeoutError:
        return "unknown"

    language_code = language.get("lang")
    language = get_language_string(language_code)

    print(yellow(f"{get_time()} [AYLIEN API] Language extraction finished."))
    return language


def get_text_from_aylien_api(url):
    """
    This method utilizes an Aylien API to extract the main text from a web page.
    :param url: A string containing the URL of the web page.
    :return: A string containing the main text of the web page.
    """
    print(yellow(f"{get_time()} [AYLIEN API] Main text extraction started."))
    try:
        text = aylien_client.Extract({'url': url})
        print(yellow(f"{get_time()} [AYLIEN API] Main text extraction finished."))
        text = text.get("article")
    except Exception:
        text = "Error during API call."
    return text


def get_topic(url):
    new_url = quote(url)
    fortiguard_url = f"https://fortiguard.com/webfilter?q={new_url}"
    html = get_quick_html(url=fortiguard_url)
    string = BeautifulSoup(html, "lxml").findAll("h4", {"class": "info_title"})[0].text
    topic = string.split(": ")[1]
    return topic
