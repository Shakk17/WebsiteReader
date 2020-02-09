import queue
import sqlite3
import threading
import time
import os
import subprocess
from pathlib import Path

from sqlite3 import Error

from colorama import Fore, Style

from databases.database_handler import Database
from url_parser import UrlParser

from scraping.crawler_handler import Crawler

TIMEOUT = 4


def save_action_in_db(action, url):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(r"./history.db")
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return


class Cursor:
    def __init__(self, url):
        self.url = url
        # Type of the page, it can be article or section.
        self.type = None
        # Number that indicates the paragraph to read in the current article.
        self.idx_paragraph = 0
        # Number that indicates the article to read in the current section.
        self.idx_article = 0
        # Link selected.
        self.link = None
        # Sentence read in current web page.
        self.sentence_number = 0

    def __repr__(self):
        return (
            f"{Fore.GREEN}"
            f"{Style.BRIGHT}+++ CURSOR +++{Style.NORMAL}\n"
            f"\tURL: {self.url}\n"
            f"\tPage type: {self.type}\n"
            f"\tIdx paragraph: {self.idx_paragraph}\n"
            f"\tIdx article: {self.idx_article}\n"
            f"\tLink: {self.link}\n"
            f"\tSentence number: {self.sentence_number}\n"
            f"{Style.RESET_ALL}")


