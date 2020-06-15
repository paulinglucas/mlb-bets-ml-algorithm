import getGamepks as gm
import statsapi as mlb
import requests
import pickle
from math import floor
import sys

# adds dictionary to pickle file
def addToPickle(variabl, fname, year, save_path="pickle_files/"):
    with open(save_path + str(year) + "/" + fname, "wb") as f:
        pickle.dump(variabl, f)

# gets variable from pickle to be used for later
def extractPickle(fname, year, save_path="pickle_files/"):
    with open(save_path + str(year) + "/" + fname, "rb") as f:
        return pickle.load(f)

class PlayerGatherer:
    def __init__(self, year):
        self.year = year
        self.ALL_BATTERS = {}
        self.ALL_PITCHERS = {}
        self.SCORES = {}

    def winOrLose(self, score):
        if score[0] < score[1]:
            score.append("Home")
            return True
        elif score[0] > score[1]:
            score.append("Away")
            return True
        # error: tie
        else:
            return False

    # gets score of game along with winning team
    def addScore(self, game, gmpk):
        awayRuns = int(game['away']['teamStats']['batting']['runs'])
        homeRuns = int(game['home']['teamStats']['batting']['runs'])
        awayScore = [awayRuns, homeRuns]
        success = self.winOrLose(awayScore)

        # no tie
        if success:
            self.SCORES[gmpk] = awayScore

    # gets dominant batting and throwing hand of each player
    def throwsAndBats(self, id):
        urlBegin = "http://lookup-service-prod.mlb.com/json/named.player_info.bam?sport_code='mlb'&player_id='"
        urlEnd = "'&player_info.col_in=bats&player_info.col_in=throws"
        id = str(id)
        r = requests.get(urlBegin + id + urlEnd)
        queries = r.json()['player_info']['queryResults']['row']
        return (queries['throws'], queries['bats'])

    # adds player to databse with no game data
    def addPlayerInfo(self, playerInfo):
        for player in playerInfo:
            p = playerInfo.get(player)
            personInfo = p['person']
            id = personInfo['id']
            statInfo = p['stats']
            # don't run through this code if player already received
            if id not in self.ALL_BATTERS or id not in self.ALL_PITCHERS:
                didHeBat = len(statInfo['batting'])
                didHePitch = len(statInfo['pitching'])
                if didHeBat > 0 and id not in self.ALL_BATTERS:
                    throws_bats = self.throwsAndBats(id)
                    self.ALL_BATTERS[id] = {'fullName': personInfo['fullName'], 'bats': throws_bats[1], 'throws': throws_bats[0], 'gmpksInOrder': [], 'gmpks': {}}
                if didHePitch > 0 and id not in self.ALL_PITCHERS:
                    throws_bats = self.throwsAndBats(id)
                    self.ALL_PITCHERS[id] = {'fullName': personInfo['fullName'], 'bats': throws_bats[1], 'throws': throws_bats[0], 'gmpksInOrder': [], 'gmpks': {}}

    # 6.2 IP == 6.67 IP used for calculation purposes
    def convertInnings(self, innings):
        innings = float(innings)
        toAdd = 0
        if (innings % 1) > 0.02:
            if (innings % 1) <= 0.12:
                toAdd = (1.0/3.0)
            elif (innings % 1) <= 0.22:
                toAdd = (2.0/3.0)
        innings = floor(innings) + toAdd
        return innings

    # add current game as game played for all players who had at bats or
    # threw any pitches, place in respective data type
    def addCurrentSeasonStats(self, playerList, gmpk):
        for player in playerList:
            p = playerList.get(player)
            pBats = p['stats']['batting']
            if len(pBats) > 0:
                if pBats['atBats'] > 0:
                    self.ALL_BATTERS[p['person']['id']]['gmpksInOrder'].append(gmpk)
                    playerGames = self.ALL_BATTERS[p['person']['id']]['gmpks']
                    currentGame = playerGames[gmpk] = p['seasonStats']['batting']
                    currentGame['gamesPlayed'] = len(playerGames)
            pThrows = p['stats']['pitching']
            if len(pThrows) > 0:
                if pThrows['pitchesThrown'] > 0:
                    self.ALL_PITCHERS[p['person']['id']]['gmpksInOrder'].append(gmpk)
                    playerGames = self.ALL_PITCHERS[p['person']['id']]['gmpks']
                    currentGame = playerGames[gmpk] = p['seasonStats']['pitching']
                    currentGame['inningsPitched'] = self.convertInnings(float(currentGame['inningsPitched']))
                    currentGame['gamesPlayed'] = len(playerGames)


    def ryanicity(self, starter, game, gmpk):
        if gmpk not in self.ALL_PITCHERS[starter]['gmpksInOrder']:
            print("Pitcher " + str(starter) + " did not pitch game " + str(gmpk))
            return
        score = 50
        gameStats = game['players']['ID'+str(starter)]['stats']['pitching']
        innings = self.convertInnings(gameStats['inningsPitched'])
        score += round(innings*3)
        if (innings - 4) > -.02:
            score += floor(innings - 4 + .02)*2
        score += gameStats['strikeOuts']
        score -= gameStats['hits']*2
        score -= gameStats['earnedRuns']*4
        score -= gameStats['runs']*2
        score -= gameStats['baseOnBalls']
        self.ALL_PITCHERS[starter]['gmpks'][gmpk]['ryanicity'] = score


    # bullpen of every team updated along the way
    def updateBullpen(self, bullpen, player, team, gmpk):
        p = team['players'].get('ID'+str(player))
        p = p['stats']['pitching']

        currGame = bullpen['gmpks'][gmpk]

        # update current stats
        bullpen['currStats'][0] += int(p['runs'])
        bullpen['currStats'][1] += int(p['homeRuns'])
        bullpen['currStats'][2] += int(p['strikeOuts'])
        bullpen['currStats'][3] += int(p['baseOnBalls'])
        bullpen['currStats'][4] += int(p['hits'])
        bullpen['currStats'][5] += int(p['atBats'])
        bullpen['currStats'][8] += self.convertInnings(float(p['inningsPitched']))
        bullpen['currStats'][9] += int(p['blownSaves'])
        bullpen['currStats'][10] += int(p['earnedRuns'])
        bullpen['currStats'][11] += int(p['rbi'])
        try:
            bullpen['currStats'][6] = round((int(bullpen['currStats'][4]) + float(bullpen['currStats'][3])) / int(bullpen['currStats'][5]), 3)
            bullpen['currStats'][7] = round(int(bullpen['currStats'][10]) / float(bullpen['currStats'][8]) * 9, 2)
        except ZeroDivisionError:
            return

        #add running total to current gamepack
        currGame['runs'] = bullpen['currStats'][0]
        currGame['homeRuns'] = bullpen['currStats'][1]
        currGame['strikeOuts'] = bullpen['currStats'][2]
        currGame['baseOnBalls'] = bullpen['currStats'][3]
        currGame['hits'] = bullpen['currStats'][4]
        currGame['atBats'] = bullpen['currStats'][5]
        currGame['obp'] = bullpen['currStats'][6]
        currGame['era'] = bullpen['currStats'][7]
        currGame['inningsPitched'] = bullpen['currStats'][8]
        currGame['blownSaves'] = bullpen['currStats'][9]
        currGame['earnedRuns'] = bullpen['currStats'][10]
        currGame['rbi'] = bullpen['currStats'][11]

    # get stats of last game to put into current gamepack
    def collectivizeBullpen(self, teamName, team, gmpk, awayOrHome):
        id = teamName + " Bullpen"
        if id not in self.ALL_PITCHERS:
            self.ALL_PITCHERS[id] = {'currStats': [0,0,0,0,0,0,0,0,0,0,0,0], 'gmpksInOrder': [], 'gmpks': {}}
        self.ALL_PITCHERS[id]['gmpksInOrder'].append(gmpk)
        self.ALL_PITCHERS[id]['gmpks'][gmpk] = {'gamesPlayed': 0, 'wins': 0, 'runs': 0, 'homeRuns': 0, 'strikeOuts': 0, 'baseOnBalls': 0, 'hits': 0, 'atBats': 0, 'obp': 0, 'era': 0, 'inningsPitched': 0, 'blownSaves': 0, 'earnedRuns': 0, 'rbi': 0}
        for player in team['pitchers'][1:]:
            self.updateBullpen(self.ALL_PITCHERS[id], player, team, gmpk)

        # updating team win percentage
        lengthOfGames = len(self.ALL_PITCHERS[id]['gmpksInOrder']) - 2
        prevGame = self.ALL_PITCHERS[id]['gmpksInOrder'][lengthOfGames]
        self.ALL_PITCHERS[id]['gmpks'][gmpk]['gamesPlayed'] = len(self.ALL_PITCHERS[id]['gmpksInOrder'])


    def rotateThrough10(self, team, stat, gmpk):
        # get team record last 10 games
        w = 0
        for i in team[stat]:
            w += i
        team['gmpks'][gmpk][stat] = w

    # keep updating expected wins to see if it helps model
    def pExpectationLast10(self, teamId, awayOrHome, gmpk, game):
        if teamId not in self.ALL_BATTERS:
            self.ALL_BATTERS[teamId] = {'gamesPlayed': 0, 'wins': 0, 'winsLast10': [], 'runsScored': [], 'runsAllowed': [], 'gmpksInOrder': [], 'gmpks': {}}
        team = self.ALL_BATTERS[teamId]
        team['gmpksInOrder'].append(gmpk)

        team['gmpks'][gmpk] = {'winPercent': 0, 'expectation': 0.0, 'winsLast10': 0, 'runsScored': 0, 'runsAllowed': 0}

        team['gamesPlayed'] += 1
        if self.SCORES[gmpk][2] == awayOrHome:
            team['winsLast10'].append(1)
            team['wins'] += 1
        else:
            team['winsLast10'].append(0)
        if len(team['winsLast10']) == 11:
            del team['winsLast10'][0]

        if team['gmpks'][gmpk]['runsScored'] != 0:
            team['gmpks'][gmpk]['expectation'] = 162*(1 / (1 + team['gmpks'][gmpk]['runsAllowed'] / team['gmpks'][gmpk]['runsScored'])**1.83)
        else:
            # average case
            team['gmpks'][gmpk]['expectation'] = 81.0

        team['runsScored'].append(game['batting']['runs'])
        team['gmpks'][gmpk]['runsScored'] = game['batting']['runs']
        if len(team['runsScored']) == 11:
            del team['runsScored'][0]

        team['runsAllowed'].append(game['pitching']['runs'])
        team['gmpks'][gmpk]['runsAllowed'] = game['pitching']['runs']
        if len(team['runsAllowed']) == 11:
            del team['runsAllowed'][0]

        team['gmpks'][gmpk]['winPercent'] = team['wins'] / team['gamesPlayed']

        self.rotateThrough10(team, 'winsLast10', gmpk)
        if team['gamesPlayed'] != 0:
            # figure out how to deal with games 1-9
            team['gmpks'][gmpk]['winsLast10'] = team['gmpks'][gmpk]['winsLast10'] / 10
        else: team['gmpks'][gmpk]['winsLast10'] = 0
        self.rotateThrough10(team, 'runsScored', gmpk)
        self.rotateThrough10(team, 'runsAllowed', gmpk)

        return 0

    # get all stats from different players and merge them into necessary team stats
    def gatherStats(self):

        # driving code
        with open("team_gameData/" + str(self.year) + "/AllGamesOnce.txt", "r") as f:
            line = f.readline()
            gamesRemaining = 2430
            # count = 0
            # while(count < 1750):
            #     line = f.readline()
            #     count += 1
            #     gamesRemaining -= 1
            while(line != ""):
                gmpk = int(line[:6])
                # print(gmpk)
                game = mlb.boxscore_data(gmpk)
                self.addScore(game, gmpk)
                gamesRemaining -= 1
                if (gamesRemaining % 50 == 0):
                    print("GAMES REMAINING: " + str(gamesRemaining))
                awayTeam = game['teamInfo']['away']['teamName']
                homeTeam = game['teamInfo']['home']['teamName']
                awayPlayerList = game['away']['players']
                homePlayerList = game['home']['players']
                self.addPlayerInfo(awayPlayerList)
                self.addPlayerInfo(homePlayerList)
                self.addCurrentSeasonStats(awayPlayerList, gmpk)
                self.addCurrentSeasonStats(homePlayerList, gmpk)
                awayP = game['away']['pitchers']
                homeP = game['home']['pitchers']
                for p in awayP:
                    self.ryanicity(p, game['away'], gmpk)
                for p in homeP:
                    self.ryanicity(p, game['home'], gmpk)
                self.collectivizeBullpen(awayTeam, game['away'], gmpk, 'Away')
                self.collectivizeBullpen(homeTeam, game['home'], gmpk, 'Home')
                self.pExpectationLast10(awayTeam, "Away", gmpk, game['away']['teamStats'])
                self.pExpectationLast10(homeTeam, "Home", gmpk, game['home']['teamStats'])
                line = f.readline()

            addToPickle(self.ALL_BATTERS, 'batters.pickle', self.year)
            addToPickle(self.ALL_PITCHERS, 'pitchers.pickle', self.year)
            addToPickle(self.SCORES, 'scores.pickle', self.year)

"""
hierarchy:
    teams X cross out for now
    |
    --- players
        |
        --- gamepacks - throws - bats - name
            |
            --- batting list - pitching list

Batters:
        at bats
        'runs'
        'homeRuns'
        'strikeOuts'
        'baseOnBalls'
        'hits'
        'avg'
        atBats'
        'obp'
        'slg'
        'ops'
        rbi'

Pitchers:
        'runs'
        'homeRuns'
        'strikeOuts'
        'baseOnBalls'
        'hits'
        'atBats'
        'obp'
        'era'
        'inningsPitched'
        'wins'
        'losses'
        'holds'
        'blownSaves'
        'earnedRuns'
        'rbi'

        """
# pl = PlayerGatherer(2019)
# print(pl.ALL_BATTERS)
