import getGamepks as gm
import gatherPlayers as players
import gameStats as stat
import extractOdds as odds
import createUsableList.py as lst
import statsapi as mlb

def setUpGamepks():
    gmpks = {}

    for tm in gm.teams_id:
        gmpk = mlb.last_game(tm)
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

            if gmpk not in gmpks:
                gmpks[gmpk] = date

        with open("team_gameData/2020/AllGamesOnce.txt", "a") as f:
            for gmpk in gmpks:
                f.write(str(gmpk) + ": " + gmpks[gmpk] + "\n")

def main():
    setUpGamepks()

    # puts all players into dictionary pickle files,
    # separated by batting and pitching stats
    pg = players.PlayerGatherer(2020)
    pg.gatherStats(2020)

    # creates team stats leading up to every mlb game ... 2426 games in total
    stats = GameStats(2020)
    stats.addInAllStats()

    # get odds of every game, one seemed to not have any ... 2425 game odds
    # o = OddsExtractor(2020)
    # o.extractAllOdds()

    # create lists to load into machine learning algorithm
    l = ListCreator(2020)
    l.addToList()
    l.checkOdds()
    l.spread()

if __name__ == "__main__":
    main()

# figure out where to get odds of game
