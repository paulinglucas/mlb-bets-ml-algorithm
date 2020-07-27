from gameStats import GameStats
from last10 import Last10
from getGamepks import teams_id
import gatherPlayers as p
import statsapi as mlb
from enum import IntEnum

class BatterStats(IntEnum):
    BA = 0      # team BA
    OBP = 1     # team BA
    SLG = 2     # team BA
    OPS = 3     # team OPS
    RPG = 4     # team Runs Per Game
    HRPG = 5    # team Home Runs Per Game
    SOPG = 6    # team Strikeouts Per Game
    LHP = 7     # percentage of left-handed batters in starting lineup

class Predictor:
    def __init__(self, year):
        self.year = year
        self.BATTERS = p.extractPickle("batters.pickle", self.year)
        self.PITCHERS = p.extractPickle("pitchers.pickle", self.year)
        self.SCORES = p.extractPickle('scores.pickle', self.year)

    def lookup(self, name, tm):
        name = name.split()
        if len(name) == 3:
            name = name[1] + " " + name[2] + ", " + name[0]
        else:
            name = name[1] + ", " + name[0]
        player = mlb.lookup_player(name, season=self.year)
        if player == []:
            return None

        for p in player:
            if teams_id[p['currentTeam']['id']] == tm:
                return p['id']


    # returns stat of lineup
    def averageLineupStats(self, stat, gmpk, lineup, perGame=False):
        statSum = 0
        count = 0
        for batter in lineup:
            try:
                batterGmpk = gmpk
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
        lhpPercent = round(lhpSum / count, 2)
        batStats[BatterStats.LHP] = lhpPercent

    def getLineups(self, g):
        data = mlb.boxscore_data(g['game_id'])
        try:
            lineups = {'home': teams_id[g['home_id']],
                               'away': teams_id[g['away_id']],
                               'hLineup': data['home']['battingOrder'],
                               'aLineup': data['away']['battingOrder'],
                               'hStarter': data['home']['pitchers'][0],
                               'aStarter': data['away']['pitchers'][0]
                              }
        except IndexError:
            print("Lineups for {} @ {} not yet created.\n".format(teams_id[g['away_id']], teams_id[g['home_id']]))
            return -1
        return lineups

    def returnTeamStats(self, tm, pitcher, lineup):
        # getGamepk for lineup and bullpen
        prevGmpk = self.BATTERS[tm]['gmpksInOrder'][-1]

        # check if pitcher has pitched in previous game
        pitcherGmpk = self.PITCHERS[pitcher]['gmpksInOrder'][-1]

        # load in batter stats
        batStats = [0,0,0,0,0,0,0,0]
        self.addBatterStats(batStats, prevGmpk, lineup)

        # load in pitcher stats
        g = GameStats(self.year)
        pitchingStats = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        g.addPitcherStats(pitchingStats, pitcherGmpk, pitcher)

        # load in bullpen stats and ERR
        g.addBullpenStats(pitchingStats, prevGmpk, tm)
        g.earnedRunRatio(pitchingStats, pitcherGmpk, prevGmpk, tm, pitcher)

        # get last 10 batting stats
        lTen = Last10(self.year)
        last10stats = lTen.gatherGameStats(prevGmpk, lineup)

        teamWinPercent = self.BATTERS[tm]['gmpks'][prevGmpk]['winPercent']
        teamWinPercentLast10 = self.BATTERS[tm]['gmpks'][prevGmpk]['winsLast10']
        pExpLast10 = self.BATTERS[tm]['gmpks'][prevGmpk]['expectation']

        # add in list of stats received for team gamepack
        teamStats = [teamWinPercent, teamWinPercentLast10, pExpLast10] + batStats + last10stats + pitchingStats
        return teamStats

    # get game stats of every game of 2019
    def inputGameStats(self, game):
        stats = {}
        lineups = self.getLineups(game)
        if lineups == -1:
            return -1

        print("####################################")
        print("##### {0:10} @  {1:10} #####".format(lineups['away'].upper(), lineups['home'].upper()))
        print("####################################")

        awayPitchId = lineups['aStarter']
        homePitchId = lineups['hStarter']

        if awayPitchId == None:
            print("Away pitcher not found. Do not bet this game. Goodbye.\n")
            return -1
        if homePitchId == None:
            print("Away pitcher not found. Do not bet this game. Goodbye.\n")
            return -1

        try:
            aPitcher = self.PITCHERS[awayPitchId]
            aPitcher = awayPitchId
        except KeyError:
            print("Away pitcher not found. Do not bet this game. Goodbye.\n")
            return -1

        try:
            hPitcher = self.PITCHERS[homePitchId]
            hPitcher = homePitchId
        except KeyError:
            print("Home pitcher not found. Do not bet this game. Goodbye.\n")
            return -1

        homeLineup = lineups['hLineup']
        awayLineup = lineups['aLineup']

        stats['away'] = self.returnTeamStats(lineups['away'], aPitcher, awayLineup)
        stats['home'] = self.returnTeamStats(lineups['home'], hPitcher, homeLineup)

        lst = stats['away'] + stats['home']
        return lst


       # use last_game() to grab info, automate lineup lookup
