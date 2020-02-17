import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse


resp_text = "The Robots are coming! Head for the hills!"
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello again from my web server!"

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    resp = MessagingResponse()
    resp.message(resp_text)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
