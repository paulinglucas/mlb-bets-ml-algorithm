# winner: 58-63% accurate
# spread: 50-58% accurate
# over/under: 55-64% accurate

from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
from magic import win_loss, spreads_loss, ou_loss
from tensorflow import keras
import numpy as np
from createPrediction import Predictor

def main():

    ml_model = tf.keras.models.load_model('models/ml.h5', custom_objects={'win_loss': win_loss})
    spread_model = tf.keras.models.load_model('models/spread.h5', custom_objects={'spreads_loss': spreads_loss})
    ou_model = tf.keras.models.load_model('models/ou.h5', custom_objects={'ou_loss': ou_loss})

    pred = Predictor(2019)
    lst = [pred.inputGameStats()]

    print("MONEYLINE PREDICTION")
    print("[P(away), P(home)]")
    print(ml_model.predict(lst))
    print()

    print("SPREAD PREDICTION")
    print("[P(away), P(home)]")
    print(spread_model.predict(lst))
    print()

    print("OU PREDICTION")
    print("[P(away), P(home)]")
    print(ou_model.predict(lst))

if __name__ == "__main__":
    main()

# new_model.summary()
