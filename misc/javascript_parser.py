import webview
from url_parser import UrlParser


def load_html(window):
    url_parser = UrlParser("http://www.open.online")

    html_code = url_parser.soup.prettify()
    window.load_html(html_code)


window = webview.create_window('Hello world')
webview.start(load_html, window)
