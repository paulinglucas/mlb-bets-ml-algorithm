# winner: 58-63% accurate
# spread: 50-58% accurate
# over/under: 55-64% accurate

# DIVIDE FOR NORMALIZATION:
# OPS: 4
# ERA: 20
# WHIP: 10
# Pexpect: 162
# RPG, SOPG: 5
# SOp9: 20
# IPG: 9
# HRp9: 3
# ryan: 114

# away = :29
# home = 29:

# 3 team stats, 8 batting stats, 5 last 10 stats, 13 pitching stats
from __future__ import absolute_import, division, print_function, unicode_literals

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "data_creation")))

import tensorflow as tf
from tensorflow import keras
from gatherPlayers import extractPickle
import numpy as np

DATA_NEW = extractPickle('data_to_use.pickle', 1)
OUTPUTS_NEW = extractPickle('outputs_to_use.pickle', 1)
CUTOFF = int(len(DATA_NEW)*0.78)
FILENAME = 'ou.h5'

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

# DATA_NEW = extractPickle('twoD_list.pickle', 2015)
# OUTPUTS_NEW = extractPickle('outcome_vectors.pickle', 2015)
# CUTOFF = 2000

# not mine, off website
# currently unused, sigmoid function returns awfully confident values that render betting on confidence value useless
def odds_loss(y_true, y_pred):
    """
    The function implements the custom loss function

    Inputs
    true : a vector of dimension batch_size, 7. A label encoded version of the output and the backp1_a and backp1_b
    pred : a vector of probabilities of dimension batch_size , 5.

    Returns
    the loss value
    """
    win_away_team = y_true[:, 0:1]
    win_home_team = y_true[:, 1:2]
    away_spread = y_true[:, 2:3]
    home_spread = y_true[:, 3:4]
    over = y_true[:, 4:5]
    under = y_true[:, 5:6]
    odds_a = y_true[:, 6:7]
    odds_h = y_true[:, 7:8]
    odds_a_s = y_true[:, 8:9]
    odds_h_s = y_true[:, 9:10]
    odds_o = y_true[:, 10:11]
    odds_u = y_true[:, 11:12]
    gain_loss_vector = tf.keras.backend.concatenate([win_away_team * (odds_a - 1) + (1 - win_away_team) * -1,
      win_home_team * (odds_h - 1) + (1 - win_home_team) * -1,
      away_spread * (odds_a_s - 1) + (1 - away_spread) * -1,
      home_spread * (odds_h_s - 1) + (1 - home_spread) * -1,
      over * (odds_o - 1) + (1 - over) * -1,
      under * (odds_u - 1) + (1 - under) * -1], axis=1)
    return -1 * tf.keras.backend.mean(tf.keras.backend.sum(gain_loss_vector * y_pred, axis=1))

# Loss function for moneyline bets
def win_loss(y_true, y_pred):
    win_away_team = y_true[:, 0:1]
    win_home_team = y_true[:, 1:2]
    odds_a = y_true[:, 6:7]
    odds_h = y_true[:, 7:8]
    gain_loss_vector = tf.keras.backend.concatenate([
        win_away_team * (odds_a - 1) + (1 - win_away_team) * -1, # *
        win_home_team * (odds_h - 1) + (1 - win_home_team) * -1], # *
    axis=1)
    return -1 * tf.keras.backend.mean(tf.keras.backend.sum(gain_loss_vector * y_pred, axis=1))

# Loss function for spreads bets
def spreads_loss(y_true, y_pred):
    win_away_team = y_true[:, 2:3]
    win_home_team = y_true[:, 3:4]
    odds_a = y_true[:, 8:9]
    odds_h = y_true[:, 9:10]
    gain_loss_vector = tf.keras.backend.concatenate([
        win_away_team * (odds_a - 1) + (1 - win_away_team) * -1,
        win_home_team * (odds_h - 1) + (1 - win_home_team) * -1],
    axis=1)
    return -1 * tf.keras.backend.mean(tf.keras.backend.sum(gain_loss_vector * y_pred, axis=1))

