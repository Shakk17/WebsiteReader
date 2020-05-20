In order to run the server locally, the following actions need to be taken:
1) download ngrok from https://ngrok.com/download
2) run ngrok
3) execute the command "ngrok http 5000" in the ngrok prompt
4) copy the URL from the row starting with "Forwarding" (it should be something like https://263b9e40.ngrok.io)
5) open Dialogflow (dialogflow.com)
6) open the section Fulfillment and paste the URL into the URL field before /webhook (https://263b9e40.ngrok.io/webhook)
7) open the IDE of choice, e.g., PyCharm
8) run the server.py file
