import requests

class CurrentOddsRequest:
    def __init__(self, year):
        try:
            self.ODDS = p.extractPickle('all_odds.pickle', self.year)
        except:
            self.ODDS = {}

    # date entered in yyyy-mm-dd format
    def getDatedEvents(self, date):
        urlBegin = "https://therundown-therundown-v1.p.rapidapi.com/sports/3/events/" + date
        return (requests.get(urlBegin,
            headers={"X-RapidAPI-Host": "therundown-therundown-v1.p.rapidapi.com",
                     "X-RapidAPI-Key": "5a78370093mshd5b6074782ce420p1f9bc7jsn8681310abafa"}).json())

    def getOdds(self, date):
        events = self.getDatedEvents(date)


c = CurrentOddsRequest()
c.getDatedEvents("2020-03-26")
