from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'AC6d8fe4ab5ffdfd3cfde77fa962e9e53f'
auth_token = '0e136b3da6aeeacc41bbe63fa508dfc3'

def send_sms(msg):
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body=msg,
                         from_='+13126817793',
                         to='+19202059889'
                     )
