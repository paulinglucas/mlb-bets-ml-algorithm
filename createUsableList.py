import gatherPlayers as p

lst = []
outputLst = []


DATA = p.extractPickle("all_games.pickle")
ODDS = p.extractPickle("all_odds.pickle")
LENGTH_OF_LIST = 38

# remember to add the stats into the gamepacks BEFOREHAND
def addToList():
    # game stats
    with open("team_gameData/AllGamesOnce.txt", "r") as f:
        line = f.readline()
        count = 0
        while line != "":
            count += 1
            gmpk = int(line[:6])
            print(gmpk, count)
            listToUse = DATA['gmpks'][gmpk]['away'] + DATA['gmpks'][gmpk]['home']
            lst.append(listToUse)
            line = f.readline()
    # Tigers/White Sox game with zero data
    del lst[1910]
    p.addToPickle(lst, "twoD_list.pickle")

# adds output vectors to odds dictionary to be used as labels for tensorflow
def checkOdds():
    """
    Vector order as follows: [1,2,3,4,5,6]
    1. Win Home
    2. Win Away
    3. Home covered spread
    4. Away covered spread
    5. Over
    6. Under
    """
    with open("team_gameData/AllGamesOnce.txt", "r") as f:
        output_vector = [0,0,0,0,0,0]
        line = f.readline()
        count = 0
        while line != "":
            output_vector = [0,0,0,0,0,0]
            count += 1
            gmpk = int(line[:6])

            if ODDS[gmpk] == "No odds":
                line = f.readline()
                continue

            score = DATA['gmpks'][gmpk]['outcome']
            awayGameOdds = ODDS[gmpk]['away']
            homeGameOdds = ODDS[gmpk]['home']
            oddsToCheck = awayGameOdds
            spreadCheck = score[0] - score[1]
            if score[2] == "Home":
                output_vector[0] = 1
            else:
                output_vector[1] = 1
            if (spreadCheck - float(oddsToCheck[2])) < .1 :
                output_vector[2] = 1
            elif (spreadCheck - float(oddsToCheck[2])) > .1:
                output_vector[3] = 1
            if (float(score[0] + score[1]) - (float(oddsToCheck[6]))) > .2:
                output_vector[4] = 1
            elif (float(score[0] + score[1]) - float(oddsToCheck[6])) < .2:
                output_vector[5] = 1
            outputLst.append(output_vector)
            line = f.readline()
    p.addToPickle(outputLst, "outcome_vectors.pickle")

# gets binary spread output of every game
def spread():
    newLst = []
    lst = p.extractPickle("outcome_vectors.pickle")
    for i in range(len(lst)):
        if lst[i][0] == 1:
            newLst.append([1,0])
        elif lst[i][1] == 1:
            newLst.append([0,1])
    p.addToPickle(newLst, "spreads.pickle")

# used as reference, puts all team stats gathered into convenient CSV
def listToCSV(lst):
    with open("references/2019stats.csv", "w") as f:
        #write in header
        f.write("Away_Avg,Obp,Slg,Ops,Rpg,Hrpg,Sopg,Lh%,P-hand,Era,Whip,Hrp9,")
        f.write("Sop9,Ipg,B-Era,B-Whip,B-Hrp9,B-Sop9,Bspg,Home_Avg,Obp,Slg,Ops,")
        f.write("Rpg,Hrpg,Sopg,Lh%,P-hand,Era,Whip,Hrp9,Sop9,Ipg,B-Era,B-Whip,")
        f.write("B-Hrp9,B-Sop9,Bspg\n")

        #write in stats
        for i in range(len(lst)):
            line = ",".join(map(str, lst[i]))
            f.write(line)
            f.write("\n")