# Loss function for over/under bets
def ou_loss(y_true, y_pred):
    win_away_team = y_true[:, 4:5]
    win_home_team = y_true[:, 5:6]
    odds_a = y_true[:, 10:11]
    odds_h = y_true[:, 11:12]
    gain_loss_vector = tf.keras.backend.concatenate([
        win_away_team * (odds_a - 1) + (1 - win_away_team) * -1,
        win_home_team * (odds_h - 1) + (1 - win_home_team) * -1],
    axis=1)
    return -1 * tf.keras.backend.mean(tf.keras.backend.sum(gain_loss_vector * y_pred, axis=1))

def loss_accuracy(y_true, y_pred):
    # ML : 0:1, 1:2
    # SPREAD : 2:3, 3:4
    # OU : 4:5, 5:6
    win_away_team = y_true[:, 0:1]
    win_home_team = y_true[:, 1:2]
    gain_loss_vector = tf.keras.backend.concatenate([
        win_away_team,
        win_home_team],
    axis=1)
    return -1 * tf.keras.backend.mean(tf.keras.backend.sum(gain_loss_vector * y_pred, axis=1))

def get_model(loss_func, input_dim, output_dim, base=1000, multiplier=0.25, p=0.2):
    inputs = tf.keras.Input(shape=(input_dim,))
    l = tf.keras.layers.BatchNormalization()(inputs)
    l = tf.keras.layers.Dropout(p)(l)
    n = base
    l = tf.keras.layers.Dense(n, activation='relu')(l)
    l = tf.keras.layers.BatchNormalization()(l)
    l = tf.keras.layers.Dropout(p)(l)
    n = int(n * multiplier)
    l = tf.keras.layers.Dense(n, activation='relu')(l)
    l = tf.keras.layers.BatchNormalization()(l)
    l = tf.keras.layers.Dropout(p)(l)
    n = int(n * multiplier)
    l = tf.keras.layers.Dense(n, activation='relu')(l)
    outputs = tf.keras.layers.Dense(output_dim, activation='softmax')(l)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    # CHANGE THE LOSS FUNCTION TO WHAT YOU WOULD LIKE TO FIND THE OUTCOME OF
    # win_loss : winner of game
    # spreads_loss: spread of game
    # ou_loss: over/under of game
    model.compile(optimizer='Nadam', loss='binary_crossentropy', metrics=['accuracy'])

    return model

def train_model():

    print("Enter loss function you wish to train with:")
    print("win_loss: train model to predict winners of future games")
    print("spreads_loss: train model to predict who will cover spread of games")
    print("ou_loss: train model to predict if game will meet over/under")
    print()

    loss_func = input("Enter loss function: ")

    if loss_func == 'win_loss':
        for r in range(len(OUTPUTS_NEW)):
            OUTPUTS_NEW[r] = OUTPUTS_NEW[r][0:2]
    elif loss_func == 'spreads_loss':
        for r in range(len(OUTPUTS_NEW)):
            OUTPUTS_NEW[r] = OUTPUTS_NEW[r][2:4]
    elif loss_func == 'ou_loss':
        for r in range(len(OUTPUTS_NEW)):
            OUTPUTS_NEW[r] = OUTPUTS_NEW[r][4:6]
    else:
        print("Invalid loss function")
        sys.exit(0)

    train_data = DATA_NEW[:CUTOFF]
    test_data = DATA_NEW[CUTOFF:]
    train_labels = OUTPUTS_NEW[:CUTOFF]
    test_labels = OUTPUTS_NEW[CUTOFF:]

    model = get_model(loss_func, 58, 2, base=50, multiplier=0.6)
    hd5file = loss_func + ".hdf5"
    history = model.fit(train_data, train_labels, validation_data=(test_data, test_labels),
              epochs=200, batch_size=100, callbacks=[tf.keras.callbacks.EarlyStopping(patience=25),tf.keras.callbacks.ModelCheckpoint(hd5file,save_best_only=True)])
    print('Training Loss : {}\nValidation Loss : {}'.format(model.evaluate(train_data, train_labels), model.evaluate(test_data, test_labels)))

    model.save('models/' + FILENAME)

if __name__ == '__main__':
    train_model()
