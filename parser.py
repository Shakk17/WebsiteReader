from bs4 import BeautifulSoup
import urllib3

http = urllib3.PoolManager()
url = 'https://old.reddit.com/'
response = http.request('GET', url)
soup = BeautifulSoup(response.data, 'html.parser')

print("Title: %s" % soup.title.string)
