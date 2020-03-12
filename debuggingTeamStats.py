import gatherPlayers as p
import getGamepks as gm
import statsapi as mlb
from enum import IntEnum

BATTERS = p.extractPickle("batters.pickle")
PITCHERS = p.extractPickle("pitchers.pickle")
SCORES = p.extractPickle('scores.pickle')
TEAM_STATS = {}
SAVE_PATH = "team_statData/"

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

def createTeamDicts():
    for tm in gm.teams_list:
        TEAM_STATS[tm] = {}

def addBatterStats(batStats, gmpk, lineup):


    def averageLineupStats(stat, gmpk, lineup, perGame=False):
        statSum = 0
        perGame = 0
        count = 0
        for batter in lineup:
            try:
                if perGame:
                    perGame = float(BATTERS[batter]['gmpks'][gmpk][stat]) / BATTERS[batter]['gmpks'][gmpk]['gamesPlayed']
                    statSum += perGame
                else:
                    statSum += float(BATTERS[batter]['gmpks'][gmpk][stat])
                count += 1
            except KeyError:
                pass
        statAvg = round(statSum / count, 3)
        return statAvg


    batStats[BatterStats.BA] = averageLineupStats('avg', gmpk, lineup)
    batStats[BatterStats.OBP] = averageLineupStats('obp', gmpk, lineup)
    batStats[BatterStats.SLG] = averageLineupStats('slg', gmpk, lineup)
    batStats[BatterStats.OPS] = averageLineupStats('ops', gmpk, lineup)
    batStats[BatterStats.RPG] = averageLineupStats('runs', gmpk, lineup, True)
    batStats[BatterStats.HRPG] = averageLineupStats('homeRuns', gmpk, lineup, True)
    batStats[BatterStats.SOPG] = averageLineupStats('strikeOuts', gmpk, lineup, True)
    lhpSum = 0
    count = 0
    try:
        for player in lineup:
            if BATTERS[player]['bats'] == "L":
                lhpSum += 1
            count += 1
    except KeyError: pass
    lhpPercent = round(lhpSum / count, 2)
    batStats[BatterStats.LHP] = lhpPercent

def addPitcherStats(pitchingStats, gmpk, tm, opposingPitcher):
    bpName = tm + " Bullpen"
    pitchingStats[PitcherStats.HAND] = PITCHERS[opposingPitcher]['throws']
    pitchingStats[PitcherStats.ERA] = float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['era'])
    pitchingStats[PitcherStats.WHIP] = \
        round((float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['hits']) + \
        float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['baseOnBalls'])) / \
        float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['inningsPitched']), 3)
    pitchingStats[PitcherStats.HRP9] = round(float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['homeRuns']) * 9 \
        / float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['inningsPitched']), 3)
    pitchingStats[PitcherStats.SOP9] = round(float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['strikeOuts']) * 9 \
        / float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['inningsPitched']), 3)
    pitchingStats[PitcherStats.IPG] = round(float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['inningsPitched']) / \
        float(PITCHERS[opposingPitcher]['gmpks'][gmpk]['gamesPlayed']), 3)
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

def gatherTeamStats(tm):
    print("Team:", tm)
    stats = {"gameStats": {}, "gamesInOrder": []}
    TEAM_STATS[tm] = stats
    with open("team_gameData/" + tm.replace(" ", "_") + ".txt", "r") as f:
        line = f.readline()
        count = 0
        while(line != ""):
            homeOrAway = line[0:4].lower()
            opponent = ""
            if homeOrAway == "away":
                opponent = 'home'
            else:
                opponent = 'away'

            gmpk = int(line[5:11])
            count += 1
            print(gmpk, count)
            stats["gamesInOrder"].append(gmpk)
            game = mlb.boxscore_data(gmpk)

            # check for empty game pack
            if game['away']['teamStats']['batting']['runs'] == game['home']['teamStats']['batting']['runs']:
                print("False game")
                line = f.readline()
                continue

            lineup = game[homeOrAway]['batters']
            opposingPitcher = int(game[opponent]['pitchers'][0])

            # load in batter stats
            batStats = [0,0,0,0,0,0,0,0]
            addBatterStats(batStats, gmpk, lineup)

            # load in pitcher stats
            pitchingStats = [0,0,0,0,0,0,0,0,0,0,0]
            addPitcherStats(pitchingStats, gmpk, tm, opposingPitcher)

            # add in list of stats received for team gamepack
            TEAM_STATS[tm]['gameStats'][gmpk] = (batStats, pitchingStats)

            line = f.readline()

def addInAllStats():
    createTeamDicts()
    for tm in gm.teams_list:
        gatherTeamStats(tm)
    p.addToPickle(TEAM_STATS, "all_team_stats.pickle")


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
