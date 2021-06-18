import gatherPlayers as p
import getGamepks as gm
import statsapi as mlb
from enum import IntEnum
from last10 import Last10
import sys, requests, time

import os
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


SAVE_PATH = "team_gameData/"

# stats for each gamepack will be stats leading up to current game
# eg. stats for game 2 will be stats accumulated after game 1
class BatterStats(IntEnum):
    BA = 0      # team BA
    OBP = 1     # team BA
    SLG = 2     # team BA
    OPS = 3     # team OPS
    RPG = 4     # team Runs Per Game
    HRPG = 5    # team Home Runs Per Game
    SOPG = 6    # team Strikeouts Per Game
    LHP = 7     # percentage of left-handed batters in starting lineup

class PitcherStats(IntEnum):
    HAND = 0    # starter dominant pitching hand
    ERA = 1     # starter ERA
    WHIP = 2    # starter WHIP
    HRP9 = 3    # starter Home Runs per 9 Innings
    SOP9 = 4    # starter Strikeouts per 9 Innings
    IPG = 5     # Starters average innings per game
    bERA = 6    # Bullpen ERA
    bWHIP = 7   # Bullpen WHIP
    bHRP9 = 8   # Bullpen Home Runs per 9
    bSOP9 = 9   # Bullpen Strikeouts per 9
    BSPG = 10   # Blown Saves per Game
    RYAN = 11   # ryanicity of pitchers last game
    ERR = 12    # Earned Run Ratio of pitchers

# Other Stats to keep in mind:
#     Home team name
#     Away team name
#     Starter Throwing Hand
#     Batting lineup %LHB

