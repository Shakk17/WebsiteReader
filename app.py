from flask import Flask, request, make_response, jsonify

from reader import PdfBookParser
from book import Book


app = Flask(__name__)

pdf_book_parser = PdfBookParser()

book = Book(pdf_book_parser)


# default route
@app.route('/')
def index():
    return 'Hello World!'


# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)

    return jsonify(book.get_response(req))


# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(results())


# run the app
if __name__ == '__main__':
    app.run()
