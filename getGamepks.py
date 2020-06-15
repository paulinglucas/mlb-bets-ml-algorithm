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

teams_id = ({
108: "Angels",
109: "D-backs",
110: "Orioles",
111: "Red Sox",
112: "Cubs",
113: "Reds",
114: "Indians",
115: "Rockies",
116: "Tigers",
117: "Astros",
118: "Royals",
119: "Dodgers",
120: "Nationals",
121: "Mets",
133: "Athletics",
134: "Pirates",
135: "Padres",
136: "Mariners",
137: "Giants",
138: "Cardinals",
139: "Rays",
140: "Rangers",
141: "Blue Jays",
142: "Twins",
143: "Phillies",
144: "Braves",
145: "White Sox",
146: "Marlins",
147: "Yankees",
158: "Brewers"
})

SAVE_PATH = "team_gameData/"

class GamePackGetter:
    def __init__(self, year):
        self.year = year

    # write boxscore of every game of 2019, used for debugging
    def writeGamepks(self):
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

    def returnSznGamepks(self):
        gmpks = []
        games = []
        startDate = '03/20/' + str(self.year)
        endDate = '10/08/' + str(self.year)
        dict = mlb.schedule(date=None, start_date=startDate, end_date=endDate, team="", opponent="", sportId=1, game_id=None)
        for gm in dict:
            # we only want regular season games, or games not postponed/cancelled
            if gm['game_type'] != 'R' or (gm['status'] == "Postponed" or gm['status'] == "Cancelled"):
                continue
            else:
                date_id = gm['game_date'].split("-")
                date = Date(int(date_id[1]), int(date_id[2]), int(date_id[0]))
                lst = [gm['game_id'], teams_id[gm['away_id']], teams_id[gm['home_id']], date]
                if lst[0] not in gmpks:
                    gmpks.append(lst[0])
                    games.append(lst)
        return games

    def writeTeamGmpk(self, tm, gmpk, awayOrHome, date):
        with open(SAVE_PATH + str(self.year) + "/" + tm.replace(" ", "_") + ".txt", "a") as f:
            f.write(awayOrHome + " " + str(gmpk) + ": " + str(date) + "\n")
            return

    # generate list to be sorted later for every team
    def generateLists(self):
        for tm in teams_list:
            fg = open(SAVE_PATH + str(self.year) + "/" + tm.replace(" ", "_") + ".txt", "w")
            fg.write("")
        fg.close()
        open(SAVE_PATH + str(self.year) + "/" + "AllGamesOnce.txt", "w").close()

        gmpks = self.returnSznGamepks()
        with open(SAVE_PATH + str(self.year) + "/" + "AllGamesOnce.txt", "a") as f:
            for gm in gmpks:
                f.write(str(gm[0]) + ": " + str(gm[3]) + "\n")
                self.writeTeamGmpk(gm[1], gm[0], "Away", gm[3])
                self.writeTeamGmpk(gm[2], gm[0], "Home", gm[3])
            return
