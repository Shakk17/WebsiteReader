import requests


class DatumBox:
    base_url = "http://api.datumbox.com:80/1.0/"

    def __init__(self, api_key):
        self.api_key = api_key

    def topic_classification(self, text):
        """Possible topics are "Arts", "Business & Economy", "Computers & Technology", "Health", "Home & Domestic
        Life", "News", "Recreation & Activities", "Reference & Education", "Science", "Shopping","Society" or "Sports
        """
        return self._classification_request(text, "TopicClassification")

    def detect_language(self, text):
        """Returns an ISO_639-1 language code"""
        return self._classification_request(text, "LanguageDetection")

    def text_extract(self, text):
        """Extracts text from a webpage"""
        return self._classification_request(text, "TextExtraction")

    def _classification_request(self, text, api_name):
        full_url = DatumBox.base_url + api_name + ".json"
        return self._send_request(full_url, {'text': text})

    def _send_request(self, full_url, data_dict):
        params_dict = dict()
        params_dict['api_key'] = self.api_key
        request = requests.post(url=full_url, params=params_dict, data=data_dict)
        response = request.json()

        if "error" in response['output']:
            raise DatumBoxError(response['output']['error']['ErrorCode'], response['output']['error']['ErrorMessage'])
        else:
            return response['output']['result']


class DatumBoxError(Exception):
    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self):
        return "Datumbox API returned an error: " + str(self.error_code) + " " + self.error_message
