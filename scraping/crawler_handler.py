import os
import pathlib
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

        dir_path = pathlib.Path(__file__).parent.absolute()
        # Change working directory to the folder of this file.
        os.chdir(dir_path)
        # Open a shell in the scrapy directory and start crawling in a new subprocess.
        path = str(Path(os.getcwd()))
        homepage_url = add_scheme(f"{self.start_url}")
        command = f"scrapy crawl links -s url={homepage_url}"
        subprocess.call(command, cwd=path, shell=True)



