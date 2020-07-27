
# winner: 58-63% accurate
# spread: 50-58% accurate
# over/under: 55-64% accurate



from __future__ import absolute_import, division, print_function, unicode_literals
import sys

import tensorflow as tf
from tensorflow import keras
from gatherPlayers import extractPickle
import numpy as np

DATA_NEW = extractPickle('data_to_use.pickle', 1)
OUTPUTS_NEW = extractPickle('outputs_to_use.pickle', 1)
CUTOFF = 9000
FILENAME = 'ou.h5'

# DATA_NEW = extractPickle('twoD_list.pickle', 2015)
# OUTPUTS_NEW = extractPickle('outcome_vectors.pickle', 2015)
# CUTOFF = 2000

train_data = DATA_NEW[:CUTOFF]
test_data = DATA_NEW[CUTOFF:]
train_labels = OUTPUTS_NEW[:CUTOFF]
test_labels = OUTPUTS_NEW[CUTOFF:]

# not mine, off website
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
        win_away_team * (odds_a - 1) + (1 - win_away_team) * -1,
        win_home_team * (odds_h - 1) + (1 - win_home_team) * -1],
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
    win_away_team = y_true[:, 4:5]
    win_home_team = y_true[:, 5:6]
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
    if loss_func == 'win_loss':
        model.compile(optimizer='Nadam', loss=win_loss)
    elif loss_func == 'spreads_loss':
        model.compile(optimizer='Nadam', loss=spreads_loss)
    elif loss_func == 'ou_loss':
        model.compile(optimizer='Nadam', loss=ou_loss)
    else:
        print("Invalid loss function")
        sys.exit(0)

    return model

def train_model(loss_func):
    model = get_model(loss_func, 58, 2)
    hd5file = loss_func + ".hdf5"
    history = model.fit(train_data, train_labels, validation_data=(test_data, test_labels),
              epochs=200, batch_size=100, callbacks=[tf.keras.callbacks.EarlyStopping(patience=25),tf.keras.callbacks.ModelCheckpoint(hd5file,save_best_only=True)])
    print('Training Loss : {}\nValidation Loss : {}'.format(model.evaluate(train_data, train_labels), model.evaluate(test_data, test_labels)))

    # model.save('models/' + FILENAME)

print("Enter loss function you wish to train with:")
print("win_loss: train model to predict winners of future games")
print("spreads_loss: train model to predict who will cover spread of games")
print("ou_loss: train model to predict if game will meet over/under")
print()

inp = input("Enter loss function: ")

train_model(inp)
