'''
Main event server script
'''
import requests
import pprint
import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse


DOWNLOAD_DIRECTORY = '/home/pi/Pictures'
MY_PERSONAL_PHONE_NUMBER = os.environ["MY_PHONE_NUMBER"]

# Incoming message fields
SMS_FROM = 'From'
SMS_BODY = 'Body'
SMS_MSG_SID = 'MessageSid'
SMS_NUM_MEDIA = 'NumMedia'
SMS_MEDIA_TYPE_BASE = 'MediaContentType'
SMS_MEDIA_URL_BASE = 'MediaUrl'

app = Flask(__name__)
debug_app = True
pretty_print = False

'''
Example text message received with no pictures:
{'AccountSid': 'AC12345abcde12345abcde12345abcde12',
 'ApiVersion': '2010-04-01',
 'Body': 'Test message 3!',
 'From': '+14045551212',
 'FromCity': 'ATLANTA',
 'FromCountry': 'US',
 'FromState': 'GA',
 'FromZip': '30360',
 'MessageSid': 'SM574821705f1458882f283ab5d5cdee12',
 'NumMedia': '0',
 'NumSegments': '1',
 'SmsMessageSid': 'SM574821705f1458882f283ab5d5cdee12',
 'SmsSid': 'SM574821705f1458882f283ab5d5cdee12',
 'SmsStatus': 'received',
 'To': '+17705551212',
 'ToCity': 'FORT LAUDERDALE',
 'ToCountry': 'US',
 'ToState': 'FL',
 'ToZip': '33301'}

Example text message received with one picture and no text:
{'AccountSid': 'AC12345abcde12345abcde12345abcde12',
 'ApiVersion': '2010-04-01',
 'Body': '',
 'From': '+14045551212',
 'FromCity': 'ATLANTA',
 'FromCountry': 'US',
 'FromState': 'GA',
 'FromZip': '30360',
 'MediaContentType0': 'image/jpeg',
 'MediaUrl0': 'https://api.twilio.com/2010-04-01/Accounts/AC12345abcde12345abcde12345abcde12/Messages/MM7225452fbc89614affd898ce3797a32e/Media/ME1938946d1abb1b94c173b7ba82512790',
 'MessageSid': 'MM7225452fbc89614affd898ce3797a32e',
 'NumMedia': '1',
 'NumSegments': '1',
 'SmsMessageSid': 'MM7225452fbc89614affd898ce3797a32e',
 'SmsSid': 'MM7225452fbc89614affd898ce3797a32e',
 'SmsStatus': 'received',
 'To': '+17705551212',
 'ToCity': 'FORT LAUDERDALE',
 'ToCountry': 'US',
 'ToState': 'FL',
 'ToZip': '33301'}

Example text message received with two pictures and text:
{'AccountSid': 'AC12345abcde12345abcde12345abcde12',
 'ApiVersion': '2010-04-01',
 'Body': "Test multiple pics and quote '",
 'From': '+14045551212',
 'FromCity': 'ATLANTA',
 'FromCountry': 'US',
 'FromState': 'GA',
 'FromZip': '30360',
 'MediaContentType0': 'image/jpeg',
 'MediaContentType1': 'image/jpeg',
 'MediaUrl0': 'https://api.twilio.com/2010-04-01/Accounts/AC12345abcde12345abcde12345abcde12/Messages/MMc6d3e08fc6ceb273191e4728452193d3/Media/MEff0ab26db282c6d62e01edc5c68a8a3d',
 'MediaUrl1': 'https://api.twilio.com/2010-04-01/Accounts/AC12345abcde12345abcde12345abcde12/Messages/MMc6d3e08fc6ceb273191e4728452193d3/Media/MEef1319fd82876c44b5a09849d7cb4e09',
 'MessageSid': 'MMc6d3e08fc6ceb273191e4728452193d3',
 'NumMedia': '2',
 'NumSegments': '2',
 'SmsMessageSid': 'MMc6d3e08fc6ceb273191e4728452193d3',
 'SmsSid': 'MMc6d3e08fc6ceb273191e4728452193d3',
 'SmsStatus': 'received',
 'To': '+17705551212',
 'ToCity': 'FORT LAUDERDALE',
 'ToCountry': 'US',
 'ToState': 'FL',
 'ToZip': '33301'}
'''


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming with a simple text message."""

    resp = MessagingResponse()

    try:
        num_pics = int(request.values[SMS_NUM_MEDIA])
    except:
        print('Invalid NumMedia format in received message.')
        pprint.pprint(request.values)
        num_pics = 0

    if num_pics:
        if debug_app:
            print(f'Found {num_pics} pictures in message')

        for idx in range(num_pics):
            try:
                ext = '.' + request.values[SMS_MEDIA_TYPE_BASE + str(idx)].split('/')[-1]
            except:
                print(f'Could not extract MediaContentType from received message for index {idx}.')
                pprint.pprint(request.values)
                ext = '.png'

            # Use the message SID as the base for the filename
            # and the image type as extension
            filename = request.values[SMS_MSG_SID] + '_' + str(idx) + ext

            # TODO: don't overwrite the file if it already exists
            with open('{}/{}'.format(DOWNLOAD_DIRECTORY, filename), 'wb') as f:
               image_url = request.values[SMS_MEDIA_URL_BASE + str(idx)]
               f.write(requests.get(image_url).content)

        if num_pics > 1:
            resp.message("Thanks for the images!")
        else:
            resp.message("Thanks for the image!")

        if debug_app and pretty_print:
            pprint.pprint(request.values)
    elif request.values[SMS_FROM] == MY_PERSONAL_PHONE_NUMBER:
        if debug_app:
            print('Received a command from the admin operator!!!')
        command = request.values[SMS_BODY].lower().strip()

        if command == 'drop':
            if debug_app:
                print('Moving picture to trash...')
            # TODO - move picture to trash folder
        elif command == 'pause':
            if debug_app:
                print('Pausing currently displayed picture...')
            # TODO - pause the currently displayed picture
        else:
            # TODO - add more commands
            if debug_app:
                print(f'Unknown command: "{command}"')
                pprint.pprint(request.values)
    else:
        if debug_app and pretty_print:
            pprint.pprint(request.values)
        resp.message("Try sending a picture message.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=debug_app)
