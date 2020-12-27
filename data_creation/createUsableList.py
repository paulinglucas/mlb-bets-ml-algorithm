import gatherPlayers as p
import gameStats as gm

import os
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 40 x 2425

class ListCreator:
    def __init__(self, year):
        self.year = year
        self.DATA = p.extractPickle("all_games.pickle", self.year)
        try:
            self.ODDS = p.extractPickle("all_odds.pickle", self.year)
        except FileNotFoundError:
            pass
        self.LENGTH_OF_LIST = 58
        self.LISTT = []

    # remember to add the stats into the gamepacks BEFOREHAND
    def addToList(self):
        lst = []
        # game stats
        with open("team_gameData/" + str(self.year) + "/AllGamesOnce.txt", "r") as f:
            line = f.readline()
            count = 0
            while line != "":
                count += 1
                gmpk = int(line[:6])
                listToUse = self.DATA['gmpks'][gmpk]['away'] + self.DATA['gmpks'][gmpk]['home']
                lst.append(listToUse)
                line = f.readline()
        # # Tigers/White Sox game with zero data
        # del lst[1910]
        self.LISTT = lst
        # p.addToPickle(lst, "twoD_list.pickle", self.year)
        p.addToPickle(self.LISTT, "twoD_list.pickle", self.year)

    # adds output vectors to odds dictionary to be used as labels for tensorflow
    def checkOdds(self):
        """
        Vector order as follows: [1,2,3,4,5,6]
        1. Win Away
        2. Win Home
        3. Away covered spread
        4. Home covered spread
        5. Over
        6. Under
        """

        def spread_check(output_vector, score, spread):
            awaySpread = False
            if score[2] == 'Away':
                if spread > 0:
                    output_vector[2] = 1
                    awaySpread = True
                elif spread < 0:
                    if (score[0] - score[1]) > abs(spread):
                        output_vector[2] = 1
                        awaySpread = True
            elif score[2] == 'Home' and spread > 0:
                if (score[1] - score[0]) < spread:
                    output_vector[2] = 1
                    awaySpread = True
            if not awaySpread:
                output_vector[3] = 1
            return output_vector

        with open("team_gameData/" + str(self.year) + "/AllGamesOnce.txt", "r") as f:
            outputLst = []
            output_vector = [0,0,0,0,0,0]
            line = f.readline()
            count = 0
            while line != "":
                output_vector = [0,0,0,0,0,0]
                gmpk = int(line[:6])

                if self.ODDS[gmpk] == "No odds":
                    line = f.readline()
                    del self.LISTT[count]
                    continue

                count += 1
                score = self.DATA['gmpks'][gmpk]['outcome']
                awayGameOdds = self.ODDS[gmpk]['away']
                oddsToCheck = awayGameOdds
                homeGameOdds = self.ODDS[gmpk]['home']
                output_vector = spread_check(output_vector, score, oddsToCheck[1])
                if score[2] == "Away":
                    output_vector[0] = 1
                else:
                    output_vector[1] = 1
                if (float(score[0] + score[1]) - (float(oddsToCheck[3]))) > .2:
                    output_vector[4] = 1
                elif (float(score[0] + score[1]) - float(oddsToCheck[3])) < .2:
                    output_vector[5] = 1
                # order: away, home, away spread, home spread, over, under
                odds_vector = [awayGameOdds[0], homeGameOdds[0], awayGameOdds[2], homeGameOdds[2], awayGameOdds[4], homeGameOdds[4]]
                # vector: first 6 outcome, next 6 odds
                output_vector = output_vector + odds_vector
                for i in range(12):
                    output_vector[i] = float(output_vector[i])
                outputLst.append(output_vector)
                line = f.readline()
        p.addToPickle(self.LISTT, "twoD_list.pickle", self.year)
        p.addToPickle(outputLst, "outcome_vectors.pickle", self.year)

    # gets binary spread output of every game
    # 01, winner, 23, spread, 45, o/u
    def spread(self):
        newLst = []
        lst = p.extractPickle("outcome_vectors.pickle", self.year)
        for i in range(len(lst)):
            odds = [lst[i][6]] + [lst[i][7]]
            if lst[i][0] == 1:
                new = [1,0] + odds
                newLst.append(new)
            elif lst[i][1] == 1:
                new = [0,1] + odds
                newLst.append(new)
        p.addToPickle(newLst, "spreads.pickle", self.year)

    # used as reference, puts all team stats gathered into convenient CSV
    def listToCSV(self, lst):
        with open("references/2019stats.csv", "w") as f:
            #write in header
            f.write("Away_Avg,Obp,Slg,Ops,Rpg,Hrpg,Sopg,Lh%,P-hand,Era,Whip,Hrp9,")
            f.write("Sop9,Ipg,B-Era,B-Whip,B-Hrp9,B-Sop9,Bspg,Home_Avg,Obp,Slg,Ops,")
            f.write("Rpg,Hrpg,Sopg,Lh%,P-hand,Era,Whip,Hrp9,Sop9,Ipg,B-Era,B-Whip,")
            f.write("B-Hrp9,B-Sop9,Bspg\n")

            #write in stats
            for i in range(len(lst)):
                line = ",".join(map(str, lst[i]))
                f.write(line)
                f.write("\n")

# l = ListCreator(2019)
# l.checkOdds()
# l.spread()
# DATA = p.extractPickle("all_games.pickle")
