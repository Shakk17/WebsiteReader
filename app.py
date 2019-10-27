from flask import Flask, request, make_response, jsonify

from page_parser import HtmlParser

app = Flask(__name__)

parser = HtmlParser()


# default route
@app.route('/')
def index():
    return 'Hello World!'


# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)

    return jsonify(parser.get_response(req))


# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(results())


# run the app
if __name__ == '__main__':
    app.run()
