from bs4 import BeautifulSoup

from databases.handlers.pages_handler import db_get_page


def extract_search_forms(url):
    """
    This method searches in the web-page if there is an input form used to search something in the page.
    :return: The text of the input form, if present. None otherwise.
    """
    page = db_get_page(url=url)
    webpage = BeautifulSoup(page[4], "lxml")
    search_input_forms = webpage.find_all(name='input', attrs={"type": "search"})
    text_input_forms = webpage.find_all(name='input', attrs={"type": "text"})
    input_forms = search_input_forms + text_input_forms
    input_forms_text = [x.get("placeholder") for x in input_forms]
    return input_forms_text
