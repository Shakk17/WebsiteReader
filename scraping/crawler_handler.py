import os
import subprocess
from pathlib import Path

from databases.database_handler import Database


class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url

    def run(self):
        # Insert url into the website database.
        Database().insert_website(url=self.start_url)
        print(f"Inserted {self.start_url} in websites database.")

        # Open a shell in the scrapy directory and start crawling in a new subprocess.
        path = str(Path(os.getcwd()))
        shell_path = path + "/scraping/"
        command = f"scrapy crawl links -s url={self.start_url}"
        print(f"Started scraping website {self.start_url}")
        subprocess.call(command, cwd=shell_path, shell=True)



