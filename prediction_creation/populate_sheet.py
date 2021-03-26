import gspread, os, sys
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from datetime import date as get_date
import requests
import re
import statsapi as mlb
import send_sms

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keys")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_creation")))

from keys import ODDS_KEY
import getGamepks as get

## TODO: figure out how spreads and totals are reported in API, add to database to use when updating
def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

def first_empty_val(worksheet):
    str_list = list(filter(None, worksheet.col_values(5)))
    return str(len(str_list)+1)

def returnCorrectGame(dict, teams):
    for game in dict:
        if teams[0] in game['teams'] and teams[1] in game['teams']:
            for site in game['sites']:
                if site['site_key'] == 'bovada':
                    return site['odds']

def editSheet(sheet, msg, confidence, amount, doub=1):
    # ML sheet
    ml = sheet.get_worksheet(0)
    spr = sheet.get_worksheet(1)
    ou = sheet.get_worksheet(2)

    ## extracting odds from api to add to database
    r = requests.get('https://api.the-odds-api.com/v3/odds/?sport=baseball_mlb&region=us&mkt=h2h&mkt=spreads&mkt=totals&apiKey={0}'.format(ODDS_KEY))
    queries = r.json()

    for gm in msg:
        teams = gm[0]
        vs = teams.find(" vs ")
        away = teams[:vs]
        home = teams[vs+4:]
        teams = [away, home]
        oddsQuery = returnCorrectGame(queries['data'], teams)
        ml_odds = oddsQuery['h2h']
        spread_odds = oddsQuery['spreads']
        ou_odds = oddsQuery['totals']

        ## populate row
        if gm[1] is not None and gm[1][1] < confidence:
            row = next_available_row(ml)
            ml.update_cell(row, 1, gm[0])
            ml.update_cell(row, 4, amount*doub)
            ml.update_cell(row, 3, ml_odds[gm[1][0]])
            bet = 'away'
            if ml_odds[gm[1][0]] == 1:
                bet = 'home'
            ml.update_cell(row, 2, bet)
        if gm[2] is not None and gm[2][1] < confidence:
            row = next_available_row(spr)
            spr.update_cell(row, 1, gm[0])
            spr.update_cell(row, 4, amount*doub)
            spr.update_cell(row, 3, ml_odds[gm[2][0]])
            bet = 'away'
            if ml_odds[gm[2][0]] == 1:
                bet = 'home'
            spr.update_cell(row, 2, bet)
        if gm[3] is not None and gm[3][1] < confidence:
            row = next_available_row(ou)
            ou.update_cell(row, 1, gm[0])
            ou.update_cell(row, 4, amount*doub)
            ou.update_cell(row, 3, ml_odds[gm[3][0]])
            bet = 'under'
            if ml_odds[gm[3][0]] == 1:
                bet = 'over'
            ou.update_cell(row, 2, bet)

    return 1

def parseLine(line):
    val = 0
    line = line.strip()[4:]

    idx = line.find('___')
    if idx > 1:
        val = 1

    num = line.strip().replace("___","").replace(",","")
    num = int(num)
    return (val, -num)

def parseMessage(msg):
    lines = msg.splitlines()
    games = []
    i = 0
    lst = []
    while i < len(lines):
        if "vs" in lines[i]:
            lst = [lines[i].strip(), None, None, None]
        elif "ml" in lines[i]:
            lst[1] = parseLine(lines[i])
        elif "spr" in lines[i]:
            lst[2] = parseLine(lines[i])
        elif "o/u" in lines[i]:
            lst[3] = parseLine(lines[i])
        else:
            games.append(lst)
        i += 1
    games.append(lst)
    return games

## figure out winners from bets made
def cycleAndUpdateSheetsWinners():
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # add credentials to the account
    json_file_handle = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keys", "920BeatstheBooks-9bd88d6862a1.json"))
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_handle, scope)

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open('920 Beats Books Spreadsheet')
    my_sheet = client.open('MLB Sheet 2021')

    for i in range(3):
        sheet_instance = sheet.get_worksheet(i)
        my_sheet_instance = my_sheet.get_worksheet(i)

        updateWinners(sheet_instance, i)
        updateWinners(my_sheet_instance, i)

