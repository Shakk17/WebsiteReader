import os
import subprocess
from pathlib import Path

from databases.database_handler import Database
from helpers.utility import add_schema, get_domain


class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url

    def run(self):
        # Insert domain into the website database.
        Database().insert_website(domain=self.start_url)

        # Open a shell in the scrapy directory and start crawling in a new subprocess.
        path = str(Path(os.getcwd()))
        shell_path = path + "/scraping/"
        homepage_url = add_schema(f"{self.start_url}")
        command = f"scrapy crawl links -s url={homepage_url}"
        subprocess.call(command, cwd=shell_path, shell=True)



