import pandas as pd

class Match:
    def __init__(self,id):
        #create and initialize(assign value to) all class variables
        self.id    = id
        self.winner = ''
        self.winnerList = []
        self.loser  = ''
        self.drawMapList = []
        self.drawMapCount = 0
        self.loserMapScore = 0
        self.loserMapList = []
        self.winnerMapScore = 0
        self.winnerMapList = []
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
            elif (row.map_loser != self.loser):
                self.loserMapList.append(row.map_name)
            else:
                self.winnerMapList.append(row.map_name)

        self.loserMapScore = len(list(set(self.loserMapList)))
        self.winnerMapScore = len(list(set(self.winnerMapList)))
        self.drawMapCount = len(list(set(self.drawMapList)))