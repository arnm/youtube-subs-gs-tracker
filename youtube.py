import json
import datetime
import string
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

def subs(event, context):
    
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.readonly', 
        'https://spreadsheets.google.com/feeds', 
        'https://www.googleapis.com/auth/drive'
        ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(event['creds'], SCOPES)

    youtube = build('youtube', 'v3', credentials=creds)
    results = {}
    channels = event['channels']

    for channelId in channels:
        request = youtube.channels().list(
            part='statistics',
            id=channelId
        )
        response = request.execute()
        results[channelId] = response['items'][0]['statistics']['subscriberCount']

    client = gspread.authorize(creds)

    googleSheetsConfig = event['googleSheets']
    sheet = client.open(googleSheetsConfig['spreadSheetName']).worksheet(googleSheetsConfig['sheetName'])
    
    
    sheet.update('A1', "Date")
    current_row = len(sheet.col_values(1)) + 1
    sheet.update('A{0}'.format(current_row), str(datetime.date.today()))

    for channel in channels:
        current_col = None
        try:
            cell = sheet.find(channel)
            current_col = cell.col
        except:
            headers = sheet.row_values(1)
            current_col = len(headers) + 1
            sheet.update_cell(1, current_col, '=HYPERLINK("youtube.com/channel/{0}", "{0}")'.format(channel))

        sheet.update_cell(current_row, current_col, results[channel])

    return {
        "message": "Successfully retrieved subs!",
    }
