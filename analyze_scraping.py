from databases.database_handler import Database
from datumbox_wrapper import DatumBox
from helper import fix_url
import requests

menu = Database().analyze_scraping("florian")
for el in menu:
    print(el)
