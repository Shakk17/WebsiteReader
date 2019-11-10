from flask import Flask, request, make_response, jsonify
import json

from open_reader import OpenReader

app = Flask(__name__)

parser = OpenReader()


# default route
@app.route('/')
def index():
    return 'Hello World!'


# function for responses
def results():
    # Parse JSON request into readable object.
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
    app.run()
