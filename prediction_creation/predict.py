# winner: 58-63% accurate
# spread: 50-58% accurate
# over/under: 55-64% accurate
from __future__ import absolute_import, division, print_function, unicode_literals
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_creation")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keys")))

import tensorflow as tf
import twilio
from magic import win_loss, spreads_loss, ou_loss, loss_accuracy
from tensorflow import keras
import numpy as np
from createPrediction import Predictor
import statsapi as mlb
import send_sms
import populate_sheet
import requests
from getGamepks import teams_id

from datetime import date as d
from datetime import timedelta

#from send_tweet import send_twt
from send_to_discord import send_message_to_discord
from send_to_discord import send_underdogs_to_discord

CONFIDENCE_VALUE = -10000
TEXT_CONFIDENCE = -200
DISCORD_CONFIDENCE = -250
UNDERDOG_CONFIDENCE = -175

YEAR = 2021

# normalize data
def normalize_lst(lst):
    lst[0][0]  = round(lst[0][0], 3) # OPS
    lst[0][29] = round(lst[0][29], 3)
    lst[0][6]  = round(lst[0][6] / 4, 3) # OPS
    lst[0][35] = round(lst[0][35] / 4, 3)
    lst[0][14]  = round(lst[0][14] / 4, 3) # OPS L10
    lst[0][43] = round(lst[0][43] / 4, 3)
    lst[0][17]  = round(lst[0][17] / 50, 3) # ERA
    lst[0][46]  = round(lst[0][46] / 50, 3)
    lst[0][22]  = round(lst[0][22] / 20, 3) # bERA
    lst[0][51]  = round(lst[0][51] / 20, 3)
    lst[0][18]  = round(lst[0][18] / 10, 3) # WHIP
    lst[0][47]  = round(lst[0][47] / 10, 3)
    lst[0][23]  = round(lst[0][23] / 10, 3) #  bWHIP
    lst[0][52]  = round(lst[0][52] / 10, 3)
    lst[0][2]  = round(lst[0][2] / 162, 3) # Pexpect
    lst[0][31]  = round(lst[0][31] / 162, 3)
    lst[0][7]  = round(lst[0][7] / 10, 3) # RPG
    lst[0][36]  = round(lst[0][36] / 10, 3)
    lst[0][15]  = round(lst[0][15] / 80, 3) # RPG L10
    lst[0][44]  = round(lst[0][44] / 80, 3)
    lst[0][8]  = round(lst[0][8] / 9, 3) # HRPG
    lst[0][37]  = round(lst[0][37] / 9, 3)
    lst[0][9]  = round(lst[0][9] / 16, 3) # SOPG
    lst[0][38]  = round(lst[0][38] / 16, 3)
    lst[0][20]  = round(lst[0][20] / 27, 3) # SOP9
    lst[0][49]  = round(lst[0][49] / 27, 3)
    lst[0][25]  = round(lst[0][25] / 27, 3) # bSOP9
    lst[0][54]  = round(lst[0][54] / 27, 3)
    lst[0][21]  = round(lst[0][21] / 9, 3) # IPG
    lst[0][50]  = round(lst[0][50] / 9, 3)
    lst[0][19]  = round(lst[0][19] / 9, 3) # HRP9
    lst[0][48]  = round(lst[0][48] / 9, 3)
    lst[0][24]  = round(lst[0][24] / 9, 3) # bHRP9
    lst[0][53]  = round(lst[0][53] / 9, 3)
    lst[0][27]  = round(lst[0][27] / 114, 3) # RYAN
    lst[0][56]  = round(lst[0][56] / 114, 3)

    return lst

# want sigmoid to give us american odds for confidence values
def convertPercentToOdds(percent):
    percent = percent*100
    if percent == 100:
        return -10000
    if percent > 50:
        return int(round((percent / (1 - (percent/100))) * -1))
    if percent == 50:
        return 100
    else:
        return -1

# make prediction in user-readable format
def parsePrediction(predict):
    away = convertPercentToOdds(predict[0][0])
    home = convertPercentToOdds(predict[0][1])
    if away == -1:
        away = "___"
    if home == -1:
        home = "___"
    return str(away) + "," + str(home)

