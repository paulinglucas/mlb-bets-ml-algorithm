import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_creation")))

import getGamepks as get
import gatherPlayers as players
import gameStats as stat
import extractOdds as odds
import createUsableList as lst
import statsapi as mlb
import requests
from datetime import date as d
from datetime import timedelta
from send_sms import send_confirmation


YEAR = 2021

# check if game has already been accounted for
def isGameInFile(tm, gmpk):
    with open("team_gameData/{}/".format(YEAR) + get.teams_id[tm].replace(" ", "_") + ".txt", "r") as fh:
        for line in fh:
            if str(gmpk) == line[5:11]:
                return True
        return False

# is game a regular/postseason game, that isnt postponed?
def invalidGame(gmpk, year):
    dict = None
    for x in range(4):
        try:
            dict = mlb.schedule(game_id=gmpk)
            break
        except requests.exceptions.ConnectionError:
            print("Connection Error for looking up game {}".format(gmpk))
            time.sleep(10)
            continue
    if not dict:
        print("Connection Errors. Program Exiting")
        send_confirmation("Failed to update data")
        sys.exit(-1)


    for gm in dict:
        if 'Scheduled' in gm['status']:
            return True
        if gm['game_type'] in 'SEAI' or (gm['status'] == "Postponed" or gm['status'] == "Cancelled" or 'Suspended' in gm['status']) or gm['status'] == "In Progress":
            return True
        if int(gm['game_date'][:4]) < year:
            return True
    return False

# add gamepacks to current year
def setUpGamepks(year):
    gmpks = {}
    yesterday = d.today() - timedelta(days=1)
    buffer = d.today() - timedelta(days=4)
    buffer_dt = buffer.strftime('%Y-%m-%d')
    dt = yesterday.strftime('%Y-%m-%d')

    gm = None
    for x in range(4):
        try:
            gm = mlb.schedule(start_date=buffer_dt, end_date=dt)
            break
        except requests.exceptions.ConnectionError:
            print("Connection Error for looking up schedule")
            time.sleep(10)
            continue
    if not gm:
        print("Connection Errors. Program Exiting")
        send_confirmation("Failed to update data")
        sys.exit(-1)

    for g in gm:
        gmpk = g['game_id']
        tms = []
        tms.append(g['home_id'])
        tms.append(g['away_id'])

        for tm in tms:
            if isGameInFile(tm, gmpk) or invalidGame(gmpk, year):
                continue

            game = None
            for x in range(4):
                try:
                    game = mlb.boxscore_data(gmpk)
                    break
                except requests.exceptions.ConnectionError:
                    print("Connection Error for looking up game {}".format(gmpk))
                    time.sleep(10)
                    continue
            if not game:
                print("Connection Errors. Program Exiting")
                send_confirmation("Failed to update data")
                sys.exit(-1)

            with open("team_gameData/{}/".format(YEAR) + get.teams_id[tm].replace(" ", "_") + ".txt", "a") as f:
                awayOrHome = 'Home'
                if game['teamInfo']['away']['teamName'] == get.teams_id[tm]:
                    awayOrHome = 'Away'
                date = ""
                for label in game['gameBoxInfo']:
                    if len(label) == 1:
                        date = label['label']
                f.write(awayOrHome + " " + str(gmpk) + ": " + date + "\n")

                # in case a different team already had this specific gamepack
                if gmpk not in gmpks:
                    gmpks[gmpk] = date
                else: continue

    # write to AllGamesOnce
    with open("team_gameData/{}/AllGamesOnce.txt".format(YEAR), "a") as f:
        for gmpk in gmpks:
            f.write(str(gmpk) + ": " + gmpks[gmpk] + "\n")

# do data creation and updating throughout the year
def main():
    setUpGamepks(YEAR)

    # puts all players into dictionary pickle files,
    # separated by batting and pitching stats
    pg = players.PlayerGatherer(YEAR)
    pg.gatherStats()

    # creates team stats leading up to every mlb game ... 2426 games in total
    stats = stat.GameStats(YEAR)
    stats.addInAllStats()

    # get odds of every game, one seemed to not have any ... 2425 game odds
    # o = odds.OddsExtractor(YEAR)
    # o.extractAllOdds()

    # create lists to load into machine learning algorithm
    l = lst.ListCreator(YEAR)
    l.addToList()
    # l.checkOdds()
    # l.spread()

    send_confirmation("Successfully updated data for date {}".format(d.today().strftime('%Y-%m-%d')))

if __name__ == "__main__":
    main()

# figure out where to get odds of game
