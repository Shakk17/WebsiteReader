import os
import subprocess
from pathlib import Path

from databases.database_handler import Database
from helpers.helper import get_domain, add_schema


class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url

    def run(self):
        # Insert domain into the website database.
        domain = get_domain(self.start_url)
        Database().insert_website(domain=domain)
        print(f"Inserted {domain} in websites database.")

        # Open a shell in the scrapy directory and start crawling in a new subprocess.
        path = str(Path(os.getcwd()))
        shell_path = path + "/scraping/"
        homepage_url = add_schema(f"www.{domain}")
        command = f"scrapy crawl links -s url={homepage_url}"
        print(f"Started scraping domain {homepage_url}")
        subprocess.call(command, cwd=shell_path, shell=True)



