import os
import subprocess
from pathlib import Path

from databases.handlers.websites_handler import db_insert_website
from debug_spider.helpers.utility import get_domain


class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url

    def run(self):
        # Insert domain into the website database.
        domain = get_domain(self.start_url)
        db_insert_website(domain=domain)
        print(f"Inserted {domain} in websites database.")

        # Open a shell in the scrapy directory and start crawling in a new subprocess.
        path = str(Path(os.getcwd()))
        shell_path = path + "/scraping/"
        command = f"scrapy crawl links -s url={self.start_url}"
        print(f"Started scraping website {self.start_url}")
        subprocess.call(command, cwd=shell_path, shell=True)



