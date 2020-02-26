from databases.database_handler import Database
from datumbox_wrapper import DatumBox
from helper import extract_search_forms
import requests

menu = Database().analyze_scraping("open")
for el in menu:
    print(el)