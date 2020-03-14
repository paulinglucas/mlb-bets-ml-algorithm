import gatherPlayers as p
import getGamepks as gm
import statsapi as mlb
from enum import IntEnum

BATTERS = p.extractPickle("batters.pickle")
PITCHERS = p.extractPickle("pitchers.pickle")
SCORES = p.extractPickle('scores.pickle')

DATA = {'gmpks': {}}
# gmpks: outcome, data away, data home

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

# get gamepack of last game played in reference to gamepack parameter using
# team file
def getPreviousTeamGame(tm, gamepk):
    with open(SAVE_PATH + tm.replace(" ", "_") + ".txt") as f:
        prevLine = None
        for line in f:
            if line[5:11] == gamepk:
                return prevLine[5:11]
            prevLine = line

# gets game after gamepack param
def getNextTeamGame(tm, gamepk):
    with open(SAVE_PATH + tm.replace(" ", "_") + ".txt") as f:
        for line in f:
            if line[5:11] == gamepk:
                try: return f.readline()[5:11]
                except: return None

# get previous game played of player
def getPreviousGame(batOrPitch, player, gmpk):
    if batOrPitch == 'Batter':
        p = BATTERS[player]['gmpksInOrder']
    else: p = PITCHERS[player]['gmpksInOrder']
    idx = p.index(gmpk)
    if idx == 0:
        return gmpk
    return p[idx-1]

# batter stats going in
def addBatterStats(batStats, gmpk, lineup):

    # returns stat of lineup
    def averageLineupStats(stat, gmpk, lineup, perGame=False):
        statSum = 0
        count = 0
        for batter in lineup:
            try:
                batterGmpk = getPreviousGame('Batter', batter, gmpk)
                if perGame:
                    statForGame = float(BATTERS[batter]['gmpks'][batterGmpk][stat]) / BATTERS[batter]['gmpks'][batterGmpk]['gamesPlayed']
                    statSum += statForGame
                else:
                    statSum += float(BATTERS[batter]['gmpks'][batterGmpk][stat])
                count += 1
            except:
                pass
        if perGame:
            statAvg = round(statSum, 3)
        else: statAvg = round(statSum / count, 3)
        return statAvg

    # add in stats to batter stats
    batStats[BatterStats.BA] = averageLineupStats('avg', gmpk, lineup)
    batStats[BatterStats.OBP] = averageLineupStats('obp', gmpk, lineup)
    batStats[BatterStats.SLG] = averageLineupStats('slg', gmpk, lineup)
    batStats[BatterStats.OPS] = averageLineupStats('ops', gmpk, lineup)
    batStats[BatterStats.RPG] = averageLineupStats('runs', gmpk, lineup, True)
    batStats[BatterStats.HRPG] = averageLineupStats('homeRuns', gmpk, lineup, True)
    batStats[BatterStats.SOPG] = averageLineupStats('strikeOuts', gmpk, lineup, True)
    lhpSum = 0
    count = 0
    # get % lineup that is left-handed
    try:
        for player in lineup:
            if BATTERS[player]['bats'] == "L":
                lhpSum += 1
            count += 1
    except KeyError: pass
    lhpPercent = round(lhpSum / count, 2)
    batStats[BatterStats.LHP] = lhpPercent

# add in pitcher stats
def addPitcherStats(pitchingStats, gmpk, pitcher):
    # make L 0 and R 1 for tensorflow purposes
    if PITCHERS[pitcher]['throws'] == "L":
        pitchingStats[PitcherStats.HAND] = 0
    else:
        pitchingStats[PitcherStats.HAND] = 1
    pitchingStats[PitcherStats.ERA] = float(PITCHERS[pitcher]['gmpks'][gmpk]['era'])
    pitchingStats[PitcherStats.WHIP] = \
        round((float(PITCHERS[pitcher]['gmpks'][gmpk]['hits']) + \
        float(PITCHERS[pitcher]['gmpks'][gmpk]['baseOnBalls'])) / \
        float(PITCHERS[pitcher]['gmpks'][gmpk]['inningsPitched']), 3)
    pitchingStats[PitcherStats.HRP9] = round(float(PITCHERS[pitcher]['gmpks'][gmpk]['homeRuns']) * 9 \
        / float(PITCHERS[pitcher]['gmpks'][gmpk]['inningsPitched']), 3)
    pitchingStats[PitcherStats.SOP9] = round(float(PITCHERS[pitcher]['gmpks'][gmpk]['strikeOuts']) * 9 \
        / float(PITCHERS[pitcher]['gmpks'][gmpk]['inningsPitched']), 3)
    pitchingStats[PitcherStats.IPG] = round(float(PITCHERS[pitcher]['gmpks'][gmpk]['inningsPitched']) / \
        float(PITCHERS[pitcher]['gmpks'][gmpk]['gamesPlayed']), 3)