def hasUnderdogValue(teams, market, prediction):
    prediction = prediction.strip().split(",")

    if prediction[0] != '___':
        prediction = [0, int(prediction[0])]
    else:
        prediction = [1, int(prediction[1])]

    if int(prediction[1]) > UNDERDOG_CONFIDENCE:
        return False

    if prediction[0] == 0: tm = 0
    else: tm = 1

    ## moneyline
    if market == 'h2h':
        queries = populate_sheet.extractMarket('h2h')
        if queries['success'] == False:
            return False
        oddsQuery, inverted = populate_sheet.returnCorrectGame(queries['data'], teams)
        if oddsQuery == False:
            print('No odds found for underdog')
            send_sms.send_confirmation("Unable to find moneyline odds for {} vs {}".format(teams[0], teams[1]))
            return False

        ml_odds = oddsQuery['h2h']
        if inverted:
            tm = not tm

        ml_odds = ml_odds[tm]
        if ml_odds == 'EVEN':
            ml_odds = 100
        else:
            ml_odds = int(ml_odds)
        if ml_odds > 0 and prediction[1] < UNDERDOG_CONFIDENCE:
            return True

    ## spread
    if market == 'spreads':
        queries = populate_sheet.extractMarket('spreads')
        if queries['success'] == False:
            return False
        oddsQuery, inverted = populate_sheet.returnCorrectGame(queries['data'], teams)
        if oddsQuery == False:
            print('No odds found for underdog')
            send_sms.send_confirmation("Unable to find spread odds for {} vs {}".format(teams[0], teams[1]))
            return False

        spread_odds = oddsQuery['spreads']['odds']
        if inverted:
            tm = not tm

        spread_odds = spread_odds[tm]
        if spread_odds == 'EVEN':
            spread_odds = 100
        else:
            spread_odds = int(spread_odds)
        if spread_odds > 0 and prediction[1] < UNDERDOG_CONFIDENCE:
            return True
    return False


# is prediction above our confidence threshold?
def checkIfConfident(pred, txtOrDis):
    if txtOrDis == 'Text':
        CONFIDENCE_VALUE = TEXT_CONFIDENCE
    elif txtOrDis == 'Discord':
        CONFIDENCE_VALUE = DISCORD_CONFIDENCE
    pred = pred.strip().split(",")
    if pred[0] != "___":
        if int(pred[0]) < CONFIDENCE_VALUE:
            return True
    elif pred[1] != "___":
        if int(pred[1]) < CONFIDENCE_VALUE:
            return True
    return False

