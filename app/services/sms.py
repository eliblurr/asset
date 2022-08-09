from twilio.rest import Client
from config import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# print(settings.TWILIO_PHONE_NUMBER)
# change the "from_" number to your Twilio number and the "to" number
# to the phone number you signed up for Twilio with, or upgrade your
# account to send SMS to any phone number
def send_sms(body:str="Hello from Restaurant Order App!", to:str="+233543081518"):
    try:
        message = client.messages.create(to=to, from_=settings.TWILIO_PHONE_NUMBER, body=body)
        return message.sid
    except Exception as e:
        print(e)
        return False
    return True