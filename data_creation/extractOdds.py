# Odds used available from Sports Book Reviews Online
# https://sportsbookreviewsonline.com/scoresoddsarchives/mlb/mlboddsarchives.htm

import statsapi as mlb
from sys import exit
import gatherPlayers as p
import requests, time

import os
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Gmpk: int
# away:, home:
#     Date: ""
#     Visitor: ""
#     Home: ""
#     Open: int
#     Close: int
#     Runline: float
#     RunlineOdds: int
#     OpenOU: float
#     OpenOUOdds: int
#     CloseOU: float
#     CloseOUOdds: int

homeAway = {'V': 'away', 'H': 'home'}
teams = ({
"LAA": "Angels",
"ARI": "D-backs",
"BAL": "Orioles",
"BOS": "Red Sox",
"BRS": "Red Sox",
"CHC": "Cubs",
"CUB": "Cubs",
"CIN": "Reds",
"CLE": "Indians",
"COL": "Rockies",
"DET": "Tigers",
"HOU": "Astros",
"KAN": "Royals",
"LAD": "Dodgers",
"WAS": "Nationals",
"NYM": "Mets",
"OAK": "Athletics",
"PIT": "Pirates",
"SDG": "Padres",
"SEA": "Mariners",
"SFO": "Giants",
"SFG": "Giants",
"STL": "Cardinals",
"TAM": "Rays",
"TEX": "Rangers",
"TOR": "Blue Jays",
"MIN": "Twins",
"PHI": "Phillies",
"ATL": "Braves",
"CWS": "White Sox",
"MIA": "Marlins",
"NYY": "Yankees",
"MIL": "Brewers",
"LOS": "Dodgers"
})

# No gmpk 567304
# No odds 565085

# 15 through 22

class OddsExtractor:
    def __init__(self, year):
        self.year = year
        self.ODDS = {}

    def getDate(self, dict):
        date = dict['gameId'][:10]
        dateMonth = date[6]
        dateDay = date[8:10]
        return dateMonth + dateDay

    def makeNumbers(self, line):
        for i in range(15,23):
            if line[i] == "NL":
                line[i] = line[i]
            elif "." in line[i]:
                line[i] = float(line[i])
            else: line[i] = int(line[i])
        return line

    # good to convert to make computations better for custom loss function
    def convertAmericanToDecimal(self, odds):
        for i in range(5):
            if i % 2 != 0: continue
            if odds[i] < 0:
                odds[i] = 1 - (100 / odds[i])
            else:
                odds[i] = 1 + (odds[i] / 100)
        return odds

    def getFirstInningOutcome(self, line, homeLine):
        if int(line[5]) + int(homeLine[5]) > 0:
            return [1,0]
        return [0,1]

    def matchGmpkToLine(self, gmpk, dict):
        oddsDate = self.getDate(dict)
        gmpkOdds = {'away': [], 'home': [], 'scoreFirst': []}

        with open("references/" + str(self.year) + "/mlb_odds_" + str(self.year) + ".csv", "r") as f:
            f.readline()
            line = f.readline()
            while line != "":
                line = line.strip().split(",")
                if line[0] != oddsDate:
                    line = f.readline()
                    continue
                team = teams[line[3]]
                homeOrAway = homeAway[line[2]]

                if homeOrAway == 'away':
                    if team != dict['teamInfo']['away']['teamName']:
                        line = f.readline()
                        continue
                else:
                    line = f.readline()
                    continue

                homeLine = f.readline().strip().split(",")
                line = self.makeNumbers(line)
                homeLine = self.makeNumbers(homeLine)

                ## do they score in first inning
                gmpkOdds['scoreFirst'] = self.getFirstInningOutcome(line, homeLine)

                line = line[16:23]
                del line[3]
                del line[3]
                line = self.convertAmericanToDecimal(line)
                homeLine = homeLine[16:23]
                del homeLine[3]
                del homeLine[3]
                homeLine = self.convertAmericanToDecimal(homeLine)

                gmpkOdds['away'] = line
                gmpkOdds['home'] = homeLine

                self.ODDS[gmpk] = gmpkOdds
                return True
            return False

    def extractAllOdds(self):
        with open("team_gameData/" + str(self.year) + "/AllGamesOnce.txt", "r") as f:
            line = f.readline()
            gamesRemaining = 2430
            while line != "":
                gamesRemaining -= 1
                gmpk = int(line[:6])
                if (gamesRemaining % 50 == 0):
                    print("GAMES REMAINING: " + str(gamesRemaining))

                ## handle connection errors when making requests
                dict = None
                for x in range(4):
                    try:
                        dict = mlb.boxscore_data(gmpk)
                        break
                    except requests.exceptions.ConnectionError:
                        print("Connection Error for gamepk {}, try #{}".format(gmpk, x))
                        time.sleep(10)
                        continue
                if not dict:
                    print("Connection Errors. Program Exit")
                    exit(-1)

                success = self.matchGmpkToLine(gmpk, dict)
                if not success:
                    self.ODDS[gmpk] = "No odds"
                    print("No odds")
                line = f.readline()
        p.addToPickle(self.ODDS, "all_odds.pickle", self.year)
