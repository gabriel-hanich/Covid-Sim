from io import SEEK_END
import random
import numpy as np
from numpy.lib.function_base import _parse_input_dimensions


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

    selectedObj = None

    for itemIndex, item in enumerate(numbList):
        if randomNumber > item[0] and randomNumber <= item[1]:
            selectedObj = dataList[itemIndex][0]
    if selectedObj == None:
        selectedObj = dataList[0][0]


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
    if r % 1 == 0:
        r = int(r)
    else:
        r = float(r)
    return r

def generateTimePeriod(timeStart, timeEnd, length): # Generate a random starter time
    if timeEnd - timeStart < length: # If the length of the event is greater then the time allocated, an even distrubution will be achieved
        gap = length - (timeEnd - timeStart) 
        periodStart = (timeStart + gap / 2)
        periodEnd = (timeEnd - gap / 2)
        if gap % 2 != 0:
            periodStart += 0.5
            periodEnd -= 0.5
    else: # Generate a timespan randomly within the time allocated
        latestStart = timeEnd  - length
        timeProbList = []
        for i in range(int(latestStart - timeStart + 1)):
            timeProbList.append([i + timeStart, 100 / (latestStart - timeStart + 1)])
        periodStart = generateFromList(timeProbList)
        periodEnd = periodStart + length
    return {"start": int(periodStart), "end": int(periodEnd)}


        