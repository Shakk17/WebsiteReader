from url_parser import UrlParser

import queue
import threading
import time


class WebPage:
    def __init__(self, url):
        self.url = url
        # Type of the page, it can be article or section.
        self.type = None
        # Number that indicates the paragraph to read in current article.
        self.idx_paragraph = 0
        # Number that indicates the article to read in current section.
        self.idx_article = 0
        # Link selected.
        self.link = None


class RequestHandler:
    def __init__(self):
        self.url_parser = None
        self.web_page = None
        self.q = queue.Queue()

    def get_response(self, request):
        main_thread = threading.Thread(target=self.elaborate, args=(request,), daemon=True)
        timeout_thread = threading.Thread(target=self.postpone_response, args=(request,), daemon=True)
        main_thread.start()
        timeout_thread.start()
        # Wait until timeout is finished.
        timeout_thread.join()

        # Returns the first available result.
        result = self.q.get()

        return result

    def elaborate(self, request):
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

        # Create object containing details about the web page.
        self.web_page = WebPage(url=url)

        try:
            self.web_page.type = context.get("parameters").get("web_page").get("type")
            self.web_page.idx_paragraph = int(context.get("parameters").get("web_page").get("idx_paragraph"))
            self.web_page.idx_article = int(context.get("parameters").get("web_page").get("idx_article"))
            self.web_page.link = context.get("parameters").get("web_page").get("link")
        except AttributeError:
            self.web_page.type = "article"
            self.web_page.idx_paragraph = 0
            self.web_page.idx_article = 0
            self.web_page.link = url

        # Initiate UrlParser.
        self.url_parser = UrlParser(url=url)

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

    def visit_page(self):
        try:
            text_response = "%s visited successfully!" % self.url_parser.url
            self.web_page = WebPage(self.url_parser.url)
            # Understand what type of page is.
            if self.url_parser.is_article():
                self.web_page.type = "article"
                text_response += "\nThis page is an article."
            else:
                self.web_page.type = "section"
                text_response += "\nThis page is a section."

        except Exception as ex:
            text_response = ex.args[0]

        # Update url in context.
        return self.build_response(text_response)

    def get_menu(self):
        menu = self.url_parser.get_menu()
        strings = [tup[1] for tup in menu]
        text_response = '-'.join(strings)
        # TODO get elements of menu, how many?
        return self.build_response(text_response)

    def get_info(self):
        text_response = self.url_parser.get_info()
        return self.build_response(text_response)

    def read_page(self):
        # If page is article, read it. otherwise read main article titles available.
        if self.url_parser.is_article():
            try:
                text_response = self.url_parser.get_article(self.web_page.idx_paragraph)
                self.web_page.idx_paragraph += 1
            except IndexError as err:
                text_response = "End of article."
                self.web_page.idx_paragraph = 0
        else:
            try:
                article = self.url_parser.get_section(self.web_page.idx_article)
                text_response = article[0]
                self.web_page.link = article[1]
                self.web_page.idx_article += 1
            except IndexError as err:
                text_response = "End of section."
                self.web_page.idx_article = 0
        return self.build_response(text_response)

    def open_link(self):
        self.url_parser = UrlParser(url=self.web_page.link)
        self.web_page.url = self.web_page.link
        return self.visit_page()

    def go_to_section(self, name):
        try:
            new_url = self.url_parser.go_to_section(name)
            self.url_parser = UrlParser(new_url)
            return self.visit_page()
        except ValueError:
            return "Wrong input."

    def build_response(self, text_response):
        print("URL: %s" % self.web_page.url)

        self.q.put(
            {
                "fulfillmentText": text_response,
                "outputContexts": [{
                    "name": "projects/<Project ID>/agent/sessions/<Session ID>/contexts/web-page",
                    "lifespanCount": 1,
                    "parameters": {
                        "web_page": vars(self.web_page)
                    }
                }]
            })

    def postpone_response(self, request):
        # Get action from request.
        action = request.get('queryResult').get('action')

        # Start timer.
        time.sleep(2.5)
        # After 4 seconds, checks if the main thread has terminated.
        if self.q.empty():
            # Send a response to server to ask for 5 more seconds to answer. Valid only two times.
            print("Sent request for more time.")
            self.q.put(
                {
                    "followupEventInput": {
                        "name": "timeout-" + action,
                        "parameters": vars(self.web_page),
                        "languageCode": "en-US"
                    }
                })
