import os
from twilio.rest import Client


SERVER_DIRECTORY = '/var/www/sms'
SEND_LIST = 'attendee_list'
SEND_LIST_MSG = 'attendee_msg'

debug_app = False


account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
my_twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]

if (os.path.exists(os.path.join(SERVER_DIRECTORY, SEND_LIST)) and
    os.path.exists(os.path.join(SERVER_DIRECTORY, SEND_LIST_MSG))):
    # Send message to list using message from text file
    with open(os.path.join(SERVER_DIRECTORY, SEND_LIST)) as file:
        phone_list = file.read().split('\n')

        if debug_app:
            print(phone_list)

    with open(os.path.join(SERVER_DIRECTORY, SEND_LIST_MSG)) as file:
        msg = file.read()

        if debug_app:
            print(msg)

    for number in phone_list:
        if number:
            receive_phone_number = number
            client = Client(account_sid, auth_token)
            client.messages.create(to=receive_phone_number,
                                   from_=my_twilio_phone_number,
                                   body=msg)

            if debug_app:
                print(f'Sent text to {number}')
else:
    receive_phone_number = os.environ["MY_PHONE_NUMBER"]
    test_text = "This is a test.  This is only a test."
    client = Client(account_sid, auth_token)
    client.messages.create(to=receive_phone_number,
                           from_=my_twilio_phone_number,
                           body=test_text)
