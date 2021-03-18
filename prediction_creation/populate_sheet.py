import gspread, os
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

def editSheet(sheet, msg, confidence, amount, doub=1):
    # ML sheet
    ml = sheet.get_worksheet(0)
    spr = sheet.get_worksheet(1)
    ou = sheet.get_worksheet(2)

    for gm in msg:
        if gm[1] is not None and gm[1] < confidence:
            row = next_available_row(ml)
            ml.update_cell(row, 1, gm[0])
            ml.update_cell(row, 3, amount*doub)
        if gm[2] is not None and gm[2] < confidence:
            row = next_available_row(spr)
            spr.update_cell(row, 1, gm[0])
            spr.update_cell(row, 3, amount*doub)
        if gm[3] is not None and gm[3] < confidence:
            row = next_available_row(ou)
            ou.update_cell(row, 1, gm[0])
            ou.update_cell(row, 3, amount*doub)

    return 1

def parseLine(line):
    num = line.strip()[4:].strip().replace("-","").replace(",","")
    num = int(num)
    return -num

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

        sheet_instance.update_cell(next_available_row(sheet_instance), 1, datetime.today().strftime('%m/%d'))
        my_sheet_instance.update_cell(next_available_row(my_sheet_instance), 1, datetime.today().strftime('%m/%d'))


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
    updateDate()
    # msg = '''White Sox vs Angels
    # ml: ---,-340
    # o/u: -301,---
    #
    # Cubs vs Pirates
    # ml: -310,---
    # spr: -170,---
    # o/u: ---,-234'''
    # updateSpreadsheets(-150, -300, msg)
