import os
import subprocess
from pathlib import Path

from databases.handlers.websites_handler import db_insert_website
from helpers.utility import add_scheme


class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url

    def run(self):
        # Insert domain into the website database.
        db_insert_website(domain=self.start_url)

        # Open a shell in the scrapy directory and start crawling in a new subprocess.
        path = str(Path(os.getcwd()))
        shell_path = path + "/scraping/"
        homepage_url = add_scheme(f"{self.start_url}")
        command = f"scrapy crawl links -s url={homepage_url}"
        subprocess.call(command, cwd=shell_path, shell=True)



