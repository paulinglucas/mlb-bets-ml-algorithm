# Odds used available from Sports Book Reviews Online
# https://sportsbookreviewsonline.com/scoresoddsarchives/mlb/mlboddsarchives.htm

import statsapi as mlb
from sys import exit
import gatherPlayers as p

ODDS = {}

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
"MIL": "Brewers"
})

# No gmpk 567304
# No odds 565085

# 15 through 22

def getDate(dict):
    date = dict['gameId'][:10]
    dateMonth = date[6]
    dateDay = date[8:10]
    return dateMonth + dateDay

def makeNumbers(line):
    for i in range(15,23):
        if line[i] == "NL":
            line[i] = line[i]
        elif "." in line[i]:
            line[i] = float(line[i])
        else: line[i] = int(line[i])
    return line

def convertAmericanToDecimal(odds):
    for i in range(8):
        if i % 2 == 0: continue
        if odds[i] < 0:
            odds[i] = 1 - (100 / odds[i])
        else:
            odds[i] = 1 + (odds[i] / 100)
    return odds


def matchGmpkToLine(gmpk, dict):
    oddsDate = getDate(dict)
    gmpkOdds = {'away': [], 'home': []}

    with open("mlb_odds_2019.csv", "r") as f:
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
            line = makeNumbers(line)
            homeLine = makeNumbers(homeLine)
            line = convertAmericanToDecimal(line[15:23])
            homeLine = convertAmericanToDecimal(homeLine[15:23])

            gmpkOdds['away'] = line
            gmpkOdds['home'] = homeLine

            ODDS[gmpk] = gmpkOdds
            return True
        return False

def extractAllOdds():
    with open("team_gameData/AllGamesOnce.txt", "r") as f:
        line = f.readline()
        count = 0
        while line != "":
            count += 1
            gmpk = int(line[:6])
            print(gmpk, count)
            dict = mlb.boxscore_data(gmpk)
            success = matchGmpkToLine(gmpk, dict)
            if not success:
                ODDS[gmpk] = "No odds"
                print("No odds")
            line = f.readline()
    p.addToPickle(ODDS, "all_odds.pickle", "odds_data/")

#extractAllOdds()
# ODDS = p.extractPickle("all_odds.pickle", "odds_data/")
# print(ODDS[565901])
