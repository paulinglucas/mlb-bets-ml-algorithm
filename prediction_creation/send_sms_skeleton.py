from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = ''
auth_token = ''

def send_sms_skel(msg):
    client = Client(account_sid, auth_token)

    numbers = []

    for number in numbers:
        message = client.messages \
                        .create(
                             body=msg,
                             from_='',
                             to=number
                         )
