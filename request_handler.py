import queue
import threading
import time


from databases.handlers.history_handler import db_insert_action, db_get_last_action, db_delete_last_action
from databases.handlers.text_links_handler import db_get_text_link
from functionality.analysis import analyze_page, analyze_domain, get_info
from functionality.bookmarks import insert_bookmark, delete_bookmark, get_bookmarks
from functionality.forms import get_text_field_form, submit_form
from functionality.functionality import get_functionality
from functionality.links import read_links, get_links_text_response, read_links_article
from functionality.main_text import get_main_text_sentences
from functionality.menu import get_menu
from helpers.api import get_urls_from_google
from helpers.cursor import Cursor
from helpers.exceptions import NoSuchFormError, PageRequestError
from helpers.helper import update_cursor_index, show_element
from helpers.printer import green, blue, red, magenta
from helpers.utility import add_scheme, get_domain
from helpers.utility import get_time

TIMEOUT = 3


class RequestHandler:
    """
    This class handles the requests received by the server from the agent.
    """
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
        print(green(f"[SERVER] Action: {action}"))

        # Get main context from request, if available.
        contexts = request.get("queryResult").get("outputContexts")
        cursor_context = next((x for x in contexts if "cursor" in x.get("name")), None)

        # Create a Cursor object containing details about the web page.
        self.cursor = Cursor(cursor_context)

        text_response = "Action not recognized by the server."

        # If the action is History, get the previous action from the database and execute it.
        if action.startswith("History"):
            a = action
            try:
                action, url = db_get_last_action("shakk")
                if a.endswith("previous"):
                    db_delete_last_action("shakk")
            except TypeError:
                text_response = "History is empty."

        if action.startswith("GoogleSearch"):
            text_response = self.google_search(action=action.split("_")[-1])
        elif action.startswith("Bookmarks"):
            text_response = self.bookmarks(command=action.split("_")[-2], action=action.split("_")[-1])
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
        elif action.startswith("OpenTextLink"):
            text_response = self.open_text_link()
        elif action.startswith("ReadLinks"):
            text_response = self.read_links(links_type=action.split("_")[-2], action=action.split("_")[-1])
        elif action.startswith("OpenLink"):
            text_response = self.open_link(links_type=action.split("_")[-1])
        elif action.startswith("FillForm"):
            text_response = self.fill_form(action=action.split("_")[-1])

        return self.build_response(text_response=text_response)

    def google_search(self, action):
        """
        This method:
            - if the user has performed a search, it returns one of the results of the Google search;
            - if the user has requested a specific URL, it returns info about the website reachable at that URL.
        :param query_results: A list containing the results of the Google search.
        :param action: a string containing "previous", "next" or "reset".
        :return: A string containing info about one result of the Google search or info about a web page.
        """
        try:
            query_results = get_urls_from_google(query=self.cursor.query)
        except Exception:
            return "Error while searching on Google."

        # Update cursor.
        self.cursor.idx_search_result = update_cursor_index(
            action=action, old_idx=self.cursor.idx_search_result, step=1, size=5)

        result = query_results[self.cursor.idx_search_result]
        text_response = f"""Result number {self.cursor.idx_search_result + 1}.
                                Do you want to visit the page: {result[0]} at {get_domain(result[1])}?"""
        self.cursor.url = result[1]

        return text_response

    def bookmarks(self, command, action):
        text_response = "Command not recognized."

        if command == "show":
            bookmarks = get_bookmarks(user="shakk")
            # Number of choices that will get displayed to the user at once.
            num_choices = 5
            # Update cursor.
            self.cursor.idx_bookmarks = update_cursor_index(action=action, old_idx=self.cursor.idx_bookmarks,
                                                            step=num_choices, size=len(bookmarks))
            # Get text response containing voices to show.
            text_response = show_element(element=bookmarks, idx_start=self.cursor.idx_bookmarks,
                                         num_choices=num_choices)
        elif command == "add":
            text_response = insert_bookmark(url=self.cursor.url, name=self.cursor.name)
        elif command == "delete":
            bookmarks = get_bookmarks(user="shakk")
            url = bookmarks[self.cursor.idx_bookmarks]
            text_response = delete_bookmark(url=url, user="shakk")
        elif command == "open":
            bookmarks = get_bookmarks(user="shakk")
            try:
                index = self.cursor.number - 1
                self.cursor.url = bookmarks[index][0]
                text_response = self.visit_page()
            except IndexError:
                text_response = "Wrong input."
        return text_response

    def visit_page(self):
        """
        This method:
        - save the action performed in the database;
        - extracts information about the web page;
        - checks if the domain has been already crawled. If not, it starts a new crawl.
        :return: A text response containing information to show to the user about the web page.
        """
        # Save, if new, the action performed by the user into the history table of the database.
        try:
            old_action, old_url = db_get_last_action("shakk")
        except TypeError:
            old_url = ""
        if old_url != self.cursor.url:
            db_insert_action("VisitPage", self.cursor.url)

        try:
            analyze_page(url=self.cursor.url)
            # Get info about the web page.
            text_response = get_info(url=self.cursor.url)
            self.cursor.reset_indexes()
            # Start analyzing the domain in the background.
            threading.Thread(target=analyze_domain, args=(self.cursor.url,)).start()
        except PageRequestError:
            text_response = "Error while visiting the website. Say 'reload' to try again."
            print(magenta(text_response))

        return text_response

    def go_to_homepage(self):
        """
        This method visits the homepage of the current website.
        :return:
        """
        self.cursor.url = add_scheme(get_domain(self.cursor.url))
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
        text_response = show_element(element=menu, idx_start=self.cursor.idx_menu, num_choices=num_choices)

        return text_response

    def open_menu_link(self):
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
        # Update cursor.
        self.cursor.idx_sentence = update_cursor_index(action, old_idx=self.cursor.idx_sentence, step=2, size=10000)
        try:
            # Get sentences from the main text to be shown to the user.
            text_response = get_main_text_sentences(
                url=self.cursor.url, idx_sentence=self.cursor.idx_sentence, n_sentences=2)
        except IndexError:
            text_response = "No more sentences to read, you have reached the end of the page."
            # Reset cursor position.
            self.cursor.idx_sentence = 0
        except FileNotFoundError:
            text_response = "Sorry, this page is still in the process of being analysed. Try again later!"

        return text_response

    def open_text_link(self):
        # Get URL to visit from the DB.
        link_url = db_get_text_link(page_url=self.cursor.url, link_num=self.cursor.number)

        # If the link is valid, update the cursor and visit the page.
        if link_url is not None:
            self.cursor.url = link_url[0]
            return self.visit_page()
        else:
            return "Wrong input."

    def read_links(self, links_type, action):
        links = []
        idx_start = 0
        num_choices = 5
        if links_type == "all":
            links = read_links(url=self.cursor.url)
            self.cursor.idx_link = update_cursor_index(
                action, old_idx=self.cursor.idx_link, step=num_choices, size=len(links))
            idx_start = self.cursor.idx_link
        elif links_type == "article":
            links = read_links_article(url=self.cursor.url)
            num_choices = 3
            self.cursor.idx_link_article = update_cursor_index(
                action, old_idx=self.cursor.idx_link_article, step=num_choices, size=len(links))
            idx_start = self.cursor.idx_link_article
        elif links_type == "best":
            links = get_functionality(url=self.cursor.url)
            self.cursor.idx_link_best = update_cursor_index(
                action, old_idx=self.cursor.idx_link_best, step=num_choices, size=len(links))
            idx_start = self.cursor.idx_link_best

        try:
            text_response = get_links_text_response(links=links, idx_start=idx_start, num_choices=num_choices)
        except IndexError:
            text_response = "No more links to read, you have reached the end of the page."
            if links_type == "all":
                self.cursor.idx_link = 0
            elif links_type == "article":
                self.cursor.idx_link_article = 0
            elif links_type == "best":
                self.cursor.idx_link_best = 0

        return text_response

    def open_link(self, links_type):
        # Select the right type of links.
        link_url = None
        if links_type == "all":
            links = read_links(url=self.cursor.url)
            link_url = links[self.cursor.number - 1]
        elif links_type == "article":
            links = read_links_article(url=self.cursor.url)
            link_url = links[self.cursor.number - 1]

        # If the link is valid, update the cursor and visit the page.
        if link_url is not None:
            self.cursor.url = link_url[1]
            return self.visit_page()
        else:
            return "Wrong input."

    def fill_form(self, action):
        url = self.cursor.url
        if action == "start":
            # Initialize form parameters.
            self.cursor.idx_form = self.cursor.number - 1
            self.cursor.form_parameters = {}
        elif action == "write":
            user_input = self.cursor.user_input
            self.cursor.form_parameters[self.cursor.idx_field] = user_input
            self.cursor.idx_field += 1
        elif action == "submit":
            fields_values = list(self.cursor.form_parameters.values())
            self.cursor.url = submit_form(url=url, form_number=self.cursor.idx_form, fields_values=fields_values)
            return self.visit_page()
        try:
            field_text = get_text_field_form(url=url,
                                             form_number=self.cursor.idx_form, field_number=self.cursor.idx_field)
            text_response = f"What do you want to write in the field: {field_text}? Start your answer with 'write'!"
        except NoSuchFormError:
            text_response = "Form not found."
        except Exception:
            text_response = f"You successfully filled all the fields. Write 'submit' to submit the form."
            # TODO: recap fields for user.

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
