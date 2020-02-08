from scrapy import cmdline
from databases.database_handler import Database

url = "https://www.polimi.it/"
command = "scrapy crawl urls -s url=" + url

cmdline.execute(command.split())
db = Database()
db.insert_website(url=url)
