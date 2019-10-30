from bs4 import BeautifulSoup
import urllib3


def build_response(response):

    return {
        'fulfillmentText': response,
    }


class HtmlParser:
    def __init__(self):
        self.http = urllib3.PoolManager()
        self.soup = None

    def get_response(self, request):
        action = request.get('queryResult').get('action')
        print("Action: " + action)

        url = request.get('queryResult').get('parameters').get('url')
        return build_response(self.get_title(url))

    def get_title(self, url):
        response = self.http.request('GET', url)
        self.soup = BeautifulSoup(response.data, 'html.parser')
        title = self.soup.title.string
        return title


parser = HtmlParser()
print(parser.get_title('https://old.reddit.com/'))
