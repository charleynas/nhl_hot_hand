
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
from scipy.stats import norm

def ww_runs_test(seq):
    unique = list(set(seq))
    if len(unique) != 2:
        return None

    # Map characters to binary
    bin_seq = [1 if char == unique[0] else 0 for char in seq]

    # Count runs
    runs = 1
    for i in range(1, len(bin_seq)):
        if bin_seq[i] != bin_seq[i - 1]:
            runs += 1

    n1 = bin_seq.count(1)
    n2 = bin_seq.count(0)

    if n1 == 0 or n2 == 0:
        return None

    expected = (2 * n1 * n2) / (n1 + n2) + 1
    variance = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / (((n1 + n2) ** 2) * (n1 + n2 - 1))

    z = (runs - expected) / np.sqrt(variance)

    p = norm.cdf(z)  # Too few runs (hot hand)

    return p

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
    #P('s' | 'gsssss')
    numShots = len(str)
    gssAppears = 0
    followingS = 0
    for i in range(numShots):
        if i+6 < numShots and str[i] == 'g':
            if str[i +1] == 's' and str[i +2] == 's' and str[i+3] == 's' and str[i+4] == 's' and str[i+5] == 's':
                #gss
                #the first two s's are part of the given statement, the final s is what we're calculating
                gssAppears += 1
                if str[i+6] == 's':
                    followingS += 1
    if gssAppears > 0:
        probability = followingS / gssAppears
    else:
        probability = 0
    return probability

def goalieList(gameID):
    url = "https://api-web.nhle.com/v1/gamecenter/" + gameID + "/play-by-play"
    response = requests.get(url)
    data = response.json()

    goalies = {}

    #get all plays
    plays = data['plays']
    for idvPlays in plays:
        if idvPlays['typeDescKey'] == 'shot-on-goal' or idvPlays['typeDescKey'] == 'goal':

            try:
                goalieID = idvPlays['details']['goalieInNetId']
            except KeyError:
                return None

            goalieID = idvPlays['details']['goalieInNetId']
            if goalieID not in goalies:
                goalies[goalieID] = []
            else:
                if idvPlays['typeDescKey'] == 'shot-on-goal':
                   goalies[goalieID].append('s')
                else:
                    goalies[goalieID].append('g') 
    return goalies

def randomBaseline(j, savePercentage, numOfShots):
    #get this season's save percentage for each goalie in the game
    #will have to prompt user because data is private
    
    savePercentage = float(savePercentage)
    numOfShots = int(numOfShots)

    orderdString = savesAndGoalsString(numOfShots, savePercentage)

    
    #y_errs = []

    plt.figure(figsize=(10, 6))

    for iter in range(100):
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
        plt.scatter(x_vals, y_vals, marker='x', linestyle='-', alpha=1, color = '#00008B')

    plt.xticks(np.arange(0, numOfShots+1, 1))
    plt.yticks(np.arange(0, 1.05, 0.05))
    plt.ylabel("Percentage of Steak")
    plt.title("Baseline Save Streaks Model")
    plt.grid(True, linestyle='--', alpha=0.4)
    if j == 1:
        plt.xlabel("Save Streak of at least Length k")
        plt.savefig("baseline_plot_streaks_of_at_least_k.png", dpi=300, bbox_inches='tight')
        plt.show()
    else:
        plt.xlabel("Save Streak of Length k")
        plt.savefig("baseline_plot_streaks_of_length_k.png", dpi=300, bbox_inches='tight')
        plt.show()   

def getGames():
    ans = 'yes'
    gameList = []
    while ans == 'yes':
        gameID = input("enter the game number id: ")
        gameList.append(gameID)
        ans = input("do you have another game? (yes or no): ")
    return gameList

