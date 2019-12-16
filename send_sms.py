import os
from twilio.rest import Client


account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
my_twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
test_text = "This is a test.  This is only a test."

client = Client(account_sid, auth_token)

client.messages.create(to="+17706341811",
                       from_=my_twilio_phone_number,
                       body=test_text)
