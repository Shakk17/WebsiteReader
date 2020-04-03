import requests
from bs4 import BeautifulSoup

from databases.handlers.pages_handler import db_get_page
from databases.handlers.forms_handler import db_insert_form, db_get_forms
from helpers.utility import remove_scheme

from urllib.parse import quote


def extract_forms(url):
    """
    This method searches in the web-page if there is an input form used to search something in the page.
    :return: (List of input_forms, list of texts)
    """
    url = remove_scheme(url)
    page = db_get_page(url=url)
    webpage = BeautifulSoup(page[4], "lxml")
    forms = webpage.find_all(name="form")
    for i, form in enumerate(forms):
        method = form.get("method")
        action = form.get("action")
        inputs = form.find_all(name="input")
        inputs = [input for input in inputs if input.get("type") == "search" or input.get("type") == "text"]
        for j, input in enumerate(inputs):
            input_name = input.get("name")
            input_text = input.get("placeholder")
            db_insert_form(page_url=url, form_num=i, method=method, action=action,
                           input_num=j, input_name=input_name, input_text=input_text)


def get_text_field_form(url, form_number, field_number):
    fields_forms = db_get_forms(page_url=url)
    fields_form = list(filter(lambda x: x[1] == form_number, fields_forms))
    text = fields_form[field_number][6]
    return text


def submit_form(url, form_number, fields_values):
    fields_forms = db_get_forms(page_url=url)
    fields_form = list(filter(lambda x: x[1] == form_number, fields_forms))
    method = fields_form[0][2]
    action = fields_form[0][3]

    if method.lower() == "get":
        url = f"{action}?"
        # Attach parameters to url.
        for i, value in enumerate(fields_values):
            name = fields_forms[i][5]
            value = quote(value)
            url += f"{name}={value}&"
        return url
    else:
        # TODO: post
        fields_params = [field_form[5] for field_form in fields_forms]
        parameters = dict(zip(fields_params, fields_values))
        response = requests.post(url, parameters)
        return response.url
