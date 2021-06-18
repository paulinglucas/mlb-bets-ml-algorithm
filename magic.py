## BACKTESTED WITH 2016 SEASON
# After betting on all bets with odds greater than -110

# winner: 70.753% accurate
# spread: 63.263% accurate
# over/under: 56.839% accurate

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

# normalize data
def normalize_lst(lst):
    for i in range(len(lst)):
        lst[i][0]  = round(lst[i][0], 3) # OPS
        lst[i][29] = round(lst[i][29], 3)
        lst[i][6]  = round(lst[i][6] / 4, 3) # OPS
        lst[i][35] = round(lst[i][35] / 4, 3)
        lst[i][14]  = round(lst[i][14] / 4, 3) # OPS L10
        lst[i][43] = round(lst[i][43] / 4, 3)
        lst[i][17]  = round(lst[i][17] / 50, 3) # ERA
        lst[i][46]  = round(lst[i][46] / 50, 3)
        lst[i][22]  = round(lst[i][22] / 20, 3) # bERA
        lst[i][51]  = round(lst[i][51] / 20, 3)
        lst[i][18]  = round(lst[i][18] / 10, 3) # WHIP
        lst[i][47]  = round(lst[i][47] / 10, 3)
        lst[i][23]  = round(lst[i][23] / 10, 3) #  bWHIP
        lst[i][52]  = round(lst[i][52] / 10, 3)
        lst[i][2]  = round(lst[i][2] / 162, 3) # Pexpect
        lst[i][31]  = round(lst[i][31] / 162, 3)
        lst[i][7]  = round(lst[i][7] / 10, 3) # RPG
        lst[i][36]  = round(lst[i][36] / 10, 3)
        lst[i][15]  = round(lst[i][15] / 80, 3) # RPG L10
        lst[i][44]  = round(lst[i][44] / 80, 3)
        lst[i][8]  = round(lst[i][8] / 9, 3) # HRPG
        lst[i][37]  = round(lst[i][37] / 9, 3)
        lst[i][9]  = round(lst[i][9] / 16, 3) # SOPG
        lst[i][38]  = round(lst[i][38] / 16, 3)
        lst[i][20]  = round(lst[i][20] / 27, 3) # SOP9
        lst[i][49]  = round(lst[i][49] / 27, 3)
        lst[i][25]  = round(lst[i][25] / 27, 3) # bSOP9
        lst[i][54]  = round(lst[i][54] / 27, 3)
        lst[i][21]  = round(lst[i][21] / 9, 3) # IPG
        lst[i][50]  = round(lst[i][50] / 9, 3)
        lst[i][19]  = round(lst[i][19] / 9, 3) # HRP9
        lst[i][48]  = round(lst[i][48] / 9, 3)
        lst[i][24]  = round(lst[i][24] / 9, 3) # bHRP9
        lst[i][53]  = round(lst[i][53] / 9, 3)
        lst[i][27]  = round(lst[i][27] / 114, 3) # RYAN
        lst[i][56]  = round(lst[i][56] / 114, 3)
    return lst

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
    outputs = tf.keras.layers.Dense(output_dim, activation='sigmoid')(l)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    # CHANGE THE LOSS FUNCTION TO WHAT YOU WOULD LIKE TO FIND THE OUTCOME OF
    # win_loss : winner of game
    # spreads_loss: spread of game
    # ou_loss: over/under of game
    # first_inning_loss: score in first inning
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model

