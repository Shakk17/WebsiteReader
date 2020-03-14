import html
import re

import tldextract


def strip_html_tags(text):
    """
    This method takes a string of text, unescapes special characters and removes any HTML tag from it.
    :param text: A string of text.
    :return: A string without escaped characters or HTML tags.
    """
    # Unescape difficult character like &amp;.
    text = html.unescape(str(text))
    # Remove all the html tags.
    regex = re.compile(r'<[^>]+>')
    text = regex.sub('', text)
    # Remove \n and \t.
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    # Remove spaces at the beginning and at the end of the string.
    text = text.strip()
    return text


def get_domain(url, complete=False):
    """
    This method extracts the domain from the URL of a website.
    :param complete: True is the subdomain is also needed, False otherwise.
    :param url: A string containing the URL.
    :return: A string containing the domain extracted from the URL.
    """
    extracted_domain = tldextract.extract(url)
    subdomain = extracted_domain.subdomain.replace("www.", "")
    if complete and len(subdomain) > 0:
        domain = f"{subdomain}.{extracted_domain.domain}.{extracted_domain.suffix}"
    else:
        domain = f"{extracted_domain.domain}.{extracted_domain.suffix}"
    return domain


def add_schema(url):
    """
    This method takes a URL and returns a well-formed URL. If the schema is missing, it will get added.
    :param url: A string containing a URL.
    :return: A string containing a well-formed URL.
    """
    if not re.match('(?:http|ftp|https)://', url):
        return 'http://{}'.format(url)
    return url


def extract_words(string):
    """
    Given a string, it returns all the words contained in it.
    :param string: The string to be analysed.
    :return: A list containing all the words contained in the string.
    """
    regex = r'\b\w+\b'
    words = re.findall(regex, string)
    return words
