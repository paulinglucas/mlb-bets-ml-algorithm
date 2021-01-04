import tweepy
import logging
import json
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keys")))

from keys import TWIT_AUTH1, TWIT_AUTH2, TWIT_TOKEN1, TWIT_TOKEN2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def send_twt(msg):
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(TWIT_AUTH1, TWIT_AUTH2)
    auth.set_access_token(TWIT_TOKEN1, TWIT_TOKEN2)

    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")

    api.update_status(msg)

if __name__ == "__main__":
    send_twt("testing 123")