class GameStats:
    def __init__(self, year):
        self.year = year
        self.BATTERS = p.extractPickle("batters.pickle", self.year)
        self.PITCHERS = p.extractPickle("pitchers.pickle", self.year)
        self.SCORES = p.extractPickle('scores.pickle', self.year)
        try:
            self.DATA = p.extractPickle('all_games.pickle', self.year)
        except:
            self.DATA = {'gmpks': {}}
            # gmpks: outcome, data away, data home

    # get gamepack of last game played in reference to gamepack parameter using
    # team file
    def getPreviousTeamGame(self, tm, gamepk):
        with open(SAVE_PATH + str(self.year) + "/" + tm.replace(" ", "_") + ".txt") as f:
            prevLine = None
            for line in f:
                if int(line[5:11]) == gamepk:
                    if prevLine == None:
                        return None
                    return prevLine[5:11]
                prevLine = line
        return -1

    # gets game after gamepack param
    def getNextTeamGame(self, tm, gamepk):
        with open(SAVE_PATH + str(self.year) + "/" + tm.replace(" ", "_") + ".txt") as f:
            for line in f:
                if line[5:11] == gamepk:
                    try: return f.readline()[5:11]
                    except: return None

    # get previous game played of player
    def getPreviousGame(self, batOrPitch, player, gmpk):
        if batOrPitch == 'Batter':
            p = self.BATTERS[player]['gmpksInOrder']
        else: p = self.PITCHERS[player]['gmpksInOrder']
        idx = p.index(gmpk)
        if idx == 0:
            return gmpk
        return p[idx-1]

    # returns stat of lineup
    def averageLineupStats(self, stat, gmpk, lineup, perGame=False):
        statSum = 0
        count = 0
        for batter in lineup:
            try:
                batterGmpk = self.getPreviousGame('Batter', batter, gmpk)
                if not self.BATTERS[batter]['gmpks'][batterGmpk]:
                    continue
                if perGame:
                    statForGame = float(self.BATTERS[batter]['gmpks'][batterGmpk][stat]) / self.BATTERS[batter]['gmpks'][batterGmpk]['gamesPlayed']
                    statSum += statForGame
                else:
                    statSum += float(self.BATTERS[batter]['gmpks'][batterGmpk][stat])
                count += 1
            except Exception as e:
                pass
        if perGame:
            statAvg = round(statSum, 3)
        else: statAvg = round(statSum / count, 3)
        return statAvg

    # batter stats going in
    def addBatterStats(self, batStats, gmpk, lineup):

        # add in stats to batter stats
        batStats[BatterStats.BA] = self.averageLineupStats('avg', gmpk, lineup)
        batStats[BatterStats.OBP] = self.averageLineupStats('obp', gmpk, lineup)
        batStats[BatterStats.SLG] = self.averageLineupStats('slg', gmpk, lineup)
        batStats[BatterStats.OPS] = self.averageLineupStats('ops', gmpk, lineup)
        batStats[BatterStats.RPG] = self.averageLineupStats('runs', gmpk, lineup, True)
        batStats[BatterStats.HRPG] = self.averageLineupStats('homeRuns', gmpk, lineup, True)
        batStats[BatterStats.SOPG] = self.averageLineupStats('strikeOuts', gmpk, lineup, True)
        lhpSum = 0
        count = 0
        # get % lineup that is left-handed
        try:
            for player in lineup:
                if self.BATTERS[player]['bats'] == "L":
                    lhpSum += 1
                count += 1
        except KeyError: pass
        try:
            lhpPercent = round(lhpSum / count, 2)
        except ZeroDivisionError:
            lhpPercent = 0.0
        batStats[BatterStats.LHP] = lhpPercent

    # add in pitcher stats
    def addPitcherStats(self, pitchingStats, gmpk, pitcher):
        # make L 0 and R 1 for tensorflow purposes
        if self.PITCHERS[pitcher]['throws'] == "L":
            pitchingStats[PitcherStats.HAND] = 0
        else:
            pitchingStats[PitcherStats.HAND] = 1
        try:
            pitchingStats[PitcherStats.ERA] = float(self.PITCHERS[pitcher]['gmpks'][gmpk]['era'])
        except ValueError:
            if float(self.PITCHERS[pitcher]['gmpks'][gmpk]['hits']) > 2:
                pitchingStats[PitcherStats.ERA] = 99.99
            else:
                pitchingStats[PitcherStats.ERA] = 0
        if self.PITCHERS[pitcher]['gmpks'][gmpk]['inningsPitched'] == 0:
            if float(self.PITCHERS[pitcher]['gmpks'][gmpk]['hits']) > 2:
                pitchingStats[PitcherStats.WHIP] = 99.99
            else:
                pitchingStats[PitcherStats.WHIP] = 0
            pitchingStats[PitcherStats.HRP9] = 0.0
            pitchingStats[PitcherStats.SOP9] = 0.0
            pitchingStats[PitcherStats.IPG] = 0.0
        else:
            pitchingStats[PitcherStats.WHIP] = \
                round((float(self.PITCHERS[pitcher]['gmpks'][gmpk]['hits']) + \
                       float(self.PITCHERS[pitcher]['gmpks'][gmpk]['baseOnBalls'])) / \
                       float(self.PITCHERS[pitcher]['gmpks'][gmpk]['inningsPitched']), 3)
            pitchingStats[PitcherStats.HRP9] = round(float(self.PITCHERS[pitcher]['gmpks'][gmpk]['homeRuns']) * 9 \
                                                   / float(self.PITCHERS[pitcher]['gmpks'][gmpk]['inningsPitched']), 3)
            pitchingStats[PitcherStats.SOP9] = round(float(self.PITCHERS[pitcher]['gmpks'][gmpk]['strikeOuts']) * 9 \
                                                   / float(self.PITCHERS[pitcher]['gmpks'][gmpk]['inningsPitched']), 3)
            pitchingStats[PitcherStats.IPG] = round(float(self.PITCHERS[pitcher]['gmpks'][gmpk]['inningsPitched']) / \
                                                    float(self.PITCHERS[pitcher]['gmpks'][gmpk]['gamesPlayed']), 3)
        pitchingStats[PitcherStats.RYAN] = self.PITCHERS[pitcher]['gmpks'][gmpk]['ryanicity']

    # bullpen stats going in too
    def addBullpenStats(self, pitchingStats, gmpk, tm):
        bpName = tm + " Bullpen"
        pitchingStats[PitcherStats.bERA] = float(self.PITCHERS[bpName]['gmpks'][gmpk]['era'])
        if self.PITCHERS[bpName]['gmpks'][gmpk]['inningsPitched'] == 0:
            # print(bpName, self.PITCHERS[bpName]['gmpks'][gmpk])
            pitchingStats[PitcherStats.bWHIP] = 0.0
            pitchingStats[PitcherStats.bHRP9] = 0.0
            pitchingStats[PitcherStats.bSOP9] = 0.0
            pitchingStats[PitcherStats.BSPG] = 0.0
        else:
            pitchingStats[PitcherStats.bWHIP] = \
                round((float(self.PITCHERS[bpName]['gmpks'][gmpk]['hits']) + \
                       float(self.PITCHERS[bpName]['gmpks'][gmpk]['baseOnBalls'])) / \
                       float(self.PITCHERS[bpName]['gmpks'][gmpk]['inningsPitched']), 3)
            pitchingStats[PitcherStats.bHRP9] = round(float(self.PITCHERS[bpName]['gmpks'][gmpk]['homeRuns']) * 9 \
                                                    / float(self.PITCHERS[bpName]['gmpks'][gmpk]['inningsPitched']), 3)
            pitchingStats[PitcherStats.bSOP9] = round(float(self.PITCHERS[bpName]['gmpks'][gmpk]['strikeOuts']) * 9 \
                                                    / float(self.PITCHERS[bpName]['gmpks'][gmpk]['inningsPitched']), 3)
            pitchingStats[PitcherStats.BSPG] = round(float(self.PITCHERS[bpName]['gmpks'][gmpk]['blownSaves']) / \
                                                     float(self.PITCHERS[bpName]['gmpks'][gmpk]['gamesPlayed']), 3)

    def earnedRunRatio(self, pitchingStats, pitcherGmpk, bullpenGmpk, tm, pitcher):
        bpName = tm + " Bullpen"
        try:
            startERR = round(float(self.PITCHERS[pitcher]['gmpks'][pitcherGmpk]['earnedRuns']) /
                                   self.PITCHERS[pitcher]['gmpks'][pitcherGmpk]['runs'], 3)
            bpERR = round(float(self.PITCHERS[bpName]['gmpks'][bullpenGmpk]['earnedRuns']) /
                                self.PITCHERS[bpName]['gmpks'][bullpenGmpk]['runs'], 3)
            ratio = (startERR * pitchingStats[PitcherStats.IPG] + bpERR * (9 - pitchingStats[PitcherStats.IPG])) / 9
            pitchingStats[PitcherStats.ERR] = round(ratio, 3)
        except ZeroDivisionError:
            pitchingStats[PitcherStats.ERR] = 1.0

    # get game stats of every game of 2019
    def gatherGameStats(self, gmpk):
        stats = {"away": [], "home": [], "outcome": []}
        self.DATA['gmpks'][gmpk] = stats

        ## handle connection errors when making requests
        game = None
        for x in range(4):
            try:
                game = mlb.boxscore_data(gmpk)
                break
            except requests.exceptions.ConnectionError:
                print("Connection Error for gamepk {}, try #{}".format(gmpk, x))
                time.sleep(10)
                continue
        if not game:
            print("Connection Errors. Program Exit")
            sys.exit(-1)

        teams = ['away', 'home']
        away = True
        for team in teams:
            currTeamName = game['teamInfo'][team]['teamName']

            # getGamepk for lineup and bullpen
            prevGmpk = self.getPreviousTeamGame(currTeamName, gmpk)
            pitcher = int(game[team]['pitchers'][0])

            if prevGmpk == -1:
                print('bad initial gmpk file for game stats')
                sys.exit()

            ## data anomalies
            if gmpk == 447959 and pitcher == 592716:
                pitcher = int(game[team]['pitchers'][1])
            elif gmpk == 530553 and pitcher == 543475:
                pitcher = int(game[team]['pitchers'][1])
            elif gmpk == 531597 and pitcher == 453329:
                pitcher = int(game[team]['pitchers'][1])

            lineup = game[team]['battingOrder']

            # check if pitcher has pitched in previous game
            pitcherGmpk = self.getPreviousGame('Pitcher', pitcher, gmpk)

            # check if this is teams first game
            if prevGmpk != None:
                prevGmpk = int(prevGmpk)
            else: prevGmpk = gmpk

            # load in batter stats
            batStats = [0,0,0,0,0,0,0,0]
            self.addBatterStats(batStats, gmpk, lineup)

            # load in pitcher stats
            pitchingStats = [0,0,0,0,0,0,0,0,0,0,0,0,0]
            self.addPitcherStats(pitchingStats, pitcherGmpk, pitcher)

            # load in bullpen stats and ERR
            self.addBullpenStats(pitchingStats, prevGmpk, currTeamName)
            self.earnedRunRatio(pitchingStats, pitcherGmpk, prevGmpk, currTeamName, pitcher)

            # get last 10 batting stats
            lTen = Last10(self.year)
            last10stats = lTen.gatherGameStats(prevGmpk, lineup)

            teamWinPercent = self.BATTERS[currTeamName]['gmpks'][prevGmpk]['winPercent']
            teamWinPercentLast10 = self.BATTERS[currTeamName]['gmpks'][prevGmpk]['winsLast10']
            pExpLast10 = self.BATTERS[currTeamName]['gmpks'][prevGmpk]['expectation']

            # add in list of stats received for team gamepack
            teamStats = [teamWinPercent, teamWinPercentLast10, pExpLast10] + batStats + last10stats + pitchingStats
            if away:
                stats['away'] = teamStats
                away = False
            else: stats['home'] = teamStats
            stats['outcome'] = self.SCORES[gmpk]

        self.DATA['gmpks'][gmpk] = stats
        return 1

    # add all stats to DATA dictionary
    def addInAllStats(self):
        with open("team_gameData/" + str(self.year) + "/AllGamesOnce.txt", "r") as f:
            line = f.readline()
            gamesRemaining = 2430 # games in MLB season
            while line != "":
                gmpk = int(line[:6])
                gamesRemaining -= 1
                if (gamesRemaining % 50 == 0):
                    print("GAMES REMAINING: " + str(gamesRemaining))
                self.gatherGameStats(gmpk)
                line = f.readline()
            p.addToPickle(self.DATA, "all_games.pickle", self.year)



"""
    team pickle file
    |
    -- team dict
        |
        -- gamepacks
            |
            ---- batter team - pitcher team stats
                (these are stats leading UP TO current game)

    we want to feed in long list of stats containing teams batting stats and
    opponents pitching stats to see which team is more likely to win

    maybe add in wind direction/stadium?
"""
