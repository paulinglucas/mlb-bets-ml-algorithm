import gatherPlayers as p
import getGamepks as gm
from enum import IntEnum

import os
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


SAVE_PATH = "team_gameData/"

# stats for each gamepack will be stats leading up to current game
# eg. stats for game 2 will be stats accumulated after game 1
class BatterStats(IntEnum):
    BA = 0      # team BA
    OBP = 1     # team OBP
    SLG = 2     # team SLG
    OPS = 3     # team OPS
    RPG = 4     # team Runs Per Game

class Last10:
    def __init__(self, year):
        self.year = year
        self.BATTERS = p.extractPickle("batters.pickle", self.year)
        self.PITCHERS = p.extractPickle("pitchers.pickle", self.year)
        self.SCORES = p.extractPickle('scores.pickle', self.year)

    # get previous game played of player
    def getPreviousGame(self, batOrPitch, player, gmpk):
        if batOrPitch == 'Batter':
            p = self.BATTERS[player]['gmpksInOrder']
        else: p = self.PITCHERS[player]['gmpksInOrder']
        idx = p.index(gmpk)
        if idx == 0:
            return gmpk
        return p[idx-1]

    def averageLast10(self, player, gmpk, stat):
        currGame = gmpk
        prevGame = self.getPreviousGame("Batter", player, gmpk)
        sum = 0
        count = 0
        p = self.BATTERS[player]['gmpks']
        while currGame != prevGame and count < 10:
            if not p[currGame]:
                temp = currGame
                currGame = prevGame
                prevGame = self.getPreviousGame("Batter", player, temp)
                continue
            sum += float(p[currGame][stat])
            count += 1
            temp = currGame
            currGame = prevGame
            prevGame = self.getPreviousGame("Batter", player, temp)
        if count == 0: return 0.0
        return round(float(sum / count), 3)

    # returns stat of lineup
    def averageLineupStats(self, stat, gmpk, lineup, perGame=False):
        statSum = 0
        count = 0
        for batter in lineup:
            try:
                statSum += self.averageLast10(batter, gmpk, stat)
                count += 1
            except (KeyError, ValueError):
                pass
        if count == 0.0:
            return 0.0
        statAvg = round(statSum / count, 3)
        return statAvg

    # batter stats going in
    def addBatterStats(self, batStats, gmpk, lineup):
        # add in stats to batter stats
        batStats[BatterStats.BA] = self.averageLineupStats('avg', gmpk, lineup)
        batStats[BatterStats.OBP] = self.averageLineupStats('obp', gmpk, lineup)
        batStats[BatterStats.SLG] = self.averageLineupStats('slg', gmpk, lineup)
        batStats[BatterStats.OPS] = self.averageLineupStats('ops', gmpk, lineup)
        batStats[BatterStats.RPG] = self.averageLineupStats('runs', gmpk, lineup)

    # get game stats of every game of 2019
    def gatherGameStats(self, gmpk, batters):
        batStats = [0,0,0,0,0]
        self.addBatterStats(batStats, gmpk, batters)
        return batStats

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
