import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_creation")))

import gatherPlayers as p
import getGamepks as g
import statsapi as mlb
from gameStats import GameStats
from createUsableList import ListCreator
import numpy as np

# 448650 fails in boxscore
def main():
    DATA2 = p.extractPickle("twoD_list.pickle", 2014)
    DATA3 = p.extractPickle("twoD_list.pickle", 2015)
    DATA4 = p.extractPickle("twoD_list.pickle", 2017)
    DATA5 = p.extractPickle("twoD_list.pickle", 2018)
    DATA = p.extractPickle("twoD_list.pickle", 2019)
    O2 = p.extractPickle("outcome_vectors.pickle", 2014)
    O3 = p.extractPickle("outcome_vectors.pickle", 2015)
    O4 = p.extractPickle("outcome_vectors.pickle", 2017)
    O5 = p.extractPickle("outcome_vectors.pickle", 2018)
    O = p.extractPickle("outcome_vectors.pickle", 2019)

    DATA_NEW = []
    OUTPUTS_NEW = []

    DATA_NEW += DATA2[100:] + DATA3[100:] + DATA4[100:] + DATA5[100:] + DATA[100:]
    OUTPUTS_NEW += O2[100:] + O3[100:] + O4[100:] + O5[100:] + O[100:]

    home_wins = 0
    away_wins = 0
    home_spreads = 0
    away_spreads = 0
    overs = 0
    unders = 0
    for i in OUTPUTS_NEW:
        home_wins += i[1]
        away_wins += i[0]
        home_spreads += i[3]
        away_spreads += i[2]
        overs += i[4]
        unders += i[5]

    total = len(OUTPUTS_NEW)
    print("HOME %: {}".format(home_wins / total))
    print("AWAY %: {}".format(away_wins / total))
    print("HOME SPREAD %: {}".format(home_spreads / total))
    print("AWAY SPREAD %: {}".format(away_spreads / total))
    print("OVER %: {}".format(overs / total))
    print("UNDER %: {}".format(unders / total))


if __name__ == '__main__':
    main()
