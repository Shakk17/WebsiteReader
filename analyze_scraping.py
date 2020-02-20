'''from databases.database_handler import Database

menu = Database().analyze_scraping("corriere")
for el in menu:
    print(el)
'''

from aylienapiclient import textapi
client = textapi.Client("b50e3216", "0ca0c7ad3a293fc011883422f24b8e73")
url = "https://www.open.online/2020/02/20/chi-e-tobias-il-killer-tedesco-che-ha-pubblicato-le-sue-tesi-razziste-su-internet-germania-hanau/"

combined = client.Combined({
        'url': url,
        'endpoint': ["classify", "language", "summarize"]
    })
print()
