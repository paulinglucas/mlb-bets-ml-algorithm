# winner: 58-63% accurate
# spread: 50-58% accurate
# over/under: 55-64% accurate
from __future__ import absolute_import, division, print_function, unicode_literals
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_creation")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tensorflow as tf
import twilio
from magic import win_loss, spreads_loss, ou_loss, loss_accuracy
from tensorflow import keras
import numpy as np
from createPrediction import Predictor
import statsapi as mlb
import send_sms
from getGamepks import teams_id

from datetime import date as d
from datetime import timedelta

from send_tweet import send_twt

CONFIDENCE_VALUE = -10000
TEXT_CONFIDENCE = -150
TWEET_CONFIDENCE = -300

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
        away = "---"
    if home == -1:
        home = "---"
    return str(away) + "," + str(home)

# is prediction above our confidence threshold?
def checkIfConfident(pred, txtOrTwt):
    if txtOrTwt == 'Text':
        CONFIDENCE_VALUE = TEXT_CONFIDENCE
    elif txtOrTwt == 'Tweet':
        CONFIDENCE_VALUE = TWEET_CONFIDENCE
    pred = pred.strip().split(",")
    if pred[0] != "---":
        if int(pred[0]) < CONFIDENCE_VALUE:
            return True
    elif pred[1] != "---":
        if int(pred[1]) < CONFIDENCE_VALUE:
            return True
    return False

## print predictions to console, send text for confident values
def main(send_text=False, send_twt=False):
                                        #models/ml.h5
    ml_model = tf.keras.models.load_model('models/win_loss.hdf5', custom_objects={'win_loss': win_loss})
    spread_model = tf.keras.models.load_model('models/spreads_loss.hdf5', custom_objects={'spreads_loss': spreads_loss})
    ou_model = tf.keras.models.load_model('models/ou_loss.hdf5', custom_objects={'ou_loss': ou_loss})

    print()
    print()

    # for texted games
    with open('team_gameData/2020/TextedGames.txt', 'r+') as f:
        texted_games = f.read().split('\n')
        txt_buf = ''

        day = d.today() #- timedelta(days=1)
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
            pred = Predictor(2020)
            lst = [pred.inputGameStats(g)]
            if lst == [-1]: continue
            lst = normalize_lst(lst)

            lst = np.array(lst)
            lst = lst.reshape(1,-1)

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

            ## twitter API
            ml_confident_tweet = checkIfConfident(ml_out, "Tweet")
            spread_confident_tweet = checkIfConfident(spread_out, "Tweet")
            ou_confident_tweet = checkIfConfident(ou_out, "Tweet")

            ## only send text if odds are greater than 77% chance either way
            if str(g['game_id']) not in texted_games and send_text and (ml_confident or spread_confident or ou_confident):
                f.write(str(g['game_id']) + '\n')
                home = teams_id[g['home_id']]
                away = teams_id[g['away_id']]
                txt_buf += away + " vs " + home + '\n'
                if ml_confident:
                    txt_buf += "ml: " + str(ml_out) + '\n'
                if spread_confident:
                    txt_buf += "spr: " + str(spread_out) + '\n'
                if ou_confident:
                    txt_buf += "o/u: " + str(ou_out) + '\n\n'

            ## for twitter API
            if str(g['game_id']) not in texted_games and send_twt and (ml_confident_tweet or spread_confident_tweet or ou_confident_tweet):
                f.write(str(g['game_id']) + '\n')
                twt_buf = ""
                home = teams_id[g['home_id']]
                away = teams_id[g['away_id']]
                twt_buf += away + " vs " + home + '\n'
                if ml_confident:
                    twt_buf += "ml: " + str(ml_out) + '\n'
                if spread_confident:
                    twt_buf += "spr: " + str(spread_out) + '\n'
                if ou_confident:
                    twt_buf += "o/u: " + str(ou_out) + '\n\n'
                send_twt(txt_buf)


        if send_text:
            try:
                send_sms.send_pred(txt_buf)
            except twilio.base.exceptions.TwilioRestException:
                print("No odds big enough to send text via Twilio")

if __name__ == "__main__":
    main(send_text=True, send_twt=True)

# new_model.summary()
