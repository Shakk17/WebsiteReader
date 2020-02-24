import queue
import threading
import time
import requests

from colorama import Fore, Style

from databases.database_handler import Database
from scraping.crawler_handler import Crawler
from page_visitor import PageVisitor
from helper import get_menu, get_menu_link, get_domain, get_urls_from_google, fix_url, is_action_recent

TIMEOUT = 4


class Cursor:
    """
    An object that keeps track of the current state of the user.
    It is sent and received by the server (as a JSON) in requests and responses to the agent.
    """
    def __init__(self, cursor_context, url):
        # Number that indicates the paragraph to read in the current article.
        self.idx_sentence = 0
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
            f"\tIdx sentence: {self.idx_sentence}\n"
            f"\tIdx menu: {self.idx_menu}\n"
            f"\tLink: {self.link}\n"
            f"\tSentence number: {self.sentence_number}\n"
            f"{Style.RESET_ALL}")


class RequestHandler:
    """
    This class handles the requests received by the server from the agent.
    """
    page_visitor = None
    cursor = None

    def __init__(self):
        # Queue set up to hold threads responses.
        self.q = queue.Queue()

    def get_response(self, request):
        """
        This method starts two threads.
        The first thread processes the incoming request.
        The second thread waits four second before sending a neq request to the agent.
        Each thread, after its completion, puts the result in a queue.
        After the second thread completes, the first available element from the queue is taken and sent to the agent.
        This escamotage is used to change the waiting time of the agent from 4 seconds to 12 seconds.
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

        # Print the cursor in the console only if the action asked by the user has been completed.
        if result.get("fulfillmentText") is not None:
            print(self.cursor)

        return result

    def elaborate(self, request):
        """
        This method parses the request and decides which action to take.
        :param request: The user request received by the server.
        :return: A well-formed text_response containing the message to show to the user, and the parameters to keep in
                the context.
        """

        # Get action from request.
        action = request.get('queryResult').get('action')
        print("-" * 20)

        # Get main context from request, if available.
        contexts = request.get("queryResult").get("outputContexts")
        cursor_context = next((x for x in contexts if "cursor" in x.get("name")), None)

        # Understand if the string passed is a URL or a query.

        # URL is either in the parameters (VisitPage) or in the context.
        if action == "VisitPage":
            string = request.get("queryResult").get("parameters").get("string")
            try:
                # Fix the URL if it's not well-formed (missing schema).
                url = fix_url(url=string)
                # Try to visit the URL.
                requests.get(url=string)
            except requests.exceptions.RequestException:
                # The string passed is actually a query, get the URL of the first result from Google Search.
                url = get_urls_from_google(string)
        else:
            url = cursor_context.get("parameters").get("url")

        # If the action is GoBack, get the previous action from the database and execute it.
        if action == "GoBack":
            action, url = Database().get_previous_action("shakk")

        # Create a Cursor object containing details about the web page.
        self.cursor = Cursor(cursor_context, url)

        # Save the action performed by the user into the history table of the database.
        Database().insert_action(action, url)
        print(f"Action {action} saved in history.")

        text_response = "Action not recognized by the server."

        if action == "VisitPage":
            text_response = self.visit_page()
        elif action == 'GetInfo':
            text_response =  self.get_info()
        elif action == 'GetMenu':
            text_response = self.get_menu()
        elif action == 'ReadPage':
            text_response = self.read_page()
        elif action == "OpenPageLink":
            text_response = self.open_page_link(link_num=int(cursor_context.get("parameters").get("number")))
        elif action == "OpenMenuLink":
            text_response = self.open_menu_link(link_num=int(cursor_context.get("parameters").get("number")))

        return self.build_response(text_response=text_response)

    def visit_page(self):
        """
        This method:
        - gets the HTML of the web page;
        - extracts information about the web page;
        - updates the cursor;
        - checks if the domain has been already crawled. If not, it starts a new crawl.
        :return: A text response containing information to show to the user about the web page.
        """
        # Get the HTML of the web page.
        self.page_visitor = PageVisitor(url=self.cursor.url)

        # Get info about the web page.
        text_response = self.page_visitor.get_info()

        # Update the cursor.
        self.cursor.url = self.page_visitor.url
        self.cursor.idx_sentence = 0
        self.cursor.idx_menu = 0

        # Checks if domain has been already crawled.
        domain = get_domain(url=self.page_visitor.url)
        to_crawl = False
        last_time_crawled = Database().last_time_crawled(domain=domain)

        # If the domain has never been crawled, crawl it.
        if last_time_crawled is None:
            print(f"The domain {domain} has never been crawled before.")
            to_crawl = True

        # If the domain hasn't been crawled in the last week, cancel the result of the previous crawl. Then crawl again.
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

        # Update the url in context and return info about the web page to the user.
        return text_response

    def get_menu(self):
        """
        This method:
        - analyzes the result of the crawl of a domain and extracts its menu;
        - selects which options are to be shown to the user.
        :return: A text response containing the options to be shown to the user.
        """
        # Number of choices that will get displayed to the user at once.
        num_choices = 10

        # Extract the menu from the crawl results.
        menu = get_menu(self.cursor.url)

        # Get how many elements of the menu have already been shown.
        idx_start = int(self.cursor.idx_menu)

        # Get the indexes of the options to be shown to the user
        if idx_start >= len(menu):
            idx_start = 0
        idx_end = idx_start + 10

        # Get the options that will be shown to the user in the text response.
        strings = [tup[1] for tup in menu[idx_start:idx_end]]

        # Format of display -> option n: text
        #                      option n+1: text
        text_response = "You can choose between: \n"
        for i, string in enumerate(strings, start=1):
            text_response += f"{idx_start + i}: {string}. \n"
        text_response += f"\n{min(idx_start + num_choices, len(menu))} out of {len(menu)} option(s) read."

        # Update cursor.
        self.cursor.idx_menu = idx_start + num_choices

        return text_response

    def get_info(self):
        """
        This method returns info about the web page currently visited to the user.
        :return: A text response containing info about the web page currently visited.
        """
        self.page_visitor = PageVisitor(url=self.cursor.url, quick_download=False)
        # Get info about the web page.
        text_response = self.page_visitor.get_info()
        return text_response

    def read_page(self):
        """
        This method gets the main text of the web page and returns a part of it to be shown to the user.
        It also updates the cursor.
        :return: A text response containing a part of the main text of the web page.
        """
        self.page_visitor = PageVisitor(url=self.cursor.url, quick_download=False)
        try:
            # Get actual position of the cursor in the main text.
            idx_sentence = int(self.cursor.idx_sentence)
            # Get sentences from the main text to be shown to the user.
            text_response = self.page_visitor.get_sentences(idx_sentence=idx_sentence, n_sentences=2)
            # Update cursor.
            self.cursor.idx_sentence += 2
        except IndexError:
            # There are no more sentences to be read.
            text_response = "You have reached the end of the page."
            # Reset cursor position.
            self.cursor.idx_sentence = 0
        except FileNotFoundError:
            text_response = "Sorry, this page is still in the process of being analysed. Try again later!"

        return text_response

    def open_page_link(self, link_num):
        """
        This method visits the link chosen from the page by the user.
        :param link_num: The position in the page of the link to be visited.
        :return: A text response containing info about the new web page.
        """
        # Get URL to visit from the DB.
        link_url = Database().get_page_link(page_url=self.cursor.url, link_num=link_num)

        # If the link is valid, update the cursor and visit the page.
        if link_url is not None:
            self.cursor.url = link_url[0]
            return self.visit_page()
        else:
            return "Wrong input."

    def open_menu_link(self, link_num):
        """
        This method visits the link chosen from the menu by the user.
        :param link_num: The position in the menu of the link to be visited.
        :return: A text response containing info about the new web page.
        """
        try:
            # Get URL to visit from the DB.
            new_url = get_menu_link(url=self.cursor.url, number=link_num)
            # Update cursor and visit the page.
            self.cursor.url = new_url
            return self.visit_page()
        except ValueError:
            return "Wrong input."

    def build_response(self, text_response):
        """
        This method builds a response message to send back to the agent.
        :param text_response: A text message containing the message to be shown to the user.
        :return: A well-formed response message to be sent to the agent.
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
        This method is used to request additional time to the DialogFlow agent.
        The DialogFlow agent normally needs to receive a response in the next 4 seconds since its request to the server.
        This is an escamotage used to push this limit to 12 seconds by triggering another event.
        The server sends back a request containing the same payload as the one sent by the agent.
        This request sent to the agent triggers an event that makes the agent resend the request to the server.
        ATTENTION: the intent triggered by the user MUST have "timeout-'actionName'" as an Event.
        It can only used 2 times, after the third trigger the agent will just display a standard response to the user.
        :param request: The request sent by the agent to the server.
        :param seconds: The seconds that the server will wait before asking more time to the agent.
        :return: A response containing the request payload and the trigger for the event.
        """
        # Get action from request.
        action = request.get('queryResult').get('action')

        # Start timer.
        time.sleep(seconds)
        # After the timer is over, if the main thread has not finished yet, send the request for more time.
        if self.q.empty():
            print(f"{Fore.CYAN}Sent request for more time.{Style.RESET_ALL}")
            # Send a response to server to ask for more time. Valid only two times.
            self.q.put(
                {
                    "followupEventInput": {
                        "name": "timeout-" + action,
                        "parameters": vars(self.cursor),
                        "languageCode": "en-US"
                    }
                })
