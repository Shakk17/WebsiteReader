import requests
from bs4 import BeautifulSoup

from databases.handlers.pages_handler import db_get_page
from databases.handlers.search_forms_handler import db_insert_search_form, db_get_search_forms
from helpers.utility import remove_scheme

from urllib.parse import quote


def extract_search_forms(url):
    """
    This method searches in the web-page if there is an input form used to search something in the page.
    :return: (List of input_forms, list of texts)
    """
    url = remove_scheme(url)
    page = db_get_page(url=url)
    webpage = BeautifulSoup(page[4], "lxml")
    forms = webpage.find_all(name="form")
    """search_input_forms = webpage.find_all(name='input', attrs={"type": "search"})
    text_input_forms = webpage.find_all(name='input', attrs={"type": "text"})
    input_forms = search_input_forms + text_input_forms"""
    for i, form in enumerate(forms):
        method = form.get("method")
        action = form.get("action")
        inputs = form.find_all(name="input")
        inputs = [input for input in inputs if input.get("type") == "search" or input.get("type") == "text"]
        for j, input in enumerate(inputs):
            input_name = input.get("name")
            input_text = input.get("placeholder")
            db_insert_search_form(page_url=url, form_num=i, method=method, action=action,
                                  input_num=j, input_name=input_name, input_text=input_text)


def fill_search_form(url, number, query):
    forms = db_get_search_forms(page_url=url)
    form = forms[number]
    method = form[2]
    action = form[3]

    if method.lower() == "get":
        name = form[5]
        # Make query safe to be put in URL.
        query = quote(query)
        url = f"{action}?{name}={query}"
        return url
    else:
        # TODO: post
        pass
