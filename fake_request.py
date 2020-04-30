# importing the requests library
import time
from helpers.utility import get_time
import requests

# defining the api-endpoint 
API_ENDPOINT = "https://eb03521d.ngrok.io/webhook"


def get_data(url):
    return {
        "queryResult": {
            "queryText": "visit open.online",
            "action": "VisitPage",
            "parameters": {
                "string": url
            },
            "outputContexts": [
                {
                    "name": "projects/websitereader-srqsqy/agent/sessions/47056a3d-1977-7eb5-f876-fb7f002832bc/contexts/navigation",
                    "lifespanCount": 5,
                    "parameters": {
                        "url": url
                    }
                }
            ]
        }
    }


domains = [
    "usatoday.com",
]

for domain in domains:
    try:
        requests.post(url=API_ENDPOINT, json=get_data(domain))
        print(f"{get_time()} Requested: {domain}")
    except ConnectionError:
        print(f"{get_time()} Connection error: {domain}")
    time.sleep(120)
