import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import Constant

class Gsheets:
  @staticmethod
  def getSheetsAPI():
      creds = None

      # The file token.pickle stores the user's access and refresh tokens, and is
      # created automatically when the authorization flow completes for the first
      # time.
      if os.path.exists('token.pickle'):
          with open('token.pickle', 'rb') as token:
              creds = pickle.load(token)
      
      # If there are no (valid) credentials available, let the user log in.
      if not creds or not creds.valid:
          if creds and creds.expired and creds.refresh_token:
              creds.refresh(Request())
          else:
              flow = InstalledAppFlow.from_client_secrets_file(
                  'credentials.json', Constant.SCOPES)
              creds = flow.run_local_server(port=0)
          # Save the credentials for the next run
          with open('token.pickle', 'wb') as token:
              pickle.dump(creds, token)

      service = build('sheets', 'v4', credentials=creds)

      # Call the Sheets API
      # pylint: disable=maybe-no-member
      sheet = service.spreadsheets()    
      return sheet

  @staticmethod
  def insertDataInSheet(playerResults, matchResults, sheet):
      startingPlayerCell = 'Week 1!A3'
      playerResults2D = []
      matchResults2D = []
      #format lists as they'll be displayed in the spreadsheet
      for word in playerResults:
          word = word.split(',')
          playerResults2D.append(word)
      for word in matchResults:
          word = word.split(',')
          matchResults2D.append(word)

      #go through the weekly sheets until the first empty one is found, and then insert player and match data
      player_range_body = {'values':playerResults2D, 'majorDimension':'ROWS'}
      match_range_body = {'values':matchResults2D, 'majorDimension':'ROWS'}
      for i in range (1, 28):
          result = sheet.values().get(spreadsheetId=Constant.SPREADSHEET_ID,
                                  range=startingPlayerCell).execute()
          values = result.get('values', [])
          if values:
              startingPlayerCell = 'Week '+ str(i+1) + '!A3'
          else:
              startingMatchCell = 'Week '+ str(i) + '!H16'
              sheet.values().update(spreadsheetId=Constant.SPREADSHEET_ID,
                  range=startingPlayerCell, valueInputOption = 'USER_ENTERED', body = player_range_body).execute()
              sheet.values().update(spreadsheetId=Constant.SPREADSHEET_ID,
                  range=startingMatchCell, valueInputOption = 'USER_ENTERED', body = match_range_body).execute() 
              break