def inGameStats(j, wantedGoalie, gameList, numOfShots):
    plt.figure(figsize=(10, 6))
    for gameID in gameList:
        x_vals = []
        y_vals = []
        goalies = goalieList(gameID)
        if goalies == None:
            continue

        else:
            wantedGoalie = int(wantedGoalie)
            savesAndGoals = ''.join(goalies[wantedGoalie]) 
            #print(savesAndGoals)
            shotsOnNet = len(goalies[wantedGoalie])

            lengthLst = saveLengthList(savesAndGoals)
            #print(lengthLst)
            
            for i in range(shotsOnNet +1):
                percentOfStreaks = howManyStreaks(lengthLst, i, j)
                x_vals.append(i)
                y_vals.append(percentOfStreaks)
                
            plt.scatter(x_vals, y_vals, marker='o', linestyle='-', alpha=1, color = '#00008B')

    plt.xticks(np.arange(0, int(numOfShots)+1, 1))
    plt.yticks(np.arange(0, 1.05, 0.05))
    plt.ylabel("Percentage of Steak")
    plt.title("In Game Save Streaks Model")
    plt.grid(True, linestyle='--', alpha=0.4)
    if j == 1:
        plt.xlabel("Save Streak of at least Length k")
        plt.savefig("in_game_plot_streaks_of_at_least_k.png", dpi=300, bbox_inches='tight')
        plt.show() 
    else:
        plt.xlabel("Save Streak of Length k")
        plt.savefig("in_game_plot_streaks_of_length_k.png", dpi=300, bbox_inches='tight')
        plt.show()
        
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

    plt.scatter(x_vals, y_vals, marker='x', linestyle='-', alpha=1, color = '#00008B')

    plt.xticks(np.arange(0, 101, 5))
    plt.yticks(np.arange(0, 1.05, 0.05))
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.xlabel("trial number")
    plt.ylabel("Percentage of Next Shot Being Saved")
    plt.title("Baseline Probabilities Model")
    plt.savefig("baseline_plot_probability.png", dpi=300, bbox_inches='tight')
    
    plt.show() 

def inGameStatsProb(wantedGoalie, gameList):
    plt.figure(figsize=(10, 6))
    i = 0
    x_vals = []
    y_vals = []
    for gameID in gameList:
        i+=1
        goalies = goalieList(gameID)
        if goalies == None:
            print("could not access game " + gameID)
            continue

        else:
            wantedGoalie = int(wantedGoalie)
            savesAndGoals = ''.join(goalies[wantedGoalie]) 

            plt.figure(figsize=(10, 6))
            gameProb = nextShotBlocked(savesAndGoals)
            x_vals.append(i)
            y_vals.append(gameProb)

            p_val = ww_runs_test(savesAndGoals)
            if p_val == None:
                print("can't use")
            elif p_val <= 0.05:
                print("game " + gameID + " had a p-value of " + str(p_val) + " which is stistically significant with the string " + savesAndGoals)
            else:
                print("game " + gameID + " had a p-value of " + str(p_val) + " which is NOT stistically significantwith the string " + savesAndGoals)
        

    plt.scatter(x_vals, y_vals, marker='o', linestyle='-', alpha=1, color = '#00008B')
    plt.xticks(np.arange(0, i+1, 1))
    plt.yticks(np.arange(0, 1.05, 0.05))

    plt.xlabel("the game")
    plt.ylabel("Percentage of Next Shot Being Saved")
    plt.title("In Game Probability Model")
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.savefig("in_game_plot_probability.png", dpi=300, bbox_inches='tight')
    plt.show() 

def mainMethod():
    #**********  MAIN METHOD *********
    savePercentage = input("what's your goalie's save percentage this year? please enter as decimal ")
    numOfShots = input("how many shots did your goalie face in your desired game? ")
    wantedGoalie = input("please enter the ID of the goalie of whose stats you want: ")
    gameList = getGames()

    #save streak of at least k
    randomBaseline(1, savePercentage, numOfShots)
    inGameStats(1, wantedGoalie, gameList, numOfShots)

    #save streak of k
    randomBaseline(2, savePercentage, numOfShots)
    inGameStats(2, wantedGoalie, gameList, numOfShots)

    randomBaselineProp(savePercentage, numOfShots)
    inGameStatsProb(wantedGoalie, gameList)


mainMethod()