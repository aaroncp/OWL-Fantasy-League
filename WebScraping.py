#HTML parsing imports
import requests
from html.parser import HTMLParser
import urllib.request as urllib2
from bs4 import BeautifulSoup
import Constant
import wget
import shutil, os
from zipfile import ZipFile

class WebScraping:
  @classmethod
  def downloadPlayerAndMatchData(cls):        
    #delete the old zip file and folder before downloading an updated one, if they exist
    if(os.path.isdir(Constant.UNZIPPED_PLAYER_STATS_DIR)):
        shutil.rmtree(Constant.UNZIPPED_PLAYER_STATS_DIR)
    if(os.path.isfile(Constant.PLAYER_STATS_ZIP_FILE_PATH)):
        os.remove(Constant.PLAYER_STATS_ZIP_FILE_PATH)

    if(os.path.isdir(Constant.UNZIPPED_MATCH_STATS_DIR)):
        shutil.rmtree(Constant.UNZIPPED_MATCH_STATS_DIR)
    if(os.path.isfile(Constant.MATCH_STATS_ZIP_FILE_PATH)):
        os.remove(Constant.MATCH_STATS_ZIP_FILE_PATH)

    #downloading the zip files
    PlayerMatchUrls = cls.getPlayerMatchCSVUrl()
    playerStatZip = wget.download(PlayerMatchUrls[0], Constant.PLAYER_STATS_ZIP_FILE_PATH)
    matchStatZip = wget.download(PlayerMatchUrls[1], Constant.MATCH_STATS_ZIP_FILE_PATH)

    #unzip the folders
    with ZipFile(playerStatZip, 'r') as zipPlrObj:
        zipPlrObj.extractall(Constant.UNZIPPED_PLAYER_STATS_DIR)
    with ZipFile(matchStatZip, 'r') as zipMtchObj:
        zipMtchObj.extractall(Constant.UNZIPPED_MATCH_STATS_DIR)

  @staticmethod
  def getPlayerMatchCSVUrl():
    Stage1PlayerUrl = ''
    Stage1MatchUrl = ''

    #open and parse the html
    html_page = requests.get(Constant.STATS_LAB_URL)
    soup = BeautifulSoup(html_page.text, features='html.parser')
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