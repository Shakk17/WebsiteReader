from databases.database_handler import Database

menu = Database().analyze_scraping("open.online")
for el in menu:
    print(el)
