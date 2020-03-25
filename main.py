import getGamepks as gm
import gatherPlayers as players
import gameStats as stat
import extractOdds as odds
import createUsableList.py as lst

def main():

    # necessary to get files to read from for gamepack orders
    gm.writeGamepks()
    gm.generateUnsortedLists()
    gm.sortTeamGames()
    gm.deleteUnsortedFiles()
    gm.createGamesInOrder()

    # puts all players into dictionary pickle files,
    # separated by batting and pitching stats
    players.allGamesOnce()
    players.gatherStats(2019)

    # creates team stats leading up to every mlb game ... 2426 games in total
    stat.addInAllStats()

    # get odds of every game, one seemed to not have any ... 2425 game odds
    odds.extractAllOdds()

    # create lists to load into machine learning algorithm
    lst.addToList()
    lst.checkOdds()
    lst.spread()

if __name__ == "__main__":
    main()
