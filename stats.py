import statsapi as mlb
import gamepks as gm
from enum import Enum

# HOME_BUFF
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

class Stat(Enum):
    AB = 3
    R = 4
    H = 5
    RBI = 6
    BB = 7
    K = 8
    AVG = 10
    OPS = 11

def createTeamFiles():
    for tm in gm.teams_list:
        fg = open(SAVE_PATH + tm.replace(" ", "_") + ".txt", "w")
        fg.write("")
    fg.close()


def addPlayersToDatabase():
    HOME_BUFF = 0
    for tm in gm.teams_list:
        gmpk = open("output.txt", "r")
        fr = open(gm.SAVE_PATH + tm.replace(" ", "_") + ".txt", "r")
        fw = open(SAVE_PATH + tm.replace(" ", "_") + ".txt", "w")
        while(fr):
            frLine = fr.readline()
            while(gmpk):
                line = gmpk.readline()
                if line[8:14] == frLine[5:11]:
                    if frLine[0:4] == "Home":
                        HOME_BUFF = 82
                    for i in range(3): gmpk.readline()
                    line = gmpk.readline()
                    while line[:20] != " "*20 or line[:20] != "-"*20:
                        digits = "0123456789"
                        line = line[ HOME_BUFF : HOME_BUFF+82 ]
                        if line[0] in digits:
                            line = line.split(" ")
                            while("" in line):
                                line.remove("")
                            if line[1][-1] == ",":
                                line[1] = line[1].replace(",", "_")
                                line[1] = line[1]+line[2]
                                del line[2]
                        print(line)
                        line = gmpk.readline()

addPlayersToDatabase()
