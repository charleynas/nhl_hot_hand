
'''
author charley nasiedlak
started april 10th 2025 
hot hand rule in hockey
'''


'''
we need to first create a baseline that is unbiased.
we'll do this by generating random strings of saves vs goals
and calculating the save streaks of at least k

we'll then compare it to the streaks in an actual game

i'll use the current season's save percentage to create the
unbiased baseline


secondly i'll use the same basline and calculate the probability
of saving the next shot given you've saved the previous three
*this will only apply if before the three shots there was a goal
'''

import matplotlib.pyplot as plt
import numpy as np
import random
import requests
import matplotlib.image as mpimg

def savesAndGoalsString(shotsFaced, percent):
    saves = int(shotsFaced * percent)
    goals = shotsFaced - saves
    result = ['s'] * saves + ['g'] * goals
    return result

def avgSaveLength(str):
    avgSaveStreak = []
    saveStreak = []
    count = 0
    for shot in str:
        if shot == 's':
            count += 1
        else:
            saveStreak.append(count)
    avgSaveStreak.append(sum(saveStreak)/len(saveStreak))
    return avgSaveStreak

def saveLengthList(str):
    saveStreak = []
    count = 0
    i = 0
    for shot in str:
        if shot == 's':
            count += 1
        else:
            saveStreak.append(count)
            count = 0
    saveStreak.append(count)
    return saveStreak

def howManyStreaks(lst, saveLength, i):
    count = 0
    if i == 1:
        for saves in lst:
            if saves >= saveLength:
                count += 1
    else:
        for saves in lst:
            if saves == saveLength:
                count += 1
    return count/len(lst)

def nextShotBlocked(str):
    #P('s' | 'gss')
    numShots = len(str)
    gssAppears = 0
    followingS = 0
    for i in range(numShots):
        if i+3 < numShots and str[i] == 'g':
            if str[i +1] == 's' and str[i +2] == 's':
                #gss
                #the first two s's are part of the given statement, the final s is what we're calculating
                gssAppears += 1
                if str[i+3] == 's':
                    followingS += 1
    if gssAppears > 0:
        probability = followingS / gssAppears
    else:
        probability = 0
    return probability

def randomBaseline(j, savePercentage, numOfShots):
    #get this season's save percentage for each goalie in the game
    #will have to prompt user because data is private
    
    savePercentage = float(savePercentage)
    numOfShots = int(numOfShots)

    orderdString = savesAndGoalsString(numOfShots, savePercentage)

    
    #y_errs = []

    plt.figure(figsize=(10, 6))

    for iter in range(1000):
        x_vals = []
        y_vals = []

        random.shuffle(orderdString)
        randomString = ''.join(orderdString)
        #print(randomString)
        lengthLst = saveLengthList(randomString)
        #print(lengthLst)

        for i in range(numOfShots+1):
            percentOfStreaks = howManyStreaks(lengthLst, i, j)
            x_vals.append(i)
            y_vals.append(percentOfStreaks)
            #print(str(i) + " " + str(percentOfStreaks))
        #print(x_vals)
        #print(y_vals)
        plt.scatter(x_vals, y_vals, marker='x', linestyle='-', alpha=0.5)

    plt.xticks(np.arange(0, numOfShots+1, 1))
    plt.yticks(np.arange(0, 1.05, 0.05))
    if j == 1:
        plt.xlabel("Save Streak of at least Length k")
    else:
        plt.xlabel("Save Streak of Length k")
    plt.ylabel("Percentage of Steak")
    plt.title("Baseline Save Streaks Model")
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.show() 

