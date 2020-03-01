import statsapi as mlb
import gamepks as gm
from enum import Enum
from player import Batter
from player import Pitcher
import sys
import pickle

HOME_BUFF = 0
SAVE_PATH = "team_playerData/"
# open(SAVE_PATH + tm.replace(" ", "_") + ".txt")

inputs_list = ([
"Team BA",
"Team OBP",
"Team SLG",
"Team RPG",
"Team HRPG",
"Starter ERA",
"Starter WHIP",
"Last Start ERA",
"Bullpen ERA"
])

ALL_BATTERS = {}
ALL_PITCHERS = {}

# create hierarchy, batters dictionary that holds teams,
# which holds gamepacks, which holds list of players from gamepack

def initializeTeamDict():
    for tm in gm.teams_list:
        BATTERS[tm] = {}
        PITCHERS[tm] = {}


def addPlayersToDatabase():


    def getTeam(gmpkFile, HOME_BUFF):
        exceptions = ["White", "Blue", "Red"]
        gmpkFile.readline()
        tmLine = gmpkFile.readline()
        tmLine = tmLine[ HOME_BUFF : HOME_BUFF + 79 ]
        tmLine = tmLine.split()
        gmpkFile.readline()
        if tmLine[0] in exceptions:
            tmLine[0] = tmLine[0] + "_" + tmLine[1]
        return tmLine[0]


    def didPlayerSwitch(player, team, batOrPitch, name):
        if player.getTeam() != team:
            newName = name
            while newName[0] != "_":
                newName = newName[1:]
            newName = newName[1:]
            newName = team + "_" + newName
            player.setTeam(team)
            if batOrPitch == "Batter":
                ALL_BATTERS[newName] = ALL_BATTERS.pop(name)
            else:
                ALL_PITCHERS[newName] = ALL_PITCHERS.pop(name)


    def parsePlayer(line, mode):

        def checkCharacters(line):
            if line[0][1] == "-":
                line[0] = line[0][2:]
            if line[0][-1] == ",":
                line[0] = line[0].replace(",", "_")
                line[0] = line[0] + line[1]
                del line[1]
                checkCharacters(line)
            return line


        def checkSpecialBatterNames(line):
            digits = "123456789"
            if line[0] in digits:
                del line[0]
            checkCharacters(line)
            positions = ["P","LF","CF","RF","1B","2B","SS","3B","C","DH", "PH", "PR"]
            if line[1] not in positions:
                line[0] = line[0].replace(",", "")
                line[0] = line[0] + "_" + line[1]
                del line[1]
                checkSpecialBatterNames(line)


        def checkSpecialPitcherNames(line):
            wlhsbs = "WLHSB"
            line = checkCharacters(line)
            # get rid of W or L stat, may use it in future?
            if line[1][1] in wlhsbs:
                del line[1]
                if ")(" in line[1]:
                    del line[1]
                del line[1]
            if line[1][1] != ".":
                line[0] = line[0].replace(",", "")
                line[0] = line[0] + "_" + line[1]
                del line[1]
                checkSpecialPitcherNames(line)


        line = line.split(" ")
        while("" in line):
            line.remove("")
        # messed up gamepk, no stats on anyone
        if line == [] or line[0][2:12] == "**********": return None
        if mode == "Batter":
            checkSpecialBatterNames(line)
        else:
            checkSpecialPitcherNames(line)
        return line


    def includeBatters(gmpk, team, gamepack):
        digits = "123456789"
        line = gmpk.readline()
        line = line[ HOME_BUFF : HOME_BUFF+79 ]
        while (line[2:12] != "----------") and (line[2:12] != "          "):
            line = parsePlayer(line, "Batter")
            for i in range(2,9):
                line[i] = int(line[i])
            line[9], line[10] = float(line[9]), float(line[10])
            # if line[1] == "P":
            #     line[0] = "Pitcher_" + line[0]
            line[0] = team + "_" + line[0]
            if line[0] not in ALL_BATTERS:
                ALL_BATTERS[line[0]] = Batter(line[0], team)
            player = ALL_BATTERS[line[0]]

            # check if program attempts to put new player in existing player list
            didPlayerSwitch(player, team, "Batter", line[0])
            player.updateAfterGame(line)
            player.updateList(gamepack)

            # must do before while loop begins again
            line = gmpk.readline()
            line = line[ HOME_BUFF : HOME_BUFF+79 ]
        return line


    def collectivizeBullpen(gamepack, players, team):
        name = team + "_bullpen"
        if name not in ALL_PITCHERS:
            ALL_PITCHERS[name] = Pitcher(name, team, False)
        bullpen = ALL_PITCHERS[name]
        for player in players:
            bullpen.updateAfterGame(player)
        bullpen.setGP(bullpen.getGP() - (len(players) - 1))
        bullpen.updateList(gamepack)


    def includePitchers(gmpk, fr, team, gamepack):
        divider = "----------"
        spaces = "          "
        line = gmpk.readline()
        prevLine = "***************"
        while (prevLine[2:12] != divider) or (line[2:12] != divider):
            prevLine = line
            line = gmpk.readline()
        gmpk.readline()
        gmpk.readline()
        line = gmpk.readline()[ HOME_BUFF : HOME_BUFF+79 ]

        isStarter = True
        bullpen = []
        while (line[2:12] != divider) and (line[2:12] != spaces):
            line = parsePlayer(line, "Pitcher")
            if line == None: return line
            line[1] = float(line[1])
            for stat in range(2, 8):
                line[stat] = int(line[stat])
            try: line[8] = float(line[8])
            except ValueError: line[8] = 0.0
            line[0] = team + "_" + line[0]
            if line[0] not in ALL_PITCHERS:
                ALL_PITCHERS[line[0]] = Pitcher(line[0], team, isStarter)
            player = ALL_PITCHERS[line[0]]

            didPlayerSwitch(player, team, "Pitcher", line[0])
            player.updateAfterGame(line)
            player.updateList(gamepack)
            if not isStarter:
                bullpen.append(line)
            isStarter = False
            line = gmpk.readline()
            line = line[ HOME_BUFF : HOME_BUFF+79]
        collectivizeBullpen(gamepack, bullpen, team)
        return line


    fr = open(gm.SAVE_PATH + "AllGames.txt", "r")
    gmpk = open("output.txt", "r")
    frLine = fr.readline()
    while(frLine != ""):
        HOME_BUFF = 0
        line = gmpk.readline()
        homeOrAway = frLine[0:4]
        gamepack = frLine[5:11]
        if line[8:14] == gamepack:
            if homeOrAway == "Home":
                HOME_BUFF = 82
            team = getTeam(gmpk, HOME_BUFF)
            includeBatters(gmpk, team, gamepack)
            includePitchers(gmpk, fr, team, gamepack)

            # only do this when pitchers are done
            gmpk.seek(0)
            frLine = fr.readline()



    fr.close()
    gmpk.close()
    addToPickle(ALL_BATTERS, "batters.pickle")
    addToPickle(ALL_PITCHERS, "pitchers.pickle")

def addToPickle(variabl, fname):
    with open(SAVE_PATH + fname, "wb") as f:
        pickle.dump(variabl, f)

def extractPickle(fname):
    with open(SAVE_PATH + fname, "rb") as f:
        return pickle.load(f)

def validatePlayers(fname):
    players = extractPickle(fname)
    count = 0
    for player in players.keys():
        playerList = players[player].getDict()
        if player[-7:] == "bullpen":
            print(player, playerList)
            print()
        # for i in players[player].getGmpks():
            # for j in playerList[i]:
            #     if j < 0:
                    # print("Negative Stat")
                    # sys.exit()

# 1391

# TODO: Refactor!!
# TODO: Add pitchers to database
    # bullpen collectively, starters individual
    # work on bullpen not having so many innings?
# TODO: gather team stats from individual stats (team BA, etc)
# TODO: create list to be fed in correctly

addPlayersToDatabase()
validatePlayers("pitchers.pickle") # 8 for pitcher, 11 for batter
