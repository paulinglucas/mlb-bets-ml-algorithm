import getGamepks as gm
import gatherPlayers as players

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
    players.gatherStats()

if __name__ == "__main__":
    main()
