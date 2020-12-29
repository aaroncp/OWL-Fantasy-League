import numpy as np
import pandas as pd

class Player:
  def __init__(self,name):
      self.name          = name
      self.eliminations  = None
      self.totalDamage   = None
      self.healing       = None
      self.allPlayerData = pd.DataFrame()
      self.numOfMaps     = 0        
      self.elimsFactor   = 1
      self.deathsFactor   = .5 
      self.damageFactor  = 0.001
      self.healingFactor = 0.001        
      
  def allocateStats(self):
      statName = ['Eliminations','Damage Done','Healing Done','Deaths']
      elims,damage,healing,deaths = None,None,None,None
      elimsList, damageList, healingList, deathsList = [],[],[],[]

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
                  elif statName[3] == row.stat_name and 'All Heroes' == row.hero_name: #deaths
                      deaths = float(row.stat_amount)                            
          #If elims/damage/healing was stored (not None), append to list
          if elims != None:
              elimsList.append(elims)
          else:
              elimsList.append(0)                
          if damage != None:
              damageList.append(damage)
          else:
              damageList.append(0)                
          if healing != None:
              healingList.append(healing)
          else:
              healingList.append(0)
          if deaths != None:
              deathsList.append(deaths)
          else:
              deathsList.append(0)
          elims,damage,healing,deaths = None,None,None,None       
      
      #Sum elim,damage, and healing scores and sort in descending order
      #zip allows you to associate elements in multiple lists based on their index.  So the result would be
      #[(elimList[1], damageList[1],healingList[1]),(elimList[2]...)]
      #i,j,k then cooresponds to the 3 values in each row for the purposes of iterating over the zipped list to create a new list
      #that totals all points for each map
      self.pointList =[j*self.elimsFactor+k*self.damageFactor+l*self.healingFactor+m*self.deathsFactor for j,k,l,m in zip(elimsList,damageList,healingList,deathsList)]        
      self.pointList.sort(reverse = True)

      #Take top three scoring entries and round values to 2 decimal places
      #using colon in the list results in a split. [:3] will give you the first 3 values, and [3:] will give you everything after the first 3 values
      self.pointTotal = round(np.sum(self.pointList[:3]),2)