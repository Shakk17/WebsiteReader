import logging

from colorama import Fore, Style
from flask import Flask, request, make_response, jsonify

from databases.models import create_tables
from helpers.utility import get_time
from request_handler import RequestHandler

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

parser = RequestHandler()


# default route
@app.route('/')
def index():
    return 'Hello World!'


# function for responses
def results():
    print("-" * 20)
    print(f"{Fore.CYAN}{get_time()} [SERVER] New request received.{Style.RESET_ALL}")

    # Parse JSON request into a readable object.
    req = request.get_json(force=True)

    obj_response = parser.get_response(req)

    return jsonify(obj_response)


# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(results())


# run the app
if __name__ == '__main__':
    create_tables()
    # Database().start()
    app.run()

