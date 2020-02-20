import queue
import threading
import time

from colorama import Fore, Style

from databases.database_handler import Database
from scraping.crawler_handler import Crawler
from page_visitor import PageVisitor
from helper import get_menu, get_menu_link, get_domain, get_url_from_google, fix_url, is_action_recent

TIMEOUT = 4


class Cursor:
    def __init__(self, cursor_context, url):
        # Number that indicates the paragraph to read in the current article.
        self.idx_paragraph = 0
        # Number that indicates the article to read in the current section.
        self.idx_menu = 0
        # Link selected.
        self.link = None
        # Sentence read in current web page.
        self.sentence_number = 0

        # Updates cursor with values received from the context.
        for key, value in cursor_context.get("parameters").items():
            if not key.endswith("original"):
                setattr(self, key, value)
        self.url = url

    def __repr__(self):
        return (
            f"{Fore.GREEN}"
            f"{Style.BRIGHT}+++ CURSOR +++{Style.NORMAL}\n"
            f"\tURL: {self.url}\n"
            f"\tIdx paragraph: {self.idx_paragraph}\n"
            f"\tIdx menu: {self.idx_menu}\n"
            f"\tLink: {self.link}\n"
            f"\tSentence number: {self.sentence_number}\n"
            f"{Style.RESET_ALL}")


