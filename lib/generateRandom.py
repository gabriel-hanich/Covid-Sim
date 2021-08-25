import random
import numpy as np


# Given a list of percentages and variable names
# generate a random variable name with the likelhood of the given percantage
def generateFromList(dataList): 
    maxNum = 0
    for item in dataList:
        maxNum += item[1]
    maxNum = round(maxNum, 5)
    if maxNum != 100:
        print("The percentages do not add up to 100, They add to " + str(maxNum))
        raise ValueError
    
    numbList = []
    currentCount = 0
    for item in dataList:
        numbList.append([currentCount, currentCount + item[1]])
        currentCount += item[1]
    randomNumber = random.randint(1, 100)


    for itemIndex, item in enumerate(numbList):
        if randomNumber > item[0] and randomNumber <= item[1]:
            selectedObj = dataList[itemIndex][0]

    return selectedObj

def generateKidsCount(residentCount):
    if residentCount % 2 == 0: # If number can be easily divided by two
        return int(residentCount / 2)
    else:
        return random.randint(residentCount / 2 - 0.5, residentCount / 2 + 0.5)

def generateFromCurve(center, deviation):
    foundNum = False
    while not foundNum:
        r = np.random.normal(center, deviation, 1)
        r = r[0]
        if r > center - deviation:
            if r < center + deviation:
                foundNum = True
    return r
        