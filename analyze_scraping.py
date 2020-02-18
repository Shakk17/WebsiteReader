'''from databases.database_handler import Database

menu = Database().analyze_scraping("corriere")
for el in menu:
    print(el)
'''

from aylienapiclient import textapi
client = textapi.Client("b50e3216", "0ca0c7ad3a293fc011883422f24b8e73")
url = "https://en.wikipedia.org/wiki/Google_Stadia"
print(client.Extract({'url': url}))