def updateWinners(worksheet, sheet_type):
    curr_row = first_empty_val(worksheet)
    end_of_db = next_available_row(worksheet)
    if curr_row == end_of_db:
        return

    day = get_date.today().strftime('%Y-%m-%d') - timedelta(days=1)
    yesterdays_games = mlb.schedule(dt=day)

    while curr_row != end_of_db:
        curr_game = worksheet.cell(curr_row, 1).value
        for gm in yesterdays_games:
            s = "{} vs {}".format(get.teams_id[gm['away_id']] , get.teams_id[gm['home_id']])
            if s != curr_game or gm['status'] != 'Final':
                continue

            away_score = gm['away_score']
            home_score = gm['home_score']
            bet = worksheet.cell(curr_row, 2).value

            ## update ml
            if sheet_type == 0:
                if (away_score > home_score and bet == 'away') or (home_score > away_score and bet == 'home'):
                    worksheet.update_cell(curr_row, 5, 'Y')
                else:
                    worksheet.update_cell(curr_row, 5, 'N')

            ## update spread
            elif sheet_type == 1:
                bet = bet.split()
                team, handicap = bet[0], float(bet[1])
                if (team == 'away' and (away_score + handicap) > home_score) or (team == 'home' and (home_score + handicap) > away_score):
                    worksheet.update_cell(curr_row, 5, 'Y')
                else:
                    worksheet.update_cell(curr_row, 5, 'N')

            ## update o/u
            elif sheet_type == 2:
                bet = bet.split()
                bet, total = bet[0], float(bet[1])
                runs = away_score + home_score
                if (bet == 'under' and runs < total) or (bet == 'over' and runs > total):
                    worksheet.update_cell(curr_row, 5, 'Y')
                else:
                    worksheet.update_cell(curr_row, 5, 'N')

        curr_row += 1
    return 1

def updateDate():
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # add credentials to the account
    json_file_handle = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keys", "920BeatstheBooks-9bd88d6862a1.json"))
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_handle, scope)

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open('920 Beats Books Spreadsheet')
    my_sheet = client.open('MLB Sheet 2021')

    for i in range(3):
        sheet_instance = sheet.get_worksheet(i)
        my_sheet_instance = my_sheet.get_worksheet(i)

        their_row = next_available_row(sheet_instance)
        my_row = next_available_row(my_sheet_instance)

        sheet_instance.update_cell(their_row, 1, datetime.today().strftime('%m/%d'))
        my_sheet_instance.update_cell(my_row, 1, datetime.today().strftime('%m/%d'))

        sheet_instance.update_cell(their_row, 5, "-")
        my_sheet_instance.update_cell(my_row, 5, "-")

    return 1


def updateSpreadsheets(my_conf, their_conf, msg):
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # add credentials to the account
    json_file_handle = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keys", "920BeatstheBooks-9bd88d6862a1.json"))
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_handle, scope)

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open('920 Beats Books Spreadsheet')
    my_sheet = client.open('MLB Sheet 2021')

    msg = parseMessage(msg)

    editSheet(sheet, msg, -300, 100)
    editSheet(my_sheet, msg, -150, 300, 2)

    return 1

if __name__ == '__main__':
    # ## handle connection errors
    # success = None
    # for x in range(4):
    #     try:
    #         success = cycleAndUpdateSheetsWinners()
    #         break
    #     except requests.exceptions.ConnectionError:
    #         print("Connection Error for updating sheet winners")
    #         time.sleep(10)
    #         continue
    # if not success:
    #     print("Connection Errors. Program Exiting")
    #     send_sms.send_confirmation("Failed to update spreadsheet winners")
    #     sys.exit(-1)
    #
    # ## handle connection errors
    # success = None
    # for x in range(1):
    #     try:
    #         success = updateDate()
    #         break
    #     except requests.exceptions.ConnectionError:
    #         print("Connection Error for updating date")
    #         time.sleep(10)
    #         continue
    # if not success:
    #     print("Connection Errors. Program Exiting")
    #     send_sms.send_confirmation("Failed to update date")
    #     sys.exit(-1)


    # msg = '''White Sox vs Angels
    # ml: ___,-340
    # o/u: -301,___
    #
    # Cubs vs Pirates
    # ml: -310,___
    # spr: -170,___
    # o/u: ___,-234'''

    # parseMessage(msg)
    # updateSpreadsheets(-150, -300, msg)
