import getGamepks as gm
import gatherPlayers as players
import gameStats as stat
import extractOdds as odds
import createUsableList as lst
import statsapi as mlb

YEAR = 2020

def isGameInFile(tm, gmpk):
    with open("team_gameData/2020/" + gm.teams_id[tm].replace(" ", "_") + ".txt", "rb") as fh:
        for line in fh:
            pass
        last = line
        if gmpk == last[5:11]:
            return True
        else: return False

def invalidGame(gmpk, year):
    dict = mlb.schedule(game_id=gmpk)
    for gm in dict:
        if gm['game_type'] != 'R' or (gm['status'] == "Postponed" or gm['status'] == "Cancelled"):
            return True
        if int(gm['game_date'][:4]) < year:
            return True
    return False



def setUpGamepks(year):
    gmpks = {}

    for tm in gm.teams_id:
        gmpk = mlb.last_game(tm)

        if isGameInFile(tm, gmpk) or invalidGame(gmpk, year):
            continue

        game = mlb.boxscore_data(gmpk)
        with open("team_gameData/2020/" + gm.teams_id[tm].replace(" ", "_") + ".txt", "a") as f:
            awayOrHome = 'Home'
            if game['teamInfo']['away']['teamName'] == gm.teams_id[tm]:
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
        with open("team_gameData/2020/AllGamesOnce.txt", "a") as f:
            for gmpk in gmpks:
                f.write(str(gmpk) + ": " + gmpks[gmpk] + "\n")


def main():
    setUpGamepks(YEAR)

    # puts all players into dictionary pickle files,
    # separated by batting and pitching stats
    pg = players.PlayerGatherer(YEAR)
    pg.gatherStats(YEAR)

    # creates team stats leading up to every mlb game ... 2426 games in total
    stats = GameStats(YEAR)
    stats.addInAllStats()

    # get odds of every game, one seemed to not have any ... 2425 game odds
    # o = OddsExtractor(YEAR)
    # o.extractAllOdds()

    # create lists to load into machine learning algorithm
    l = ListCreator(YEAR)
    l.addToList()

if __name__ == "__main__":
    main()

# figure out where to get odds of game
