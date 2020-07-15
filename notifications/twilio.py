from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from decouple import config


account = config("TWILIO_ACCOUNT_SID")
token = config("TWILIO_TOKEN")


def send_message(to, body):

    client = Client(account, token)
    client.messages.create(to=to, from_="+12563650572", body=body)
    print("message sent.")