def inGameStats(j, gameID, wantedGoalie):
    url = "https://api-web.nhle.com/v1/gamecenter/" + gameID + "/play-by-play"
    response = requests.get(url)
    data = response.json()

    goalies = {}

    #get all plays
    plays = data['plays']
    for idvPlays in plays:
        if idvPlays['typeDescKey'] == 'shot-on-goal' or idvPlays['typeDescKey'] == 'goal':

            
            #this is now every shot on goal including goals
            goalieID = idvPlays['details']['goalieInNetId']
            if goalieID not in goalies:
                goalies[goalieID] = []
            else:
                if idvPlays['typeDescKey'] == 'shot-on-goal':
                    goalies[goalieID].append('s')
                else:
                    goalies[goalieID].append('g') 

    x_vals = []
    y_vals = []

   
    wantedGoalie = int(wantedGoalie)
    savesAndGoals = ''.join(goalies[wantedGoalie]) 
    #print(savesAndGoals)
    shotsOnNet = len(goalies[wantedGoalie])

    lengthLst = saveLengthList(savesAndGoals)
    #print(lengthLst)
    plt.figure(figsize=(10, 6))
    for i in range(shotsOnNet +1):
        percentOfStreaks = howManyStreaks(lengthLst, i, j)
        x_vals.append(i)
        y_vals.append(percentOfStreaks)
        
        plt.scatter(x_vals, y_vals, marker='o', linestyle='-', alpha=0.5)

    plt.xticks(np.arange(0, shotsOnNet+1, 1))
    plt.yticks(np.arange(0, 1.05, 0.05))
    if j == 1:
        plt.xlabel("Save Streak of at least Length k")
    else:
        plt.xlabel("Save Streak of Length k")
    plt.ylabel("Percentage of Steak")
    plt.title("In Game Save Streaks Model")
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.show() 
    

    return x_vals, y_vals 

def randomBaselineProp(savePercentage, numOfShots):
    #get this season's save percentage for each goalie in the game
    #will have to prompt user because data is private
    
    savePercentage = float(savePercentage)
    numOfShots = int(numOfShots)
    orderdString = savesAndGoalsString(numOfShots, savePercentage)

    plt.figure(figsize=(10, 6))
    x_vals = []
    y_vals = []

    for iter in range(100):
        random.shuffle(orderdString)
        randomString = ''.join(orderdString)
        #print(randomString)
        probPercent = nextShotBlocked(randomString)
        #print(probPercent)
        x_vals.append(iter)
        y_vals.append(probPercent)

    plt.scatter(x_vals, y_vals, marker='x', linestyle='-', alpha=0.5)

    plt.xticks(np.arange(0, 101, 5))
    plt.yticks(np.arange(0, 1.05, 0.05))
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.xlabel("trial number")
    plt.ylabel("Percentage of Next Shot Being Saved")
    plt.title("Baseline Probabilities Model")
    
    plt.show() 

def inGameStatsProb(gameID, wantedGoalie):
    url = "https://api-web.nhle.com/v1/gamecenter/" + gameID + "/play-by-play"
    response = requests.get(url)
    data = response.json()

    goalies = {}

    #get all plays
    plays = data['plays']
    for idvPlays in plays:
        if idvPlays['typeDescKey'] == 'shot-on-goal' or idvPlays['typeDescKey'] == 'goal':
            #this is now every shot on goal including goals
            goalieID = idvPlays['details']['goalieInNetId']
            if goalieID not in goalies:
                goalies[goalieID] = []
            else:
                if idvPlays['typeDescKey'] == 'shot-on-goal':
                    goalies[goalieID].append('s')
                else:
                    goalies[goalieID].append('g') 

    x_vals = []
    y_vals = []

    wantedGoalie = int(wantedGoalie)
    savesAndGoals = ''.join(goalies[wantedGoalie]) 

    plt.figure(figsize=(10, 6))
    gameProb = nextShotBlocked(savesAndGoals)
    x_vals.append(0.5)
    y_vals.append(gameProb)
    plt.scatter(x_vals, y_vals, marker='x', linestyle='-', alpha=0.5)

    plt.xticks(np.arange(0, 2, 1))
    plt.yticks(np.arange(0, 1.05, 0.05))

    plt.xlabel("the game")
    plt.ylabel("Percentage of Next Shot Being Saved")
    plt.title("In Game Probability Model")
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.show() 

def mainMethod():
    #**********  MAIN METHOD *********
    savePercentage = input("what's your goalie's save percentage this year? please enter as decimal ")
    numOfShots = input("how many shots did your goalie face in your desired game? ")
    gameID = input("enter the game number id: ")
    wantedGoalie = input("please enter the ID of the goalie of whose stats you want: ")

    #save streak of at least k
    randomBaseline(1, savePercentage, numOfShots)
    inGameStats(1, gameID, wantedGoalie)

    #save streak of k
    randomBaseline(2, savePercentage, numOfShots)
    inGameStats(2, gameID, wantedGoalie)

    randomBaselineProp(savePercentage, numOfShots)
    inGameStatsProb(gameID, wantedGoalie)

mainMethod()