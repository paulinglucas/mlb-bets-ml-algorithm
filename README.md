## MLB Sports Betting Predictor

#### Maching learning algorithm used to gain an advantage against sports betting books

This repo is designed for one to be able to gather all of the necessary statistics and train a neural network to come up with a more educated guess on the winners of MLB regular season games, for the purpose of profits against the sportsbooks.

#### Libraries / outside data used

- Past odds gathered from database on website: https://sportsbookreviewsonline.com/scoresoddsarchives/mlb/mlboddsarchives.htm
- MLB Data API used to gather player names and hand-dominance
- Python wrapper of MLB API created by Todd Roberts to gather player statistics; link: https://github.com/toddrob99/MLB-StatsAPI/wiki

#### To run the program

1. Run the main.py program to gather statistics necessary

Navigate to directory of repo and run:
```
$ python main.py
```
which will take a few hours to complete. Program gathers all player statistics from seasons 2014 - 2019 (with the exception of 2016 due to data error in used database) to give neural network five seasons of data to train with.

Data gets saved in .pickle files so user does not need to run long program each time it needs to gather data. **Make sure to delete pickle files each time you run main.py program so you don't accidentally overlap data in selected years.**

2. Run the magic.py program to train neural network
```
$ python magic.py
```
This program will prompt you to pick a loss function to train your neural network.
- win_loss will train network to optimize for predicting moneyline bets effectively
- spreads_loss will train network to optimize for predicting spread bets effectively
- ou_loss will train network to optimize for predicting over/under bets effectively

The choice is up to you based on your betting style, however moneyline bets have proven to be most lucrative with this model.

A .hdf5 file is created after training, which allows you to not have to train model each time you wish to predict.

3. Run the current_games.py program every day to gather current season statistics
```
$ python current_games.py
```

This is necessary so the model can use relevant statistics to base its predictions for future current-season games. Make sure it runs every day of a regular season.

3. Run createPrediction.py on future games to get outcome prediction
```
$ python createPrediction.py
```

This program will ask you to input the lineups of both teams in a game you wish to bet on. The model uses individualized statistics for the idea of better accuracy. The statistics used to train and predict are as follows:

Away stats first, followed by home stats:
  - Current team win percentage
  - Teams win percentage over last 10 games
  - P-Expectation of team over the last 10 games, with the idea of tracking the teams hot/cold recency factor
  - Batter stats, including batting average of lineup, on base, slugging, OPS, average home runs/strikeouts per game, etc.
  - Same stats but only taken over last 10 games of lineup
  - Pitching stats, beginning with starting pitcher ofllowed by bullpen, including strikouts per game, ERA, WHIP, Ryanicity, earned run ratio, etc.

The model will spit out a two-element list in the form: [0,1] or [1,0]. If the
1 is the first elelemtn of the list, the model suggests betting on the away team, otherwise it suggests betting on the home team.
