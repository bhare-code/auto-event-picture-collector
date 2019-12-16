import requests
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse


DOWNLOAD_DIRECTORY = '/home/pi/Pictures'
app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming with a simple text message."""

    resp = MessagingResponse()

    if request.values['NumMedia'] != '0':

        # Use the message SID as a filename.
        filename = request.values['MessageSid'] + '.png'
        with open('{}/{}'.format(DOWNLOAD_DIRECTORY, filename), 'wb') as f:
           image_url = request.values['MediaUrl0']
           f.write(requests.get(image_url).content)

        resp.message("Thanks for the image!")
    else:
        resp.message("Try sending a picture message.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
