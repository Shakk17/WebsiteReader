#WebsiteReader Engine
![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)

Website reader is voice-based conversational browser for navigating web pages. The current repository contains the engine for automating incoming browsing actions.


##Instalation
You can install the dependencies using `pipenv install`.

WesiteReader relies on the following third-party services
- FortiGuard Labs API, for topic identification [[Learn more](http://fortiguard.com/learnmore#wf)]
- Aylien Text API, for text summarisation and language detection  [[Learn more](https://aylien.com/text-api/)]
- Google Custom Search API, for searching websites [[Learn more](https://developers.google.com/custom-search/v1/overview)] 

##Running

`$ heroku local --port 5000`

`$ python server.py`

Endpoint

`$ localhost:5000/webhook`

##Supported actions


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


##License 
WebsiteReader is Apache 2.0 - licensed.
