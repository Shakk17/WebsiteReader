# importing the requests library
import time

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
                        "string": "open.online",
                        "string.original": "open.online"
                    }
                },
                {
                    "name": "projects/websitereader-srqsqy/agent/sessions/47056a3d-1977-7eb5-f876-fb7f002832bc/contexts/searchpage",
                    "lifespanCount": 2,
                    "parameters": {
                        "string": "open.online",
                        "string.original": "open.online"
                    }
                }
            ]
        }
    }


domains = ["open.online"]

for domain in domains:
    requests.post(url=API_ENDPOINT, json=get_data(domain))
    time.sleep(30)
