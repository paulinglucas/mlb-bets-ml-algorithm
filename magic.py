
# winner: 58-63% accurate
# spread: 50-58% accurate
# over/under: 55-64% accurate



from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
from tensorflow import keras
import gatherPlayers as p
import numpy as np

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
      under * (odds_u - 1) + (1 - under) * -1,], axis=1)
    return -1 * tf.keras.backend.mean(tf.keras.backend.sum(gain_loss_vector * y_pred, axis=1))

DATA = p.extractPickle("twoD_list.pickle", 2019)
OUTPUTS = p.extractPickle("outcome_vectors.pickle", 2019)

train_data = DATA[:2000]
test_data = DATA[2000:]
train_labels = OUTPUTS[:2000]
test_labels = OUTPUTS[2000:]

def get_model(input_dim, output_dim, base=1000, multiplier=0.25, p=0.2):
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
    model.compile(optimizer='Nadam', loss=odds_loss)
    return model

model = get_model(40, 6, 2000)

history = model.fit(train_data, train_labels, validation_data=(test_data, test_labels),
          epochs=200, batch_size=5, callbacks=[tf.keras.callbacks.EarlyStopping(patience=25),tf.keras.callbacks.ModelCheckpoint('odds_loss.hdf5',save_best_only=True)])
print('Training Loss : {}\nValidation Loss : {}'.format(model.evaluate(train_data, train_labels), model.evaluate(test_data, test_labels)))

# model = tf.keras.models.Sequential([
#   tf.keras.layers.Dense(40),
#   tf.keras.layers.Dense(10, activation='relu'),
#   tf.keras.layers.Dense(2, activation='softmax'),
# ])
#
# model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
#
# model.fit(train_data, train_labels, epochs=8)
#
# test_loss, test_acc = model.evaluate(test_data, test_labels)
#
# probability_model = tf.keras.Sequential([model,
#                                          tf.keras.layers.Softmax()])
# predictions = model.predict(test_data)