class RequestHandler:
    page_visitor = None
    cursor = None

    def __init__(self):
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
        timeout_thread = threading.Thread(target=self.postpone_response, args=(request, TIMEOUT), daemon=True)

        # If you receive a timeout request, just wait for the previous one to finish, no need to start another one.
        if not request.get('queryResult').get('queryText').startswith("timeout-"):
            self.q = queue.Queue()
            main_thread.start()
        timeout_thread.start()

        # Wait until the timeout expires.
        timeout_thread.join()

        # Returns the first available result.
        result = self.q.get()

        if result.get("fulfillmentText") is not None:
            print(self.cursor)

        return result

    def elaborate(self, request):
        """
        Parses the request and understands what to do.
        """

        # Get action from request.
        action = request.get('queryResult').get('action')
        print("-" * 20)

        # Get main context from request, if available.
        contexts = request.get("queryResult").get("outputContexts")
        cursor_context = next((x for x in contexts if "cursor" in x.get("name")), None)

        # URL is either in parameters (VisitPage) or in context.
        try:
            url = request.get("queryResult").get("parameters").get("url")
            if url is None:
                raise AttributeError
        except AttributeError:
            url = cursor_context.get("parameters").get("url")

        # Recognize if URL is not well-formed.
        url = fix_url(url)

        # Get first result from Google Search (in case the parameter is not a URL).
        query = request.get("queryResult").get("parameters").get("query")
        if query != '' and query is not None:
            url = get_url_from_google(query)

        # If the action is GoBack, get the previous action from the database and execute it.
        if action == "GoBack":
            action, url = Database().get_previous_action("shakk")

        # Create a Cursor object containing details about the web page.
        self.cursor = Cursor(cursor_context, url)

        # Save action requested into the history table of the database.
        Database().insert_action(action, url)
        print(f"Action {action} saved in history.")

        if action == "VisitPage":
            return self.visit_page()
        elif action == 'GetInfo':
            return self.get_info()
        elif action == 'GetMenu':
            return self.get_menu()
        elif action == 'ReadPage':
            return self.read_page()
        elif action == "OpenPageLink":
            return self.open_page_link(cursor_context.get("parameters"))
        elif action == "OpenMenuLink":
            return self.open_menu_link(cursor_context.get("parameters"))

    def visit_page(self):
        """
        This method:
        - parses the page, extracting info about it;
        - if there are no errors, updates the cursor to the new page just visited;
        - checks if the domain has been already crawled. If not, it starts a new crawl.
        Returns a response.
        """
        # Page parsing.
        self.page_visitor = PageVisitor(url=self.cursor.url)
        self.cursor.idx_paragraph = 0
        self.cursor.idx_menu = 0

        # Get info about the web page.
        text_response = self.page_visitor.get_info()
        # Cursor update.
        self.cursor.url = self.page_visitor.url

        # Checks if domain has been already crawled.
        domain = get_domain(url=self.page_visitor.url)
        to_crawl = False
        last_time_crawled = Database().last_time_crawled(domain=domain)

        if last_time_crawled is None:
            print(f"The domain {domain} has never been crawled before.")
            to_crawl = True

        # Check if the last crawling is recent.
        elif not is_action_recent(timestamp=last_time_crawled, days=7):
            print(f"The domain {domain} was last crawled too many days ago.")
            # Remove previous crawling results.
            Database().remove_old_website(domain)
            to_crawl = True

        # If necessary, start crawling in the background.
        if to_crawl:
            crawler = Crawler(start_url=self.page_visitor.url)
            thread = threading.Thread(target=crawler.run, args=())
            thread.start()

        # Update url in context.
        return self.build_response(text_response)

    def get_menu(self):
        num_choices = 10
        # Get the first 10 strings of the menu starting from idx_menu.
        menu = get_menu(self.cursor.url)

        idx_start = int(self.cursor.idx_menu)
        if idx_start >= len(menu):
            idx_start = 0
        idx_end = idx_start + 10
        strings = [tup[1] for tup in menu[idx_start:idx_end]]

        text_response = "You can choose between: \n"
        for i, string in enumerate(strings, start=1):
            text_response += f"{idx_start + i}: {string}. \n"
        text_response += f"\n{min(idx_start + num_choices, len(menu))} out of {len(menu)} option(s) read."

        self.cursor.idx_menu = idx_start + num_choices

        return self.build_response(text_response)

    def get_info(self):
        self.page_visitor = PageVisitor(url=self.cursor.url, quick_download=False)
        text_response = self.page_visitor.get_info()
        return self.build_response(text_response)

    def read_page(self):
        self.page_visitor = PageVisitor(url=self.cursor.url, quick_download=False)
        try:
            text_response = self.page_visitor.get_sentences(int(self.cursor.idx_paragraph))
            self.cursor.idx_paragraph += 2
        except IndexError:
            text_response = "You have reached the end of the page."
            self.cursor.idx_paragraph = 0
        except FileNotFoundError:
            text_response = "Sorry, this page is not ready. Try again later!"

        return self.build_response(text_response)

    def open_page_link(self, parameters):
        """
        Visits the web page linked in the cursor, then sets the cursor on that page.
        """
        # Get the parameter from the request.
        link_num = int(parameters.get("number"))
        # Get URL to visit from the DB and update the cursor.
        link_url = Database().get_page_link(page_url=self.cursor.url, link_num=link_num)
        if link_url is not None:
            self.cursor.url = link_url[0]
            return self.visit_page()
        else:
            return self.build_response("Wrong input.")

    def open_menu_link(self, parameters):
        """
        Opens the section of the menu, if present.
        """
        # Get the parameter from the request.
        link_num = int(parameters.get("number"))
        try:
            new_url = get_menu_link(url=self.cursor.url, number=link_num)
            self.cursor.url = new_url
            return self.visit_page()
        except ValueError:
            return self.build_response("Wrong input.")

    def build_response(self, text_response):
        """
        Put the successful response in the queue.
        """
        self.q.put(
            {
                "fulfillmentText": text_response,
                "outputContexts": [{
                    "name": "projects/<Project ID>/agent/sessions/<Session ID>/contexts/cursor",
                    "lifespanCount": 1,
                    "parameters": vars(self.cursor)
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
            print(f"{Fore.CYAN}Sent request for more time.{Style.RESET_ALL}")
            self.q.put(
                {
                    "followupEventInput": {
                        "name": "timeout-" + action,
                        "parameters": vars(self.cursor),
                        "languageCode": "en-US"
                    }
                })
