# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 19:43:23 2020

@author: acp
"""

#v1: add ability to read row date and only take in data from past week
#v1.1-1.2: comment the code
#v1.3: give each player their own dataframe with all rows from the csv that pertain to them
#   separate findMaps function no longer necessary
#   simplify removal of duplicates
#v2 download csv from statslab instead of put in as an argument
#v2.1 made folder/file paths global variables for ease of use
#v2.2 made script consistent in use of single over double quotes
#v2.3 combined scripts into 1 file
#v3 can now run main() on a scheduled interval
#V3.1 used proper convention for global variable naming
#V3.2 combined downloadMatchData and downloadPlayerData for ease
#v4 data autmatically formatted and entered into spreadsheet
#v4.1  script now properly finds the csv links on the statslab webpage rather than having hardcoded values
#v4.2 fixed behavior around player having played the same map twice in a weekend

#requires pip installs of oauth2client, google-api-python-client, google-auth-httplib2, google-auth-oauthlib,
#   schedule, pandas, numpy, beautifulsoup4, wget
#also requires following step 1 here: https://developers.google.com/sheets/api/quickstart/python

import sys
import numpy as np
import pandas as pd
import wget
import shutil, os
from zipfile import ZipFile

#HTML parsing imports
from html.parser import HTMLParser
import urllib.request as urllib2
from bs4 import BeautifulSoup

#google sheets imports
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1LsuN_2Oo4wHV9kMEAulGZEnT1W8B8--A89XMZI8r5LE'

STATS_LAB_URL = 'https://www.overwatchleague.com/en-us/statslab'

UNZIPPED_PLAYER_STATS_DIR = 'unzipped directory that contains playerStats csv'
PLAYER_STATS_ZIP_FILE_PATH = 'file path of downloaded playerStats zip'
PLAYER_STATS_CSV_FILE_PATH = 'file path of playerStats csv'

UNZIPPED_MATCH_STATS_DIR = 'unzipped directory that contains matchStats csv'
MATCH_STATS_ZIP_FILE_PATH = 'file path of downloaded matchStats zip'
MATCH_STATS_CSV_FILE_PATH = 'file path of matchStats csv'

class Player:
    def __init__(self,name):
        #create and initialize(assign value to) all class variables
        self.name          = name
        self.eliminations  = None
        self.totalDamage   = None
        self.healing       = None
        self.allPlayerData = pd.DataFrame()
        self.numOfMaps     = 0        
        self.elimFactor    = 0.5
        self.damageFactor  = 0.001
        self.healingFactor = 0.001        
        
    def allocateStats(self):
        statName = ['Eliminations','All Damage Done','Healing Done']
        elims,damage,healing = None,None,None
        elimList    = []
        damageList  = []
        healingList = []

        #new dataframe of rows with unique date and map name
        uniqueDateMapDF = self.allPlayerData.drop_duplicates(subset=['start_time','map_name'])
        uniqueDateMapList = uniqueDateMapDF.values.tolist()
        self.numOfMaps = len(uniqueDateMapDF.index)
        
        #For each map
        for i in range(len(uniqueDateMapList)):
            #For each row of data
            for row in self.allPlayerData.itertuples(index=False):
                #if row of data has stat we want(elims/damage/healing from statName), store stat in elims/damage/healing
                if uniqueDateMapList[i][0] == row.start_time and uniqueDateMapList[i][1] == row.map_name:
                    if statName[0] == row.stat_name and 'All Heroes' == row.hero_name: #elims
                        elims   = float(row.stat_amount)
                    elif statName[1] == row.stat_name and 'All Heroes' == row.hero_name: #damage
                        damage  = float(row.stat_amount)
                    elif statName[2] == row.stat_name and 'All Heroes' == row.hero_name: #healing
                        healing = float(row.stat_amount)                        
            #If elims/damage/healing was stored (not None), append to list
            if elims != None:
                elimList.append(elims)
            else:
                elimList.append(0)
                
            if damage != None:
                damageList.append(damage)
            else:
                damageList.append(0)
                
            if healing != None:
                healingList.append(healing)
            else:
                healingList.append(0)
            elims,damage,healing = None,None,None       
        
        #Sum elim,damage, and healing scores and sort in descending order
        #zip allows you to associate elements in multiple lists based on their index.  So the result would be
        #[(elimList[1], damageList[1],healingList[1]),(elimList[2]...)]
        #i,j,k then cooresponds to the 3 values in each row for the purposes of iterating over the zipped list to create a new list
        #that totals all points for each map
        self.pointList =[j*self.elimFactor+k*self.damageFactor+l*self.healingFactor for j,k,l in zip(elimList,damageList,healingList)]        
        self.pointList.sort(reverse = True)

        #Take top three scoring entries and round values to 2 decimal places
        #using colon in the list results in a split. [:3] will give you the first 3 values, and [3:] will give you everything after the first 3 values
        self.pointTotal = round(np.sum(self.pointList[:3]),2)

class Match:
    def __init__(self,id):
        #create and initialize(assign value to) all class variables
        self.id    = id
        self.winner = ''
        self.winnerList = []
        self.loser  = ''
        self.loserMapScore = 0
        self.drawMapList = []
        self.drawMapCount = 0
        self.mapList = []
        self.allMatchData = pd.DataFrame()
        
        
    def findMatchInfo(self):
        self.winner = self.allMatchData.match_winner.unique().item()

        #make list of 2 teams in the match, and then check list against the winner to find the loser
        mapLosers = self.allMatchData.map_loser.unique()
        for i in range(len(mapLosers)):
            if mapLosers[i] != self.winner and mapLosers[i] != 'draw':
                self.loser = mapLosers[i]

        #make list of maps that the losing team won to find their score
        for row in self.allMatchData.itertuples(index=False):
            if (row.map_loser == 'draw'):
                self.drawMapList.append(row.map_name)
            elif (row.map_loser != 'draw' and row.map_loser != self.loser):
                self.mapList.append(row.map_name)

        self.loserMapScore = len(list(set(self.mapList)))
        self.drawMapCount = len(list(set(self.drawMapList)))
        
def loopPlayers(playersDF):
    #Create list of players that removes duplicates
    playerList = playersDF.player_name.unique()

    #List of results to pass to insert functions
    playerResultsList = []
    
    #For each OWL player, create an object with class Player() within dictionary 'holder'
    #dictionaries are key:value pairs, where you can look up and get a value based on a key.  
    # In this case, the key is the player name and the value is the Player() object
    holder = {name: Player(name=name) for name in playerList}

    #For each player name in playerList, create a new dataframe that only contains rows from the csv with that player's name in them
    #assign that new dataframe to the cooresponding Player() object
    #call allocateStats() to figure out map score totals
    #then print name, score, and maps played
    for i in range(len(playerList)):
        nameValue = {'player_name': [playerList[i]]}
        #both .any and .all work here, since there's only one value we're searching for per row
        player_row_mask = playersDF.isin(nameValue).any(1)
        singlePlayerDF = playersDF[player_row_mask]
        holder[playerList[i]].allPlayerData = singlePlayerDF
        holder[playerList[i]].allocateStats()
        playerResultsList.append(holder[playerList[i]].name + ',' + str(holder[playerList[i]].pointTotal) + ',' + str(holder[playerList[i]].numOfMaps))

    return playerResultsList

def loopMatches(matchesDF):
    #Create list of matches that removes duplicates
    matchList = matchesDF.match_id.unique()

    #List of results to pass to insert functions
    matchResultsList = []

    #For each OWL match, create an object with class Match() within dictionary 'holder'
    #dictionaries are key:value pairs, where you can look up and get a value based on a key.  
    # In this case, the key is the match id and the value is the Match() object
    holder = {id: Match(id=id) for id in matchList}

    #For each match id in matchList, create a new dataframe that only contains rows from the csv with that match id in them
    #assign that new dataframe to the cooresponding Match() object
    #call findMatchInfo() to figure out map score totals
    for i in range(len(matchList)):
        matchIDValue = {'match_id': [matchList[i]]}
        match_row_mask = matchesDF.isin(matchIDValue).any(1)
        singleMatchDF = matchesDF[match_row_mask]
        holder[matchList[i]].allMatchData = singleMatchDF
        holder[matchList[i]].findMatchInfo()
        if (holder[matchList[i]].drawMapCount > 0):
            matchResultsList.append(holder[matchList[i]].winner + ',' + holder[matchList[i]].loser + ',3 - ' + str(holder[matchList[i]].loserMapScore) + ' - ' + str(holder[matchList[i]].drawMapCount))            
        else:
            matchResultsList.append(holder[matchList[i]].winner + ',' + holder[matchList[i]].loser + ',3 - ' + str(holder[matchList[i]].loserMapScore))

    return matchResultsList

def getPlayerMatchCSVUrl():
    Stage1PlayerUrl = ''
    Stage1MatchUrl = ''

    #open and parse the html
    html_page = urllib2.urlopen(STATS_LAB_URL)
    soup = BeautifulSoup(html_page, 'html.parser')
    prettyStr = str(soup.prettify())

    #look through the html for the links cooresponding to match and player data
    stringList = prettyStr.split()
    for word in stringList:
        if 'phs_2020' in word:
            Stage1PlayerUrl = word
        elif 'match_map_stats' in word:
            Stage1MatchUrl = word

    #edit the returned strings to contain no extra leading or trailing characters
    Stage2PlayerUrl = Stage1PlayerUrl[Stage1PlayerUrl.find('https'):]
    Stage2MatchUrl = Stage1MatchUrl[Stage1MatchUrl.find('https'):]
    FinalPlayerUrl = Stage2PlayerUrl[:Stage2PlayerUrl.find('zip')+3]
    FinalMatchUrl = Stage2MatchUrl[:Stage2MatchUrl.find('zip')+3]

    urlList = [FinalPlayerUrl, FinalMatchUrl]
    return urlList

def downloadPlayerAndMatchData():        
    #delete the old zip file and folder before downloading an updated one, if they exist
    if(os.path.isdir(UNZIPPED_PLAYER_STATS_DIR)):
        shutil.rmtree(UNZIPPED_PLAYER_STATS_DIR)
    if(os.path.isfile(PLAYER_STATS_ZIP_FILE_PATH)):
        os.remove(PLAYER_STATS_ZIP_FILE_PATH)

    if(os.path.isdir(UNZIPPED_MATCH_STATS_DIR)):
        shutil.rmtree(UNZIPPED_MATCH_STATS_DIR)
    if(os.path.isfile(MATCH_STATS_ZIP_FILE_PATH)):
        os.remove(MATCH_STATS_ZIP_FILE_PATH)

    #downloading the zip files
    PlayerMatchUrls = getPlayerMatchCSVUrl()
    playerStatZip = wget.download(PlayerMatchUrls[0], PLAYER_STATS_ZIP_FILE_PATH)
    matchStatZip = wget.download(PlayerMatchUrls[1], MATCH_STATS_ZIP_FILE_PATH)

    #unzip the folders
    with ZipFile(playerStatZip, 'r') as zipPlrObj:
        zipPlrObj.extractall(UNZIPPED_PLAYER_STATS_DIR)
    with ZipFile(matchStatZip, 'r') as zipMtchObj:
        zipMtchObj.extractall(UNZIPPED_MATCH_STATS_DIR)    

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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet

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
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=startingPlayerCell).execute()
        values = result.get('values', [])
        if values:
            startingPlayerCell = 'Week '+ str(i+1) + '!A3'
        else:
            startingMatchCell = 'Week '+ str(i) + '!G14'
            sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=startingPlayerCell, valueInputOption = 'USER_ENTERED', body = player_range_body).execute()
            sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=startingMatchCell, valueInputOption = 'USER_ENTERED', body = match_range_body).execute() 
            break

def main():
    #get latest player and match data from online
    downloadPlayerAndMatchData()

    #Put necessary columns from csv into dataframes
    matchStats = pd.read_csv(MATCH_STATS_CSV_FILE_PATH, parse_dates=['round_start_time'], 
        usecols = ['round_start_time', 'match_id', 'match_winner', 'map_loser','map_name', 'team_one_name', 'team_two_name'])
    playerStats = pd.read_csv(PLAYER_STATS_CSV_FILE_PATH, parse_dates=['start_time'], 
        usecols = ['start_time', 'map_name', 'player_name','stat_name', 'hero_name', 'stat_amount'])

    #eliminate all data from the player/match dataframes that's older than 7 days
    lastWeekendMatchData = matchStats[matchStats['round_start_time']>(pd.to_datetime('now') - pd.DateOffset(days=10))]
    lastWeekendPlayerData = playerStats[playerStats['start_time']>(pd.to_datetime('now') - pd.DateOffset(days=10))]
    #process the data and insert into google sheet
    insertDataInSheet(loopPlayers(lastWeekendPlayerData), loopMatches(lastWeekendMatchData), getSheetsAPI())

if __name__ == '__main__':
    #if script is running, run main() every Wednesday once the new data for the week has been published
    #if you don't want to keep script always running, comment out schedule and the while and uncomment main()
    schedule.every().wednesday.at('12:00').do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
    #main()