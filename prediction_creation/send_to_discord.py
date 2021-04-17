import json
import sys, os
from discord_webhook import DiscordWebhook

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keys")))

from keys import ML_URL, SPREAD_URL, OU_URL, UNDERDOG_URL

def format_msg(msg_key, msg, ou=False):
    msg = msg.strip().split(",")
    msg_teams = msg_key.strip().split(" vs ")
    idx = 0
    if "___" == msg[0]:
        idx = 1
    bet = msg_teams[idx]
    if ou:
        bet = ['Over', 'Under'][idx]
    return "{0}:   {1} {2}".format(msg_key.upper(), bet, msg[idx])


def send_message_to_discord(msg_dict):
    ml_msg = ""
    spread_msg = ""
    ou_msg = ""
    for gm in msg_dict['ml']:
        ml_msg += "{}\n".format(format_msg(gm, msg_dict['ml'][gm]))
    webhook = DiscordWebhook(url=ML_URL, content=ml_msg.strip())
    response = webhook.execute()

    for gm in msg_dict['spread']:
        spread_msg += "{}\n".format(format_msg(gm, msg_dict['spread'][gm]))
    webhook = DiscordWebhook(url=SPREAD_URL, content=spread_msg.strip())
    response = webhook.execute()

    for gm in msg_dict['ou']:
        ou_msg += "{}\n".format(format_msg(gm, msg_dict['ou'][gm], ou=True))
    webhook = DiscordWebhook(url=OU_URL, content=ou_msg.strip())
    response = webhook.execute()


def send_underdogs_to_discord(msg_dict):
    ml_msg = "MONEYLINE UNDERDOGS\n\n"
    spread_msg = "SPREAD UNDERDOGS\n\n"
    for gm in msg_dict['ml']:
        ml_msg += "{}\n".format(format_msg(gm, msg_dict['ml'][gm]))
    if len(msg_dict['ml'].keys()) > 0:
        webhook = DiscordWebhook(url=UNDERDOG_URL, content=ml_msg)
        response = webhook.execute()

    for gm in msg_dict['spread']:
        spread_msg += "{}\n".format(format_msg(gm, msg_dict['spread'][gm]))
    if len(msg_dict['spread'].keys()) > 0:
        webhook = DiscordWebhook(url=UNDERDOG_URL, content=spread_msg)
        response = webhook.execute()


if __name__ == "__main__":
    msg_dict = {
    'ml': {
        'Twins vs Brewers': '___,-430',
        'White Sox vs Angels': '-210,___'
        },
    'spread': {
        'Giants vs Cubs': '-160,___'
        },
    'ou': {
        'Giants vs Cubs': '___,-530'
        }
    }
    send_message_to_discord(msg_dict)
