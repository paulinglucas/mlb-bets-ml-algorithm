from __future__ import absolute_import, division, print_function, unicode_literals

import sys, os
import curses
import time
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_creation")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tensorflow as tf
from tensorflow import keras
from gatherPlayers import extractPickle
import numpy as np
from magic import win_loss, spreads_loss, ou_loss, loss_accuracy

class Backtest:
    def __init__(self, confidence, amount_per_bet, double_yes, wantScreen):
        self.LIST = extractPickle('twoD_list.pickle', 2021)[150:]
        self.OUTCOMES = extractPickle('outcome_vectors.pickle', 2021)[150:]
        self.ml_model = tf.keras.models.load_model('past_models/win_loss.hdf5')
        self.spread_model = tf.keras.models.load_model('past_models/spreads_loss.hdf5')
        self.ou_model = tf.keras.models.load_model('past_models/ou_loss.hdf5')
        self.confidence = self.convertOddsToPercent(confidence)
        self.amount_per_bet = amount_per_bet
        self.wantScreen = wantScreen
        self.double_val = double_yes

    # normalize data
    def normalize_lst(self, lst):
        lst[0]  = round(lst[0], 3) # OPS
        lst[29] = round(lst[29], 3)
        lst[6]  = round(lst[6] / 4, 3) # OPS
        lst[35] = round(lst[35] / 4, 3)
        lst[14]  = round(lst[14] / 4, 3) # OPS L10
        lst[43] = round(lst[43] / 4, 3)
        lst[17]  = round(lst[17] / 50, 3) # ERA
        lst[46]  = round(lst[46] / 50, 3)
        lst[22]  = round(lst[22] / 20, 3) # bERA
        lst[51]  = round(lst[51] / 20, 3)
        lst[18]  = round(lst[18] / 10, 3) # WHIP
        lst[47]  = round(lst[47] / 10, 3)
        lst[23]  = round(lst[23] / 10, 3) #  bWHIP
        lst[52]  = round(lst[52] / 10, 3)
        lst[2]  = round(lst[2] / 162, 3) # Pexpect
        lst[31]  = round(lst[31] / 162, 3)
        lst[7]  = round(lst[7] / 10, 3) # RPG
        lst[36]  = round(lst[36] / 10, 3)
        lst[15]  = round(lst[15] / 80, 3) # RPG L10
        lst[44]  = round(lst[44] / 80, 3)
        lst[8]  = round(lst[8] / 9, 3) # HRPG
        lst[37]  = round(lst[37] / 9, 3)
        lst[9]  = round(lst[9] / 16, 3) # SOPG
        lst[38]  = round(lst[38] / 16, 3)
        lst[20]  = round(lst[20] / 27, 3) # SOP9
        lst[49]  = round(lst[49] / 27, 3)
        lst[25]  = round(lst[25] / 27, 3) # bSOP9
        lst[54]  = round(lst[54] / 27, 3)
        lst[21]  = round(lst[21] / 9, 3) # IPG
        lst[50]  = round(lst[50] / 9, 3)
        lst[19]  = round(lst[19] / 9, 3) # HRP9
        lst[48]  = round(lst[48] / 9, 3)
        lst[24]  = round(lst[24] / 9, 3) # bHRP9
        lst[53]  = round(lst[53] / 9, 3)
        lst[27]  = round(lst[27] / 114, 3) # RYAN
        lst[56]  = round(lst[56] / 114, 3)
        return lst

    def convertOddsToPercent(self, odds):
        if odds > 0:
            return 100 / (odds + 100)
        if odds < 0:
            odds = -odds
            return odds / (odds + 100)
        return .5

    def test(self):
        #os.system('clear')
        ## curses initialization
        try:
            if self.wantScreen:
                stdscr = curses.initscr()
                curses.curs_set(0)
                curses.noecho()
                curses.cbreak()

            ## normalize first
            for i in range(len(self.LIST)):
                self.LIST[i] = self.normalize_lst(self.LIST[i])
                self.LIST[i][2] = 0.5
                self.LIST[i][31] = 0.5

            ## initialize all variables
            day = 0
            game_num = 0
            double_val = self.double_val

            amount_bet = 0
            amount_won = 0

            num_ml_bets = 0
            num_ml_success = 0
            ml_money = 0
            ml_winnings = 0

            num_spread_bets = 0
            num_spread_success = 0
            spread_money = 0
            spread_winnings = 0

            num_ou_bets = 0
            num_ou_success = 0
            ou_money = 0
            ou_winnings = 0

            home_bets = 0
            home_spread_bets = 0
            under_bets = 0

            ## data points for the graph
            munnies = []
            munnies_made = []


            ## ru through each game in the list, updating profits and wins accordingly
            for game, outcome in zip(self.LIST, self.OUTCOMES):
                game_num += 1
                if self.wantScreen:
                    stdscr.erase()
                    ## update days in terminal
                    if game_num % 15 == 0: day += 1
                    stdscr.addstr("DAY {}\n\n".format(day))

                ## moneyline
                ml_predict = self.ml_model.predict([game])




                if ml_predict[0][0] > self.confidence:
                    if outcome[6] >= 2:
                        home_bets += 1
                    if outcome[0] == 1:
                        num_ml_success += 1
                        ml_winnings += self.amount_per_bet*outcome[6]*double_val
                    ml_money += self.amount_per_bet*double_val
                    num_ml_bets += 1

                if ml_predict[0][1] > self.confidence:
                    if outcome[7] >= 2:
                        home_bets += 1
                    if outcome[1] == 1:
                        num_ml_success += 1
                        ml_winnings += self.amount_per_bet*outcome[7]*double_val
                    ml_money += self.amount_per_bet*double_val
                    num_ml_bets += 1

                ## spread
                spread_predict = self.spread_model.predict([game])

                if spread_predict[0][0] > self.confidence:
                    if outcome[8] >= 2:
                        home_spread_bets += 1
                    if outcome[2] == 1:
                        num_spread_success += 1
                        spread_winnings += self.amount_per_bet*outcome[8]
                    spread_money += self.amount_per_bet
                    num_spread_bets += 1

                if spread_predict[0][1] > self.confidence:
                    if outcome[9] >= 2:
                        home_spread_bets += 1
                    if outcome[3] == 1:
                        num_spread_success += 1
                        spread_winnings += self.amount_per_bet*outcome[9]
                    spread_money += self.amount_per_bet
                    num_spread_bets += 1

                ## o/u
                ou_predict = self.ou_model.predict([game])

                if ou_predict[0][0] > self.confidence:
                    if outcome[4] == 1:
                        num_ou_success += 1
                        ou_winnings += self.amount_per_bet*outcome[10]
                    ou_money += self.amount_per_bet
                    num_ou_bets += 1

                if ou_predict[0][1] > self.confidence:
                    under_bets += 1
                    if outcome[5] == 1:
                        num_ou_success += 1
                        ou_winnings += self.amount_per_bet*outcome[11]
                    ou_money += self.amount_per_bet
                    num_ou_bets += 1

                ## update totals
                total_bet = num_ml_bets + num_spread_bets + num_ou_bets
                total_won = num_ml_success + num_spread_success + num_ou_success
                amount_bet = ml_money + spread_money + ou_money
                amount_won = ml_winnings + spread_winnings + ou_winnings

                ## add data points to graph
                munnies .append(round(amount_bet,2))
                munnies_made.append(round(amount_won - amount_bet,2))

                ## add to curses screen
                if self.wantScreen:
                    try:
                        stdscr.addstr("SUCCESS RATE: {}%\n".format(round((total_won / total_bet)*100, 3)))
                    except ZeroDivisionError:
                        pass
                    stdscr.addstr("\n")
                    stdscr.addstr("BETS MADE: {}\n".format(total_bet))
                    stdscr.addstr("TOTAL BET: ${}\n".format(round(amount_bet, 2)))
                    stdscr.addstr("TOTAL WON: ${}\n".format(round(amount_won - amount_bet, 2)))
                    stdscr.addstr("\n")
                    try:
                        stdscr.addstr("ML BETS MADE: {}\n".format(num_ml_bets))
                        stdscr.addstr("ML SUCCESS RATE: {}%\n".format(round((num_ml_success / num_ml_bets)*100, 3)))
                        stdscr.addstr("ML UNDERDOG BET RATE: {}%\n".format(round((home_bets / num_ml_bets)*100, 3)))
                        stdscr.addstr("AVG WINNINGS: ${}\n".format(round((ml_winnings-(num_ml_success*self.amount_per_bet*self.double_val)) / num_ml_success, 2)))
                    except ZeroDivisionError:
                        pass
                    stdscr.addstr("ML PROFITS: ${}\n".format(round(ml_winnings - ml_money, 2)))
                    stdscr.addstr("\n")
                    try:
                        stdscr.addstr("SPREAD BETS MADE: {}\n".format(num_spread_bets))
                        stdscr.addstr("SPREAD SUCCESS RATE: {}%\n".format(round((num_spread_success / num_spread_bets)*100, 3)))
                        stdscr.addstr("-1.5 SPREAD BET RATE: {}%\n".format(round((home_spread_bets / num_spread_bets)*100, 3)))
                        stdscr.addstr("AVG WINNINGS: ${}\n".format(round((spread_winnings-(num_spread_success*self.amount_per_bet)) / num_spread_success, 2)))
                    except ZeroDivisionError:
                        pass
                    stdscr.addstr("SPREAD PROFITS: ${}\n".format(round(spread_winnings - spread_money, 2)))
                    stdscr.addstr("\n")
                    try:
                        stdscr.addstr("O/U BETS MADE: {}\n".format(num_ou_bets))
                        stdscr.addstr("O/U SUCCESS RATE: {}%\n".format(round((num_ou_success / num_ou_bets)*100, 3)))
                        stdscr.addstr("UNDER BET RATE: {}%\n".format(round((under_bets / num_ou_bets)*100, 3)))
                        stdscr.addstr("AVG WINNINGS: ${}\n".format(round((ou_winnings-(num_ou_success*self.amount_per_bet)) / num_ou_success, 2)))
                    except ZeroDivisionError:
                        pass
                    stdscr.addstr("OU PROFITS: ${}\n".format(round(ou_winnings - ou_money, 2)))
                    stdscr.addstr("\n\n")
                    stdscr.refresh()
            if self.wantScreen:
                stdscr.addstr("END BACKTEST\n")
                try:
                    stdscr.addstr("PROFIT MARGIN: {}%\n".format(round(((amount_won - amount_bet) / amount_bet)*100, 3)))
                except ZeroDivisionError:
                    pass
                stdscr.refresh()

            ##drawdown
            i = np.argmax(np.maximum.accumulate(munnies_made) - munnies_made) # end of the period
            j = np.argmax(munnies_made[:i]) # start of period

            ## plot graph
            plt.plot(munnies, munnies_made)
            plt.title('Total profit with ${} bets - 2019'.format(self.amount_per_bet))
            plt.xlabel('Amount bet\nProfit range: {}, {}\nMax Drawdown: ${}'.format(min(munnies_made), max(munnies_made), round(munnies_made[i] - munnies_made[j], 2)))
            plt.ylabel('Profit')
            plt.plot([munnies[i], munnies[j]], [munnies_made[i], munnies_made[j]], 'o', color='Red', markersize=4)

            plt.tight_layout()
            plt.show()
        except (KeyboardInterrupt, Exception):
            pass
        if self.wantScreen:
            curses.curs_set(1)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

        return total_bet, (amount_won - amount_bet) / amount_bet, amount_won - amount_bet

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("USAGE: python3 backtesting.py [CONFIDENCE_VALUE] [AMOUNT_PER_BET] [DOUBLE MONEYLINE BET (1 for no, 2 for yes)]")
        sys.exit(0)

    Backtest(int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), wantScreen=True).test()
