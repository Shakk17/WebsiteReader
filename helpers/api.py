from time import time

from aylienapiclient import textapi
from googleapiclient.discovery import build

aylien_client = textapi.Client("b50e3216", "0ca0c7ad3a293fc011883422f24b8e73")


def get_urls_from_google(query):
    """
    This method makes a search on Google and returns the first 5 results.
    :param query: A string containing the query to input into Google Search.
    :return: A list containing tuples (title, URL, snippet) of the first 5 results.
    """
    start = time()
    # Perform Google Search.
    api_key = "AIzaSyBxmCvHuuBmno25vybpLHEmVL1sOZusYa0"
    cse_id = "001618926378962890992:ri89cvvqaiw"
    query_service = build(serviceName="customsearch", version="v1", developerKey=api_key)
    query_results = query_service.cse().list(q=query, cx=cse_id).execute().get("items")
    # Get results.
    results = [(result.get("title"), result.get("link"), result.get("snippet")) for result in query_results]
    print(f"[GOOGLE API] Search elapsed time: {(time() - start):.2f}")
    return results


def get_info_from_aylien_api(url):
    """
    This method returns info regarding a certain web page by using Aylien APIs.
    :param url: A string containing the URL of the web page.
    :return: A tuple (topic, language) containing info about the web page.
    """
    start = time()
    # This is a combined call to the Aylien APIs.
    combined = aylien_client.Combined({
        'url': url,
        'endpoint': ["classify", "language"]
    })

    language = combined.get("results")[0].get("result").get("lang")

    # The topic is returned only if it the level of confidence is over a certain threshold.
    try:
        topic_confidence = combined.get("results")[1].get("result").get("categories")[0].get("confidence")
        if topic_confidence > 0.3:
            topic = combined.get("results")[1].get("result").get("categories")[0].get("label")
        else:
            topic = "unknown"
    except IndexError:
        topic = "unknown"
    print(f"[AYLIEN API] Extract info elapsed time: {(time() - start):.2f}")
    return topic, language


def get_text_from_aylien_api(url):
    """
    This method utilizes an Aylien API to extract the main text from a web page.
    :param url: A string containing the URL of the web page.
    :return: A string containing the main text of the web page.
    """
    start = time()
    text = aylien_client.Extract({'url': url})
    print(f"[AYLIEN API] Extract text elapsed time: {(time() - start):.2f}")
    return text.get("article")
