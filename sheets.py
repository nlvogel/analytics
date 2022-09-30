from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pprint import pprint

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1CbepUNJarwt_VelDKZHv-DfdLHONXjwicn0eUL0fefA'
RANGE = 'Sheet1!A1'
VALUE_INPUT_OPTION = 'user_entered'.upper()

def main(data_list, gsheet):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'sheets_creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)
        value_range_body = {
            'majorDimension': 'ROWS',
            'range': RANGE,
            'values': data_list
        }
        request = service.spreadsheets().values().update(spreadsheetId=gsheet,
                                                         range=RANGE,
                                                         valueInputOption=VALUE_INPUT_OPTION,
                                                         body=value_range_body)
        response = request.execute()

    except HttpError as err:
        print(err)


def sheets_auth():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'sheets_creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def append_sheet(data_list, gsheet, range):
    try:
        service = build('sheets', 'v4', credentials=sheets_auth())
        value_range_body = {
            'majorDimension': 'ROWS',
            'range': range,
            'values': data_list
        }

        request = service.spreadsheets().values().append(spreadsheetId=gsheet,
                                                         range=range,
                                                         valueInputOption=VALUE_INPUT_OPTION,
                                                         body=value_range_body,
                                                         insertDataOption='INSERT_ROWS')

        response = request.execute()


    except HttpError as err:
        print(err)


# if __name__ == '__main__':
    # main()
