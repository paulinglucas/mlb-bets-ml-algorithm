import os
import errno
import getGamepks as gm

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__))))

CURR_YEAR = 2021

def prep():
    print(os.getcwd())
    # need year direcotries made for data
    for year in range(2021,CURR_YEAR+1):
        filename = "pickle_files/" + str(year) + "/"
        all_games_filename = "team_gameData/" + str(year) + "/AllGamesOnce.txt"
        text_filename = "team_gameData/" + str(year) + "/TextedGames.txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        open(all_games_filename, "a").close()
        open(text_filename, "a").close()
        for team in gm.teams_list:
            filename3 = "team_gameData/" + str(year) + "/" + team.replace(" ", "_") + ".txt"
            open(filename3, 'a').close()


    # two outlier directories necessary to make this work
    if not os.path.exists(os.path.dirname("models/")):
        try:
            os.makedirs(os.path.dirname("models/"))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    if not os.path.exists(os.path.dirname("pickle_files/1/")):
        try:
            os.makedirs(os.path.dirname("pickle_files/1/"))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise





if __name__ == "__main__":
    prep()
