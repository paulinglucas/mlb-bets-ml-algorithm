# 3 team stats, 8 batting stats, 5 last 10 stats, 13 pitching stats
from __future__ import absolute_import, division, print_function, unicode_literals
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_creation")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keys")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from keys import ODDS_KEY

from copy import deepcopy
import gatherPlayers as p
import getGamepks as g
import statsapi as mlb
from gameStats import GameStats
from createUsableList import ListCreator
import numpy as np
import requests
from magic import win_loss, spreads_loss, ou_loss, loss_accuracy

import tensorflow as tf
from tensorflow import keras

def extractMarket(markType):
    ## extracting odds from api to add to database
    r = requests.get('https://api.the-odds-api.com/v3/odds/?sport=baseball_mlb&region=us&oddsFormat=american&mkt={1}&apiKey={0}'.format(ODDS_KEY, markType))
    queries = r.json()

    return queries

# 448650 fails in boxscore
def main():
    model = tf.keras.models.load_model('models/test_ml.h5')
    DATA_NEW = p.extractPickle('twoD_list.pickle', 2016)[150:]
    outputs = p.extractPickle('outcome_vectors.pickle', 2016)[150:]

    for i in range(len(outputs)):
        outputs[i] = outputs[i][0:2]

    # normalize data
    for i in range(len(DATA_NEW)):
        DATA_NEW[i][0]  = round(DATA_NEW[i][0], 3) # OPS
        DATA_NEW[i][29] = round(DATA_NEW[i][29], 3)
        DATA_NEW[i][6]  = round(DATA_NEW[i][6] / 4, 3) # OPS
        DATA_NEW[i][35] = round(DATA_NEW[i][35] / 4, 3)
        DATA_NEW[i][14]  = round(DATA_NEW[i][14] / 4, 3) # OPS L10
        DATA_NEW[i][43] = round(DATA_NEW[i][43] / 4, 3)
        DATA_NEW[i][17]  = round(DATA_NEW[i][17] / 50, 3) # ERA
        DATA_NEW[i][46]  = round(DATA_NEW[i][46] / 50, 3)
        DATA_NEW[i][22]  = round(DATA_NEW[i][22] / 20, 3) # bERA
        DATA_NEW[i][51]  = round(DATA_NEW[i][51] / 20, 3)
        DATA_NEW[i][18]  = round(DATA_NEW[i][18] / 10, 3) # WHIP
        DATA_NEW[i][47]  = round(DATA_NEW[i][47] / 10, 3)
        DATA_NEW[i][23]  = round(DATA_NEW[i][23] / 10, 3) #  bWHIP
        DATA_NEW[i][52]  = round(DATA_NEW[i][52] / 10, 3)
        DATA_NEW[i][2]  = round(DATA_NEW[i][2] / 162, 3) # Pexpect
        DATA_NEW[i][31]  = round(DATA_NEW[i][31] / 162, 3)
        DATA_NEW[i][7]  = round(DATA_NEW[i][7] / 10, 3) # RPG
        DATA_NEW[i][36]  = round(DATA_NEW[i][36] / 10, 3)
        DATA_NEW[i][15]  = round(DATA_NEW[i][15] / 80, 3) # RPG L10
        DATA_NEW[i][44]  = round(DATA_NEW[i][44] / 80, 3)
        DATA_NEW[i][8]  = round(DATA_NEW[i][8] / 9, 3) # HRPG
        DATA_NEW[i][37]  = round(DATA_NEW[i][37] / 9, 3)
        DATA_NEW[i][9]  = round(DATA_NEW[i][9] / 16, 3) # SOPG
        DATA_NEW[i][38]  = round(DATA_NEW[i][38] / 16, 3)
        DATA_NEW[i][20]  = round(DATA_NEW[i][20] / 27, 3) # SOP9
        DATA_NEW[i][49]  = round(DATA_NEW[i][49] / 27, 3)
        DATA_NEW[i][25]  = round(DATA_NEW[i][25] / 27, 3) # bSOP9
        DATA_NEW[i][54]  = round(DATA_NEW[i][54] / 27, 3)
        DATA_NEW[i][21]  = round(DATA_NEW[i][21] / 9, 3) # IPG
        DATA_NEW[i][50]  = round(DATA_NEW[i][50] / 9, 3)
        DATA_NEW[i][19]  = round(DATA_NEW[i][19] / 9, 3) # HRP9
        DATA_NEW[i][48]  = round(DATA_NEW[i][48] / 9, 3)
        DATA_NEW[i][24]  = round(DATA_NEW[i][24] / 9, 3) # bHRP9
        DATA_NEW[i][53]  = round(DATA_NEW[i][53] / 9, 3)
        DATA_NEW[i][27]  = round(DATA_NEW[i][27] / 114, 3) # RYAN
        DATA_NEW[i][56]  = round(DATA_NEW[i][56] / 114, 3)


    arr = []

    for i in range(int(len(DATA_NEW[0]) / 2)):
        test_data = deepcopy(DATA_NEW)
        for j in range(len(test_data)):
            test_data[j][i] = 0.0
            test_data[j][i+29] = 0.0

        results = model.evaluate(test_data, outputs, batch_size=1)
        print('INPUT {}'.format(i+1))
        print("Loss: {} ; Accuracy: {}".format(results[0], results[1]))
        print()

        arr.append(results[1])

    print("END OF EVALUATION")
    print("BIGGEST IMPACTORS")
    for i in range(len(arr)):
        print("{}:  {}".format(i+1, round(arr[i] - 0.6926, 4)))


if __name__ == '__main__':
    main()
