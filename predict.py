# winner: 58-63% accurate
# spread: 50-58% accurate
# over/under: 55-64% accurate

from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
from magic import win_loss, spreads_loss, ou_loss
from tensorflow import keras
import numpy as np
from createPrediction import Predictor
import statsapi as mlb

from datetime import date as d
#from datetime import timedelta

def main():
                                        #models/ml.h5
    ml_model = tf.keras.models.load_model('models/win_loss.hdf5', custom_objects={'win_loss': win_loss})
    spread_model = tf.keras.models.load_model('models/spread.h5', custom_objects={'spreads_loss': spreads_loss})
    ou_model = tf.keras.models.load_model('models/ou.h5', custom_objects={'ou_loss': ou_loss})

    print()
    print()

    gmpks = []
    day = d.today()
    dt = day.strftime('%Y-%m-%d')
    gm = mlb.schedule(date=dt)

    for g in gm:
        gmpks.append(g)

    for g in gmpks:
        pred = Predictor(2020)
        lst = [pred.inputGameStats(g)]
        if lst == [-1]: continue

        print("PREDICTIONS (ML, SPREAD, O/U)")
        print("[P(away), P(home)]:    ", end='')
        print(ml_model.predict(lst))
        print("[P(away), P(home)]:    ", end='')
        print(spread_model.predict(lst))
        print("[P(over), P(under)]:    ", end='')
        print(ou_model.predict(lst))
        print()

if __name__ == "__main__":
    main()

# new_model.summary()
