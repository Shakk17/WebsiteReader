from databases.database_handler import Database

menu = Database().analyze_scraping("corriere")
for el in menu:
    print(el)
