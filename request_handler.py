import queue
import threading
import time

import requests
from colorama import Style

from databases.history_handler import db_insert_action, db_get_previous_action
from databases.text_links_handler import db_get_text_link
from functionality.menu import get_menu, get_menu_text_response
from helpers.api import get_urls_from_google
from helpers.helper import update_cursor_index, get_menu_link, get_sentences, read_links
from helpers.printer import green, blue, red, magenta
from helpers.utility import add_schema, get_domain
from helpers.utility import get_time
from functionality.analysis import analyze_page, analyze_domain, get_info

TIMEOUT = 3


class Cursor:
    """
    An object that keeps track of the current state of the user.
    It is sent and received by the server (as a JSON) in requests and responses to the agent.
    """

    def __init__(self, cursor_context):
        self.url = "https://www.google.com"
        # Number that indicates the paragraph to read in the current article.
        self.idx_sentence = 0
        # Number that indicates the article to read in the current section.
        self.idx_menu = 0
        # Number of GoogleSearch result to show.
        self.idx_search_result = 0
        # Index of next link to read in the page.
        self.idx_link = 0

        # Updates cursor with values received from the context.
        for key, value in cursor_context.get("parameters").items():
            if not key.endswith("original"):
                try:
                    value = int(value)
                except ValueError:
                    pass
                setattr(self, key, value)

    def __repr__(self):
        return (green(
            f"{Style.BRIGHT}+++ CURSOR +++{Style.NORMAL}\n"
            f"\tURL: {self.url}\n"
            f"\tIdx sentence: {self.idx_sentence}\n"
            f"\tIdx menu: {self.idx_menu}\n"
            f"\tIdx search result: {self.idx_search_result}\n"
            f"\tIdx link: {self.idx_link}\n"
        ))


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
            # print(self.cursor)
            print(blue(f"{get_time()} [SERVER] Response sent to the server."))
        else:
            print(red(f"{get_time()} [SERVER] Sent request for more time."))

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

        # Get main context from request, if available.
        contexts = request.get("queryResult").get("outputContexts")
        cursor_context = next((x for x in contexts if "cursor" in x.get("name")), None)

        # Create a Cursor object containing details about the web page.
        self.cursor = Cursor(cursor_context)

        # Understand if the string passed is a URL or a query.

        # URL is either in the parameters (VisitPage) or in the context.
        url = ""
        query_results = None
        if action.startswith("SearchPage"):
            string = self.cursor.string
            # Try both http and https schemas.
            try:
                url = string.replace("www.", "")
                url = add_schema(url=url)
                # Try to visit the URL.
                requests.get(url=url)
            except requests.exceptions.RequestException:
                # The string passed is actually a query, get the first 5 results from Google Search.
                query_results = get_urls_from_google(string)
        else:
            url = self.cursor.url

        self.cursor.url = add_schema(url)

        # If the action is History, get the previous action from the database and execute it.
        if action.startswith("History"):
            action, url = db_get_previous_action("shakk")

        text_response = "Action not recognized by the server."

        if action.startswith("SearchPage"):
            text_response = self.search_page(query_results=query_results, action=action.split("_")[-1])
        elif action.startswith("VisitPage"):
            text_response = self.visit_page()
        elif action.startswith("GoToHomepage"):
            text_response = self.go_to_homepage()
        elif action.startswith("GetInfo"):
            text_response = self.get_info()
        elif action.startswith("GetMenu"):
            text_response = self.get_menu(action=action.split("_")[-1])
        elif action.startswith("OpenMenuLink"):
            text_response = self.open_menu_link()
        elif action.startswith("ReadPage"):
            text_response = self.read_page(action=action.split("_")[-1])
        elif action.startswith("OpenPageLink"):
            text_response = self.open_page_link()
        elif action.startswith("ReadLinks"):
            text_response = self.read_links(action=action.split("_")[-1])
        elif action.startswith("OpenTextLink"):
            text_response = self.open_text_link()

        return self.build_response(text_response=text_response)

    def search_page(self, query_results, action):
        """
        This method:
            - if the user has performed a search, it returns one of the results of the Google search;
            - if the user has requested a specific URL, it returns info about the website reachable at that URL.
        :param query_results: A list containing the results of the Google search.
        :param action: a string containing "previous", "next" or "reset".
        :return: A string containing info about one result of the Google search or info about a web page.
        """
        # Reset the counter if a new search is performed.
        self.cursor.idx_search_result = update_cursor_index(
            action=action, old_idx=self.cursor.idx_search_result, step=1, size=5)

        # If the parameter given by the user was a valid URL, visit the page.
        if query_results is None:
            text_response = self.visit_page()
        # Otherwise, return one of the Google Search results.
        else:
            result = query_results[self.cursor.idx_search_result]
            text_response = f"""Result number {self.cursor.idx_search_result + 1}.
                                    Do you want to visit the page: {result[0]} at {get_domain(result[1])}?"""
            self.cursor.url = result[1]
        return text_response

    def visit_page(self):
        """
        This method:
        - save the action performed in the database;
        - extracts information about the web page;
        - checks if the domain has been already crawled. If not, it starts a new crawl.
        :return: A text response containing information to show to the user about the web page.
        """
        # Save the action performed by the user into the history table of the database.
        db_insert_action("VisitPage", self.cursor.url)

        try:
            analyze_page(url=self.cursor.url)

            analyze_domain(url=self.cursor.url)

            # Get info about the web page.
            text_response = get_info(url=self.cursor.url)
        except Exception:
            print(magenta("Error encountered."))
            return "Error encountered. Try again!"

        # Update the cursor.
        self.cursor.idx_sentence = 0
        self.cursor.idx_menu = 0
        self.cursor.idx_link = 0

        # Update the url in context and return info about the web page to the user.
        return text_response

    def go_to_homepage(self):
        """
        This method visits the homepage of the current website.
        :return:
        """
        self.cursor.url = add_schema(get_domain(self.cursor.url, complete=True))
        text_response = self.visit_page()
        return text_response

    def get_info(self):
        """
        This method returns info about the web page currently visited to the user.
        :return: A text response containing info about the web page currently visited.
        """
        # Get info about the web page.
        text_response = get_info(url=self.cursor.url)
        return text_response

    def get_menu(self, action):
        """
        This method:
        - analyzes the result of the crawl of a domain and extracts its menu;
        - selects which options are to be shown to the user.
        :return: A text response containing the options to be shown to the user.
        """
        # Extract the menu from the crawl results.
        menu = get_menu(self.cursor.url)
        # Update cursor.
        self.cursor.idx_menu = update_cursor_index(action=action, old_idx=self.cursor.idx_menu, step=10, size=len(menu))
        # Number of choices that will get displayed to the user at once.
        num_choices = 10
        # Get text response containing voices to show.
        text_response = get_menu_text_response(menu=menu, idx_start=self.cursor.idx_menu, num_choices=num_choices)

        return text_response

    def open_menu_link(self):
        """
        This method visits the link chosen from the menu by the user.
        :return: A text response containing info about the new web page.
        """
        menu = get_menu(url=self.cursor.url)
        # Get all the URLs of the menu links.
        menu_anchors = [tup[2] for tup in menu]
        try:
            # Get URL to visit.
            new_url = menu_anchors[self.cursor.number - 1]
        except ValueError:
            return "Wrong input."
        # Update cursor and visit the page.
        self.cursor.url = new_url
        return self.visit_page()

    def read_page(self, action):
        """
        This method gets the main text of the web page and returns a part of it to be shown to the user.
        It also updates the cursor.
        :return: A text response containing a part of the main text of the web page.
        """
        # Update cursor.
        self.cursor.idx_sentence = update_cursor_index(action, old_idx=self.cursor.idx_sentence, step=2, size=10000)
        try:
            # Get sentences from the main text to be shown to the user.
            text_response = get_sentences(url=self.cursor.url, idx_sentence=self.cursor.idx_sentence, n_sentences=2)
        except IndexError:
            text_response = "No more sentences to read, you have reached the end of the page."
            # Reset cursor position.
            self.cursor.idx_sentence = 0
        except FileNotFoundError:
            text_response = "Sorry, this page is still in the process of being analysed. Try again later!"

        return text_response

    def open_page_link(self):
        # Get URL to visit from the DB.
        links = read_links(url=self.cursor.url)
        link_url = links[self.cursor.idx_link]

        # If the link is valid, update the cursor and visit the page.
        if link_url is not None:
            self.cursor.url = link_url[1]
            return self.visit_page()
        else:
            return "Wrong input."

    def open_text_link(self):
        """
        This method visits the link chosen from the page by the user.
        :return: A text response containing info about the new web page.
        """
        # Get URL to visit from the DB.
        link_url = db_get_text_link(page_url=self.cursor.url, link_num=self.cursor.number)

        # If the link is valid, update the cursor and visit the page.
        if link_url is not None:
            self.cursor.url = link_url[0]
            return self.visit_page()
        else:
            return "Wrong input."

    def read_links(self, action):
        links = read_links(url=self.cursor.url)
        self.cursor.idx_link = update_cursor_index(
            action=action, old_idx=self.cursor.idx_link, step=1, size=len(links))
        if len(links) > 0:
            try:
                text_response = f"Do you want to visit:\n '{links[self.cursor.idx_link][0]}'?"
            except IndexError:
                text_response = "No more links in the page."
                self.cursor.idx_link = 0
        else:
            text_response = "Wait for the page to be analyzed."
        return text_response

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
            # Send a response to server to ask for more time. Valid only two times.
            self.q.put(
                {
                    "followupEventInput": {
                        "name": "timeout-" + action,
                        "parameters": vars(self.cursor),
                        "languageCode": "en-US"
                    }
                })
