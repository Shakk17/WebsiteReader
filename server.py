from flask import Flask, request, make_response, jsonify
from time import time

from request_handler import RequestHandler

app = Flask(__name__)

parser = RequestHandler()


# default route
@app.route('/')
def index():
    return 'Hello World!'


# function for responses
def results():
    start = time()
    # Parse JSON request into a readable object.
    req = request.get_json(force=True)

    obj_response = parser.get_response(req)
    print("Total time elapsed: %.2f" % (time() - start))
    return jsonify(obj_response)


# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(results())


# run the app
if __name__ == '__main__':
    app.run()
