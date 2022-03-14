from config import VAPID_PRIVATE_KEY, VAPID_CLAIMS
from pywebpush import webpush, WebPushException

def send_web_push(subscription_info, message_body):
    return webpush(
        subscription_info=subscription_info,
        data=message_body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )


'''Generate the VAPIDs via following command:

openssl ecparam -name prime256v1 -genkey -noout -out vapid_private.pem
Create base64 encoded DER representation of the keys

openssl ec -in ./vapid_private.pem -outform DER|tail -c +8|head -c 32|base64|tr -d '=' |tr '/+' '_-' >> private_key.txt

openssl ec -in ./vapid_private.pem -pubout -outform DER|tail -c 65|base64|tr -d '=' |tr '/+' '_-' >> public_key.txt
These VAPIDs keys will be used in the newly developed backend service.'''