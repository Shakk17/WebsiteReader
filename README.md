In order to run the server locally, the following actions need to be taken:
1) download ngrok from https://ngrok.com/download
2) run ngrok
3) execute the command "ngrok http 5000" in the ngrok prompt
4) copy the URL from the row starting with "Forwarding" (it should be something like https://263b9e40.ngrok.io)
5) open Dialogflow (dialogflow.com)
6) open the section Fulfillment and paste the URL into the URL field before /webhook (https://263b9e40.ngrok.io/webhook)
7) open the IDE of choice, e.g., PyCharm
8) run the server.py file
# WebsiteReader Engine
![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)

Website reader is voice-based conversational browser for navigating web pages. The current repository contains the engine for automating incoming browsing actions.


## Instalation
You can install the dependencies using `pipenv install`.

WesiteReader relies on the following third-party services
- FortiGuard Labs API, for topic identification [[Learn more](http://fortiguard.com/learnmore#wf)]
- Aylien Text API, for text summarisation and language detection  [[Learn more](https://aylien.com/text-api/)]
- Google Custom Search API, for searching websites [[Learn more](https://developers.google.com/custom-search/v1/overview)] 

## Running
The code can be run by simply typing:
`$ python server.py`

Or alternatively with heroku cli using the following command:
`$ heroku local --port 5000`



Endpoint

`$ localhost:5000/webhook`

## Supported actions


- GoogleSearch
- Bookmarks
- VisitPage
- Homepage
- BasicInformation
- Menu
- MainText
- Links_all
- Links_article
- Form
- Functionality


## License 
WebsiteReader is Apache 2.0 - licensed.
