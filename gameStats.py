import gatherPlayers as p
import getGamepks as gm
import statsapi as mlb
from enum import IntEnum


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
    BSPG = 10    # Blown Saves per Game

# Other Stats to keep in mind:
#     Home team name
#     Away team name
#     Starter Throwing Hand
#     Batting lineup %LHB


inputs_list = ([
"Team BA",
"Team OBP",
"Team SLG",
"Team RPG",
"Team HRPG",
"Starter ERA",
"Starter WHIP",
"Bullpen ERA",
"Starter HRPG",
"Bullpen HRPG"
])

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
                if line[5:11] == gamepk:
                    return prevLine[5:11]
                prevLine = line

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

    # batter stats going in
    def addBatterStats(self, batStats, gmpk, lineup):

        # returns stat of lineup
        def averageLineupStats(self, stat, gmpk, lineup, perGame=False):
            statSum = 0
            count = 0
            for batter in lineup:
                try:
                    batterGmpk = self.getPreviousGame('Batter', batter, gmpk)
                    if perGame:
                        statForGame = float(self.BATTERS[batter]['gmpks'][batterGmpk][stat]) / self.BATTERS[batter]['gmpks'][batterGmpk]['gamesPlayed']
                        statSum += statForGame
                    else:
                        statSum += float(self.BATTERS[batter]['gmpks'][batterGmpk][stat])
                    count += 1
                except:
                    pass
            if perGame:
                statAvg = round(statSum, 3)
            else: statAvg = round(statSum / count, 3)
            return statAvg

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
        lhpPercent = round(lhpSum / count, 2)
        batStats[BatterStats.LHP] = lhpPercent

    # add in pitcher stats
    def addPitcherStats(self, pitchingStats, gmpk, pitcher):
        # make L 0 and R 1 for tensorflow purposes
        if self.PITCHERS[pitcher]['throws'] == "L":
            pitchingStats[PitcherStats.HAND] = 0
        else:
            pitchingStats[PitcherStats.HAND] = 1
        pitchingStats[PitcherStats.ERA] = float(self.PITCHERS[pitcher]['gmpks'][gmpk]['era'])
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

    # bullpen stats going in too
    def addBullpenStats(self, pitchingStats, gmpk, tm):
        bpName = tm + " Bullpen"
        pitchingStats[PitcherStats.bERA] = float(self.PITCHERS[bpName]['gmpks'][gmpk]['era'])
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

    # get game stats of every game of 2019
    def gatherGameStats(self, gmpk, count):
        stats = {"away": [], "home": [], "outcome": []}
        self.DATA['gmpks'][gmpk] = stats

        print(gmpk, count)
        game = mlb.boxscore_data(gmpk)

        # check for empty game pack
        if game['away']['teamStats']['batting']['runs'] == game['home']['teamStats']['batting']['runs']:
            print("False game")
            return None

        teams = ['away', 'home']
        away = True
        for team in teams:
            currTeamName = game['teamInfo'][team]['teamName']

            # getGamepk for lineup and bullpen
            prevGmpk = self.getPreviousTeamGame(currTeamName, gmpk)
            pitcher = int(game[team]['pitchers'][0])
            lineup = game[team]['batters']

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
            pitchingStats = [0,0,0,0,0,0,0,0,0,0,0]
            self.addPitcherStats(pitchingStats, pitcherGmpk, pitcher)

            # load in bullpen stats
            self.addBullpenStats(pitchingStats, prevGmpk, currTeamName)

            bpName = currTeamName + " Bullpen"
            teamWinPercent = round(float(self.PITCHERS[bpName]['gmpks'][prevGmpk]['wins']) / self.PITCHERS[bpName]['gmpks'][prevGmpk]['gamesPlayed'], 3)
            # add in list of stats received for team gamepack
            teamStats = [teamWinPercent] + batStats + pitchingStats
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
            count = 1
            while line != "":
                gmpk = int(line[:6])
                gatherGameStats(gmpk, count)
                line = f.readline()
                count += 1
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
