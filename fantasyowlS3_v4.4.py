# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 19:43:23 2020

@author: acp
"""

import sys
import numpy as np
import pandas as pd
from Player import Player
from Match import Match
from Gsheets import Gsheets
from WebScraping import WebScraping
import Constant

def main():
    #get latest player and match data from online
    WebScraping.downloadPlayerAndMatchData()

    #Put necessary columns from csv into dataframes
    matchStats = pd.read_csv(Constant.MATCH_STATS_CSV_FILE_PATH, parse_dates=['round_start_time'], 
        usecols = ['round_start_time', 'match_id', 'match_winner', 'map_loser','map_name', 'team_one_name', 'team_two_name'])
    playerStats = pd.read_csv(Constant.PLAYER_STATS_CSV_FILE_PATH, parse_dates=['start_time'], 
        usecols = ['start_time', 'map_name', 'player_name','stat_name', 'hero_name', 'stat_amount'])

    #eliminate all data from the player/match dataframes that's older than 7 days
    givenWeekendMatchDataTop = matchStats[matchStats['round_start_time']>(pd.to_datetime('now') - pd.DateOffset(days=7))]
    #givenWeekendMatchDataBottom = givenWeekendMatchDataTop[givenWeekendMatchDataTop['round_start_time']>(pd.to_datetime('now') - pd.DateOffset(days=5))]
    givenWeekendPlayerDataTop = playerStats[playerStats['start_time']>(pd.to_datetime('now') - pd.DateOffset(days=7))]
    #givenWeekendPlayerDataBottom = givenWeekendPlayerDataTop[givenWeekendPlayerDataTop['start_time']>(pd.to_datetime('now') - pd.DateOffset(days=5))]
    
    #process the data and insert into google sheet
    Gsheets.insertDataInSheet(loopPlayers(givenWeekendPlayerDataTop), loopMatches(givenWeekendMatchDataTop), Gsheets.getSheetsAPI())
        
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
            matchResultsList.append(holder[matchList[i]].winner + ',' + holder[matchList[i]].loser + ',' + str(holder[matchList[i]].winnerMapScore) + ' - ' + str(holder[matchList[i]].loserMapScore) + ' - ' + str(holder[matchList[i]].drawMapCount))            
        else:
            matchResultsList.append(holder[matchList[i]].winner + ',' + holder[matchList[i]].loser + ',' + str(holder[matchList[i]].winnerMapScore) + ' - ' + str(holder[matchList[i]].loserMapScore))

    return matchResultsList

if __name__ == '__main__':
    #if script is running, run main() every Wednesday once the new data for the week has been published
    #schedule.every().wednesday.at('12:00').do(main)
    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)
    main()