class RequestHandler:
    def __init__(self):
        self.url_parser = None
        self.cursor = None
        # Queue set up to hold threads responses.
        self.q = queue.Queue()

    def get_response(self, request):
        """
        Starts two threads.
        One to process the incoming request, the other one is a timeout.
        Each thread, after its completion, puts the result in a queue.
        After the timeout, gets the first available element from the queue.
        """
        main_thread = threading.Thread(target=self.elaborate, args=(request,), daemon=True)
        # TODO: timeout handler
        # timeout_thread = threading.Thread(target=self.postpone_response, args=(request, TIMEOUT), daemon=True)
        main_thread.start()
        # timeout_thread.start()
        # Wait until the timeout expires.
        # timeout_thread.join()

        # Returns the first available result.
        result = self.q.get()

        print(self.cursor)

        return result

    def elaborate(self, request):
        """
        Parses the request and understands what to do.
        """
        # Get action from request.
        action = request.get('queryResult').get('action')
        print("-" * 20)
        print("Action: " + action)

        # Get open-online context from request, if available.
        contexts = request.get("queryResult").get("outputContexts")
        context = next((x for x in contexts if "web-page" in x.get("name")), None)

        # Get context parameters from request, if available.
        try:
            # URL is either in parameters or in context.
            url = request.get("queryResult").get("parameters").get("url")
            if url is None:
                raise AttributeError
        except AttributeError:
            url = context.get("parameters").get("web_page").get("url")

        # Create an object containing details about the web page.
        self.cursor = Cursor(url=url)

        try:
            self.cursor.type = context.get("parameters").get("web_page").get("type")
            self.cursor.idx_paragraph = int(context.get("parameters").get("web_page").get("idx_paragraph"))
            self.cursor.idx_article = int(context.get("parameters").get("web_page").get("idx_article"))
            self.cursor.link = context.get("parameters").get("web_page").get("link")
            self.cursor.sentence_number = int(context.get("parameters").get("web_page").get("sentence_number"))
        except AttributeError:
            self.cursor.type = "article"
            self.cursor.idx_paragraph = 0
            self.cursor.idx_article = 0
            self.cursor.link = url
            self.cursor.sentence_number = 0

        # Save action requested into the history database.
        history_db = Database()
        history_db.insert_action(action, url)

        if action == "VisitPage":
            return self.visit_page()
        elif action == 'GetInfo':
            return self.get_info()
        elif action == 'GetMenu':
            return self.get_menu()
        elif action == 'ReadPage':
            return self.read_page()
        elif action == "OpenLink":
            return self.open_link()
        elif action == "GoToSection":
            return self.go_to_section(context.get("parameters").get("section-name"))
        elif action == "Analyze":
            return self.analyze()

    def visit_page(self):
        """
        This method:
        - parses the page, extracting info about it;
        - if there are no errors, updates the cursor to the new page just visited;
        - checks if the domain has been already crawled. If not, it starts a new crawl.
        Returns a response.
        """
        self.cursor = Cursor(self.cursor.url)
        self.url_parser = UrlParser(url=self.cursor.url)
        try:
            # Page parsing.
            text_response = "%s visited successfully!" % self.url_parser.url
            text_response += self.url_parser.get_info()
            # Cursor update.
            self.cursor = Cursor(self.url_parser.url)
        except Exception as ex:
            text_response = ex.args[0]

        # Checks if domain has been already crawled.
        if not Database().has_been_crawled(self.url_parser.url):
            # Start crawling in the background.
            crawler = Crawler(start_url=self.url_parser.url)
            thread = threading.Thread(target=crawler.run, args=())
            thread.start()

        # Update url in context.
        return self.build_response(text_response)

    def get_menu(self):
        """
        Returns the links reachable from the menu.
        """
        self.url_parser = UrlParser(url=self.cursor.url)
        menu = self.url_parser.get_menu()
        strings = [tup[0] for tup in menu]
        text_response = '-'.join(strings)
        # TODO get elements of menu, how many?
        return self.build_response(text_response)

    def get_info(self):
        """
        Returns info about the web page.
        """
        self.url_parser = UrlParser(url=self.cursor.url)
        text_response = self.url_parser.get_info()
        return self.build_response(text_response)

    def read_page(self):
        """
        If page is article, read it. Otherwise, read main article titles available.
        """
        self.url_parser = UrlParser(url=self.cursor.url)
        if self.url_parser.is_article():
            try:
                text_response = self.url_parser.get_article(self.cursor.idx_paragraph)
                self.cursor.idx_paragraph += 1
            except IndexError as err:
                text_response = "End of article."
                self.cursor.idx_paragraph = 0
        else:
            try:
                article = self.url_parser.get_section(self.cursor.idx_article)
                text_response = article[0]
                self.cursor.link = article[1]
                self.cursor.idx_article += 1
            except IndexError as err:
                text_response = "End of section."
                self.cursor.idx_article = 0
        return self.build_response(text_response)

    def open_link(self):
        """
        Visits the web page linked in the cursor, then sets the cursor on that page.
        """
        self.cursor.url, self.cursor.link = self.cursor.link, None
        return self.visit_page()

    def go_to_section(self, name):
        """
        Opens the section of the menu, if present.
        """
        self.url_parser = UrlParser(url=self.cursor.url)
        try:
            new_url = self.url_parser.go_to_section(name)
            self.url_parser = UrlParser(new_url)
            return self.visit_page()
        except ValueError:
            return "Wrong input."

    def analyze(self):
        """
        Analyze web page through SD algorithm.
        """
        self.url_parser = UrlParser(url=self.cursor.url)
        result = self.url_parser.analysis

        # Take text result, split it into sentences. Return only first two sentence pointed by the cursor.
        number_of_sentences = 3
        sentences = result.split('.')[self.cursor.sentence_number:self.cursor.sentence_number + number_of_sentences]
        sentence = ".".join(sentences)
        text_response = f"Title: {self.url_parser.soup.title.string}\n"
        try:
            text_response += f"Text: {sentence}."
            print(text_response)
            self.cursor.sentence_number += number_of_sentences
        except IndexError:
            text_response += "You have reached the end of the web page."
            self.cursor.sentence_number = 0

        return self.build_response(text_response)

    def build_response(self, text_response):
        """
        Put the successful response in the queue.
        """
        self.q.put(
            {
                "fulfillmentText": text_response,
                "outputContexts": [{
                    "name": "projects/<Project ID>/agent/sessions/<Session ID>/contexts/web-page",
                    "lifespanCount": 1,
                    "parameters": {
                        "web_page": vars(self.cursor)
                    }
                }]
            })

    def postpone_response(self, request, seconds):
        """
        Puts a request for more time in the queue.
        """
        # Get action from request.
        action = request.get('queryResult').get('action')

        # Start timer.
        time.sleep(seconds)
        # After 4 seconds, checks if the main thread has terminated.
        if self.q.empty():
            # Send a response to server to ask for 5 more seconds to answer. Valid only two times.
            print("Sent request for more time.")
            self.q.put(
                {
                    "followupEventInput": {
                        "name": "timeout-" + action,
                        "parameters": vars(self.cursor),
                        "languageCode": "en-US"
                    }
                })
