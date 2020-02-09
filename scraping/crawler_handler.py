import os
import subprocess
from pathlib import Path

from databases.database_handler import Database


class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url

    def run(self):
        path = str(Path(os.getcwd()))
        shell_path = path + "/scraping/"
        command = f"scrapy crawl links -s url={self.start_url}"
        subprocess.call(command, cwd=shell_path, shell=True)

        db = Database()
        db.insert_website(url=self.start_url)

