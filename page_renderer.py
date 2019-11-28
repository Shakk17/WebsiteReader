import webview
from url_parser import UrlParser


url_parser = UrlParser("www.google.it")
html_code = url_parser.soup.prettify()
webview.create_window('Hello world', 'https://pywebview.flowrl.com/hello')
webview.start()