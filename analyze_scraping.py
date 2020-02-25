from databases.database_handler import Database
from helper import fix_url
import requests

'''menu = Database().analyze_scraping("florian")
for el in menu:
    print(el)
'''

url = fix_url("facebook")
requests.get(url)