## print predictions to console, send text for confident values
def main(send_text=False, send_discord=False):
                                        #models/ml.h5
    ml_model = tf.keras.models.load_model('models/win_loss.hdf5', custom_objects={'win_loss': win_loss})
    spread_model = tf.keras.models.load_model('models/spreads_loss.hdf5', custom_objects={'spreads_loss': spreads_loss})
    ou_model = tf.keras.models.load_model('models/ou_loss.hdf5', custom_objects={'ou_loss': ou_loss})

    print()
    print()

    # for texted games
    with open('team_gameData/{}/TextedGames.txt'.format(YEAR), 'r+') as f:
        texted_games = f.read().split('\n')
        txt_buf = ''
        discord_dict = {'ml': {}, 'spread': {}, 'ou': {}}
        underdog_dict = {'ml': {}, 'spread': {}}

        day = d.today() # - timedelta(days=1)
        dt = day.strftime('%Y-%m-%d')

        ## handle connection errors
        gm = None
        for x in range(4):
            try:
                gm = mlb.schedule(date=dt)
                break
            except requests.exceptions.ConnectionError:
                print("Connection Error for schedule")
                time.sleep(10)
                continue
        if not gm:
            print("Connection Errors. Program Exiting")
            send_sms.send_confirmation("Failed to update data")
            sys.exit(-1)

        print("PREDICTIONS FOR DATE {}".format(dt))
        print()
        print()

        for g in gm:
            pred = Predictor(YEAR)
            home = teams_id[g['home_id']]
            away = teams_id[g['away_id']]

            lst = [pred.inputGameStats(g)]
            if lst == [-1]: continue
            lst = normalize_lst(lst)

            lst = np.array(lst)
            lst = lst.reshape(1,-1)

            # print(g['game_id'])
            # print(lst)

            print("PREDICTIONS (ML, SPREAD, O/U)")
            print("[P(away), P(home)]:    ", end='')
            ml_out = parsePrediction(ml_model.predict(lst))
            print(str(ml_out))
            print("[P(away), P(home)]:    ", end='')
            spread_out = parsePrediction(spread_model.predict(lst))
            print(spread_out)
            print("[P(over), P(under)]:    ", end='')
            ou_out = parsePrediction(ou_model.predict(lst))
            print(ou_out)
            print()

            ## text to me
            ml_confident = checkIfConfident(ml_out, "Text")
            spread_confident = checkIfConfident(spread_out, "Text")
            ou_confident = checkIfConfident(ou_out, "Text")

            ## discord API
            ml_confident_discord = checkIfConfident(ml_out, "Discord")
            spread_confident_discord = checkIfConfident(spread_out, "Discord")
            ou_confident_discord = checkIfConfident(ou_out, "Discord")

            ## underdog value?
            spread_underdog = None
            for x in range(4):
                try:
                    ## saves on requests
                    if str(g['game_id']) not in texted_games:
                        ml_underdog = hasUnderdogValue([away, home], 'h2h', ml_out)
                        spread_underdog = hasUnderdogValue([away, home], 'spreads', spread_out)
                    else:
                        ml_underdog = False
                        spread_underdog = False
                    break
                except requests.exceptions.ConnectionError:
                    print("Connection Error for looking up odds to predict")
                    time.sleep(10)
                    continue
            if spread_underdog == None:
                print("Connection Errors. Program Exiting")
                send_sms.send_confirmation("Failed to update underdogs")
                sys.exit(-1)

            under_dog_ml = False
            under_dog_spread = False

            ## for underdog discord API
            if str(g['game_id']) not in texted_games and send_discord and (ml_underdog or spread_underdog):
                dic_key = away + " vs " + home
                if ml_underdog:
                    underdog_dict['ml'][dic_key] = str(ml_out)
                    under_dog_ml = True
                if spread_underdog:
                    underdog_dict['spread'][dic_key] = str(spread_out)
                    under_dog_spread = True

            ## only send text if odds are greater than 77% chance either way
            if str(g['game_id']) not in texted_games and send_text and (ml_confident or spread_confident or ou_confident or ml_underdog or spread_underdog):
                txt_buf += away + " vs " + home + '\n'
                if ml_confident or ml_underdog:
                    txt_buf += "ml: " + str(ml_out) + '\n'
                if spread_confident or spread_underdog:
                    txt_buf += "spr: " + str(spread_out) + '\n'
                if ou_confident:
                    txt_buf += "o/u: " + str(ou_out) + '\n'
                txt_buf += '\n'

            ## for discord API
            if str(g['game_id']) not in texted_games and send_discord and (ml_confident_discord or spread_confident_discord or ou_confident_discord):
                dic_key = away + " vs " + home
                if ml_confident_discord and not under_dog_ml:
                    discord_dict['ml'][dic_key] = str(ml_out)
                if spread_confident_discord and not under_dog_spread:
                    discord_dict['spread'][dic_key] = str(spread_out)
                if ou_confident_discord:
                    discord_dict['ou'][dic_key] = str(ou_out)

            ## write to texted games so predictions dont come in after game starts
            f.write(str(g['game_id']) + '\n')

        if send_text:
            try:
                send_sms.send_pred(txt_buf.strip())
                if send_discord:
                    send_message_to_discord(discord_dict)
                    send_underdogs_to_discord(underdog_dict)

                success = None
                for x in range(4):
                    try:
                        success = populate_sheet.updateSpreadsheets(TEXT_CONFIDENCE, DISCORD_CONFIDENCE, UNDERDOG_CONFIDENCE, txt_buf, underdog_dict)
                        break
                    except requests.exceptions.ConnectionError:
                        print("Connection Error for updating spreadsheet")
                        time.sleep(10)
                        continue
                if not success:
                    print("Connection Errors. Program Exiting")
                    send_sms.send_confirmation("Failed to update spreadsheet")
                    sys.exit(-1)

            except twilio.base.exceptions.TwilioRestException:
                print("No odds big enough to send text via Twilio")

if __name__ == "__main__":
    main(send_text=True, send_discord=True)

# new_model.summary()
