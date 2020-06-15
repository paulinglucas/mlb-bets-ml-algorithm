import statsapi as mlb
from date import Date
from getGamepks import GamePackGetter
import gatherPlayers as players
from gatherPlayers import PlayerGatherer
from gameStats import GameStats
from extractOdds import OddsExtractor
from createUsableList import ListCreator

#missing year 2016
BEG_YEAR = 2014
END_YEAR = 2019

def main():
    print()
    print("BEGINNING THE EXTRACTION OF PLAYER DATA BETWEEN YEARS " + str(BEG_YEAR) + " AND " + str(END_YEAR))
    for yr in range(BEG_YEAR, END_YEAR+1):
        print()
        if yr == 2016:
            continue
        print("YEAR: " + str(yr))
        # print("GENERATING GAMEPACK FILES FOR YEAR " + str(yr))
        # g = GamePackGetter(yr)
        # g.generateLists()

        # get player data for specific year
        print()
        print("NOW GATHERING PLAYER STATS FOR YEAR " + str(yr))
        p = PlayerGatherer(yr)
        p.gatherStats()

        # creates team stats leading up to every mlb game ...
        print()
        print("TURNING PLAYER STATS INTO TEAM STATISTICS FOR YEAR " + str(yr))
        stats = GameStats(yr)
        stats.addInAllStats()

        # get odds of every game ...
        print()
        print("EXTRACTING ODDS FOR YEAR " + str(yr))
        o = OddsExtractor(yr)
        o.extractAllOdds()

        # create lists to load into machine learning algorithm
        print()
        print("CREATING LIST OF INPUTS FOR YEAR " + str(yr))
        l = ListCreator(yr)
        l.addToList()
        l.checkOdds()
        l.spread()


if __name__ == "__main__":
    main()
