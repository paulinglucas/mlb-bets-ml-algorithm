import statsapi as mlb
from date import Date
import os

# This file serves as the algorithm necessary to extract data from
# every game using the mlb stats api from Todd Robb. This data will be
# preprocessed to be used in tensorflow to design a keen algorithm that
# should work to make more educated bets than I ever could, because I am
# lazy

BEG_2019_SZN_GAMEPK = 564734
END_2019_SZN_GAMEPK = 567633

teams_list = ([
"Angels",
"D-backs",
"Orioles",
"Red Sox",
"Cubs",
"Reds",
"Indians",
"Rockies",
"Tigers",
"Astros",
"Royals",
"Dodgers",
"Nationals",
"Mets",
"Athletics",
"Pirates",
"Padres",
"Mariners",
"Giants",
"Cardinals",
"Rays",
"Rangers",
"Blue Jays",
"Twins",
"Phillies",
"Braves",
"White Sox",
"Marlins",
"Yankees",
"Brewers"
])

SAVE_PATH = "team_gameData/"

# write boxscore of every game of 2019
def writeGamepks():
    gamepkDivider = "*"*60
    fo = open("references/output.txt", "w")
    for gm in range(BEG_2019_SZN_GAMEPK, END_2019_SZN_GAMEPK+1):
        gm = int(line[5:11])
        try:
            fo.write("gamepk: " + str(gm) + "\n")
            fo.write(mlb.boxscore(gm))
            fo.write(gamepkDivider + "\n")
        except:
            fo.write("No data for gamepk #\n")
            fo.write(gamepkDivider + "\n")

# generate list to be sorted later for every team
def generateUnsortedLists():
    for tm in teams_list:
        fg = open(SAVE_PATH + tm.replace(" ", "_") + "_Unsorted.txt", "w")
        fg.write("")
    fg.close()

    fh = open("references/output.txt", "r")
    for gm in range(BEG_2019_SZN_GAMEPK, END_2019_SZN_GAMEPK+1):
        line = fh.readline()
        gamepk = line[8:14]
        line = fh.readline()
        if line[0:2] == "No":
            fh.readline()
        else:
            line = fh.readline()
            date = ""
            count = 0
            for tm in teams_list:
                if (tm in line[0:14]):
                    ft = open(SAVE_PATH + tm.replace(" ", "_") + "_Unsorted.txt", "a")
                    ft.write("Away " + gamepk + ": ")
                    if(count==0):
                        while fh.readline()[0:5] != "Venue":
                            continue
                        date = fh.readline().strip()
                        count += 1
                    ft.write(date + "\n")
                    ft.close()
                elif (tm in line):
                    ft = open(SAVE_PATH + tm.replace(" ", "_") + "_Unsorted.txt", "a")
                    ft.write("Home " + gamepk + ": ")
                    if(count==0):
                        while fh.readline()[0:5] != "Venue":
                            continue
                        date = fh.readline().strip()
                        count += 1
                    ft.write(date + "\n")
                    ft.close()
            fh.readline()
            fh.readline()
    fh.close()

# sort unsorted list
def sortTeamGames():


    def countLines(tm):
        fa = open(SAVE_PATH + tm.replace(" ", "_") + "_Unsorted.txt", "r")
        lineNum = 0
        while fa.readline():
            lineNum += 1
        fa.close()
        return lineNum


    def getLines(tm):
        fc = open(SAVE_PATH + tm.replace(" ", "_") + "_Unsorted.txt", "r")
        lines = fc.readlines()
        fc.close()
        return lines


    def deleteLine(tm, lines, minLine):
        fd = open(SAVE_PATH + tm.replace(" ", "_") + "_Unsorted.txt", "w")
        for line in lines:
            if line != minLine:
                fd.write(line)
        fd.close()


    for tm in teams_list:
        fo = open(SAVE_PATH + tm.replace(" ", "_") + ".txt", "w")
        lineNum = countLines(tm)
        while lineNum > 0:
            fb = open(SAVE_PATH + tm.replace(" ", "_") + "_Unsorted.txt", "r")
            minLine = fb.readline()
            min = minLine[13:]
            min = min.strip().replace(",", "").replace(":", "").split(" ")
            if min == ['']: continue
            else:
                min = Date(min[0], int(min[1]), int(min[2]))
                for line in fb:
                    date = line[13:]
                    date = date.strip().replace(",", "").replace(":", "").split(" ")
                    date = Date(date[0], int(date[1]), int(date[2]))
                    if (date < min):
                        min = date
                        minLine = line
                # if min > Date("March", 27, 2019) and min < Date("September", 30, 2019):
                fo.write(minLine)
                fb.close()
                lines = getLines(tm)
                deleteLine(tm, lines, minLine)
                lineNum -= 1
        fo.close()

# only using sorted
def deleteUnsortedFiles():
    for tm in teams_list:
        os.remove(SAVE_PATH + tm.replace(" ", "_") + "_Unsorted.txt")


# add in all gamepacks into one file
def createGamesInOrder():


    def insertFileLine(fname, index, line):
        f = open(fname, "r")
        contents = f.readlines()
        f.close()

        contents.insert(index, line)

        f = open(fname, "w")
        f.writelines(contents)
        f.close()


    fo = open(SAVE_PATH + "AllGames.txt", "w")
    fr = open(SAVE_PATH + "Angels.txt", "r")
    contents = fr.readlines()
    fo.writelines(contents)
    fr.close()
    fo.close()
    for tm in teams_list[1:]:
        ft = open(SAVE_PATH + tm.replace(" ", "_") + ".txt", "r")
        line = ft.readline()
        while(line != ""):
            lineNum = 0
            date = line[13:].replace(",", "").split()
            date = Date(date[0], int(date[1]), int(date[2]))
            fp = open(SAVE_PATH + "AllGames.txt", "r")
            otherLine = fp.readline()
            inserted = False
            while(otherLine != ""):
                date2 = otherLine[13:].replace(",", "").split()
                date2 = Date(date2[0], int(date2[1]), int(date2[2]))
                if date < date2 or date == date2:
                    fp.close()
                    insertFileLine(SAVE_PATH + "AllGames.txt", lineNum, line)
                    inserted = True
                    break
                lineNum += 1
                otherLine = fp.readline()
            if not inserted:
                fp.close()
                insertFileLine(SAVE_PATH + "AllGames.txt", lineNum, line)
            line = ft.readline()
        ft.close()
    fp.close()
