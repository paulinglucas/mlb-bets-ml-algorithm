from backtesting import Backtest
import os
import time

def main():
    dic = {}
    os.system('clear')
    for i in range(-150, -800, -50):
        print("BACKTESTING VALUE {}".format(i))
        bets, prof_margin = Backtest(i, 20, wantScreen=False).test()
        dic[i] = (bets, prof_margin)

    for k in dic:
        print(str(k) + ": ")
        print("    Bets made: {}".format(dic[k][0]))
        print("    Profit Margin: {}%".format(round(dic[k][1], 3)))

if __name__ == '__main__':
    main()
