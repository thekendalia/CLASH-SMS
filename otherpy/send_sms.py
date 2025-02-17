import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("account_sid")
TWILIO_AUTH_TOKEN = os.getenv("auth_token")
TWILIO_PHONE_NUMBER = os.getenv("number")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(id, phone, username, attacks):
    message = client.messages.create(
        body=f"{username} you have {attacks} remaining in war! Only a couple hours left!",
        from_="+18667831078",
        to=f"{phone}",
    )
    print(message.body)