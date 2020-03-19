# importing the requests library
import time
from helpers.utility import get_time
import requests

# defining the api-endpoint 
API_ENDPOINT = "https://55614aef.ngrok.io/webhook"


def get_data(url):
    return {
        "queryResult": {
            "queryText": "visit open.online",
            "action": "SearchPage_reset",
            "parameters": {
                "string": url
            },
            "outputContexts": [
                {
                    "name": "projects/websitereader-srqsqy/agent/sessions/47056a3d-1977-7eb5-f876-fb7f002832bc/contexts/cursor",
                    "lifespanCount": 5,
                    "parameters": {
                        "string": url
                    }
                }
            ]
        }
    }


domains = [
    "reddit.com",
    "cnn.com",
    "nytimes.com"
    "news.google.com",
    "theguardian.com",
    "shutterstock.com",
    "washingtonpost.com",
    "news.yahoo.com",
    "forbes.com",
    "cnbc.com",
    "foxnews.com",
    "weather.com",
    "bloomberg.com"
    "wsj.com",
    "reuters.com",
    "usatoday.com",
    "nbcnews.com",
    "nypost.com",
    "accuweather.com",
    "chron.com",
    "dw.com",
    "drudgereport.com",
    "usnews.com",
    "livemint.com",
    "time.com"
]

for domain in domains:
    try:
        requests.post(url=API_ENDPOINT, json=get_data(domain))
        print(f"{get_time()} Requested: {domain}")
    except ConnectionError:
        print(f"{get_time()} Connection error: {domain}")
    time.sleep(100)