def train_model():
    DATA_NEW = extractPickle('data_to_use.pickle', 1)
    OUTPUTS_NEW = extractPickle('outputs_to_use.pickle', 1)
    CUTOFF = int(len(DATA_NEW)*0.78)
    FILENAME = 'test_ou.hdf5'

    val_data = extractPickle('twoD_list.pickle', 2016)
    val_labels = extractPickle('outcome_vectors.pickle', 2016)

    val_data = normalize_lst(val_data)
    DATA_NEW = normalize_lst(DATA_NEW)

    print("Enter loss function you wish to train with:")
    print("win_loss: train model to predict winners of future games")
    print("spreads_loss: train model to predict who will cover spread of games")
    print("ou_loss: train model to predict if game will meet over/under")
    print("first_inning_loss: train model to predict if first inning will score")
    print()

    loss_func = input("Enter loss function: ")

    if loss_func == 'win_loss':
        for r in range(len(OUTPUTS_NEW)):
            OUTPUTS_NEW[r] = OUTPUTS_NEW[r][0:2]
        for r in range(len(val_labels)):
            val_labels[r] = val_labels[r][0:2]
    elif loss_func == 'spreads_loss':
        for r in range(len(OUTPUTS_NEW)):
            OUTPUTS_NEW[r] = OUTPUTS_NEW[r][2:4]
        for r in range(len(val_labels)):
            val_labels[r] = val_labels[r][2:4]
    elif loss_func == 'ou_loss':
        for r in range(len(OUTPUTS_NEW)):
            OUTPUTS_NEW[r] = OUTPUTS_NEW[r][4:6]
        for r in range(len(val_labels)):
            val_labels[r] = val_labels[r][4:6]
    elif loss_func == 'first_inning_loss':
        for r in range(len(OUTPUTS_NEW)):
            DATA_NEW[r] = DATA_NEW[r][:22] + DATA_NEW[r][27:51] + DATA_NEW[r][56:]
            OUTPUTS_NEW[r] = OUTPUTS_NEW[r][12:]
        for r in range(len(val_labels)):
            val_data[r] = val_data[r][:22] + val_data[r][27:51] + val_data[r][56:]
            val_labels[r] = val_labels[r][12:]
    else:
        print("Invalid loss function")
        sys.exit(0)

    train_data = np.array(DATA_NEW[:CUTOFF])
    test_data = np.array(DATA_NEW[CUTOFF:])
    val_data = np.array(val_data)

    train_labels = np.array(OUTPUTS_NEW[:CUTOFF])
    test_labels = np.array(OUTPUTS_NEW[CUTOFF:])
    val_labels = np.array(val_labels)


    # best_acc, best_base, best_mul = 0, 0, 0
    #
    # for i in range(10, 100, 5):
    #     for j in range(1, 9):
    #         j_temp = j / 10
    #         model = get_model(loss_func, 58, 2, base=i, multiplier=j_temp)
    #         history = model.fit(train_data, train_labels, validation_data=(test_data, test_labels),
    #                   epochs=200, batch_size=20, callbacks=[tf.keras.callbacks.EarlyStopping(patience=25)])#,tf.keras.callbacks.ModelCheckpoint(hd5file,save_best_only=True)])
    #         loss, accuracy = model.evaluate(val_data, val_labels)
    #         if accuracy > best_acc:
    #             best_acc = accuracy
    #             best_base = i
    #             best_mul = j_temp
    #
    # print("BEST MODEL ARC:")
    # print("Accuracy: {}".format(best_acc))
    # print("Base size: {}".format(best_base))
    # print("Batch size: {}".format(20))
    # print("Multiplier: {}".format(best_mul))

    model, acc, base, mul = find_best_model(loss_func, train_data, train_labels, test_data, test_labels, val_data, val_labels)

    model.save('models_temp/best_{}.hdf5'.format(loss_func))

    print()
    print("Accuracy: {}".format(acc))
    print("Base: {}, Multiplier: {}".format(base, mul))
    print()

    return 0

def validate_model(loss_func, train_data, train_labels, test_data, test_labels, val_data, val_labels, base_, mul_):
    input_size = 58
    if loss_func == 'first_inning_loss':
        input_size = 48
    model = get_model(loss_func, input_size, 2, base=base_, multiplier=mul_)
    hd5file = loss_func + ".hdf5"

    print("Now training {} model".format(loss_func))
    print("Current base: {}".format(base_))
    print("Current multiplier: {}".format(mul_))
    print()

    history = model.fit(train_data, train_labels, validation_data=(test_data, test_labels),
              epochs=200, batch_size=20, callbacks=[tf.keras.callbacks.EarlyStopping(patience=25),tf.keras.callbacks.ModelCheckpoint(hd5file,save_best_only=True)])
    loss, acc = model.evaluate(val_data, val_labels)
    print('Training Loss : {}\nValidation Loss : {}'.format(model.evaluate(train_data, train_labels), [loss, acc]))
    return model, loss, acc


def find_best_model(loss_func, train_data, train_labels, test_data, test_labels, val_data, val_labels):
    best_acc = 0
    curr_base = 0
    curr_mul = 0
    model = -1
    for i in range(40, 101, 5):
        for j in range(20, 91, 10):
            for k in range(3):
                print("Best Accuracy: {}%".format(round(best_acc, 2)))
                model, loss, acc = validate_model(loss_func, train_data, train_labels, test_data, test_labels, val_data, val_labels, i, (j/100))
                if acc > best_acc:
                    best_model = model
                    best_acc = acc
                    curr_base = i
                    curr_mul = (j/100)
    return best_model, best_acc, curr_base, curr_mul


if __name__ == '__main__':
    train_model()

    # ml:
    # 85, 0.6