# bullpen stats going in too
def addBullpenStats(pitchingStats, gmpk, tm):
    bpName = tm + " Bullpen"
    pitchingStats[PitcherStats.bERA] = float(PITCHERS[bpName]['gmpks'][gmpk]['era'])
    pitchingStats[PitcherStats.bWHIP] = \
        round((float(PITCHERS[bpName]['gmpks'][gmpk]['hits']) + \
        float(PITCHERS[bpName]['gmpks'][gmpk]['baseOnBalls'])) / \
        float(PITCHERS[bpName]['gmpks'][gmpk]['inningsPitched']), 3)
    pitchingStats[PitcherStats.bHRP9] = round(float(PITCHERS[bpName]['gmpks'][gmpk]['homeRuns']) * 9 \
        / float(PITCHERS[bpName]['gmpks'][gmpk]['inningsPitched']), 3)
    pitchingStats[PitcherStats.bSOP9] = round(float(PITCHERS[bpName]['gmpks'][gmpk]['strikeOuts']) * 9 \
        / float(PITCHERS[bpName]['gmpks'][gmpk]['inningsPitched']), 3)
    pitchingStats[PitcherStats.BSPG] = round(float(PITCHERS[bpName]['gmpks'][gmpk]['blownSaves']) / \
        float(PITCHERS[bpName]['gmpks'][gmpk]['gamesPlayed']), 3)

# get game stats of every game of 2019
def gatherGameStats(gmpk, count):
    stats = {"away": [], "home": [], "outcome": []}
    DATA['gmpks'][gmpk] = stats

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
        prevGmpk = getPreviousTeamGame(currTeamName, gmpk)
        pitcher = int(game[team]['pitchers'][0])
        lineup = game[team]['batters']

        # check if pitcher has pitched in previous game
        pitcherGmpk = getPreviousGame('Pitcher', pitcher, gmpk)

        # check if this is teams first game
        if prevGmpk != None:
            prevGmpk = int(prevGmpk)
        else: prevGmpk = gmpk

        # load in batter stats
        batStats = [0,0,0,0,0,0,0,0]
        addBatterStats(batStats, gmpk, lineup)

        # load in pitcher stats
        pitchingStats = [0,0,0,0,0,0,0,0,0,0,0]
        addPitcherStats(pitchingStats, pitcherGmpk, pitcher)

        # load in bullpen stats
        addBullpenStats(pitchingStats, prevGmpk, currTeamName)

        bpName = currTeamName + " Bullpen"
        teamWinPercent = round(float(PITCHERS[bpName]['gmpks'][prevGmpk]['wins']) / PITCHERS[bpName]['gmpks'][prevGmpk]['gamesPlayed'], 3)
        # add in list of stats received for team gamepack
        teamStats = [teamWinPercent] + batStats + pitchingStats
        if away:
            stats['away'] = teamStats
            away = False
        else: stats['home'] = teamStats
        stats['outcome'] = SCORES[gmpk]

    DATA['gmpks'][gmpk] = stats
    return 1

# add all stats to DATA dictionary
def addInAllStats():
    with open("team_gameData/AllGamesOnce.txt", "r") as f:
        line = f.readline()
        count = 1
        while line != "":
            gmpk = int(line[:6])
            gatherGameStats(gmpk, count)
            line = f.readline()
            count += 1
        p.addToPickle(DATA, "all_games.pickle")



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
