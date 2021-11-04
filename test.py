from typing import OrderedDict
import lib.entities as entities
from lib.readCsv import getData
from lib.generateRandom import generateFromList
from lib.generateRandom import generateKidsCount
from lib.generateRandom import generateFromCurve
from lib.decodeMinMax import decode
from lib.generateRandom import generateTimePeriod
import matplotlib.pyplot as plt
import random
import json
import numpy as np
import math
import collections

with open("data/" + "1" + "/Covid/spread.json", "r", encoding='utf-8') as divFile:
    covidConstants = json.load(divFile)

def findProb(age, covidConstants, fluctuationScore, overlapTime):
    prob = abs(age - 25) ** covidConstants["ageWeighting"] + (overlapTime  ** covidConstants["exposureWeighting"]) + (fluctuationScore * 50) ** covidConstants["exposureWeighting"]
    return prob 

def normalizeVal(val, minVal, maxVal):
    if (val - minVal) / (maxVal - minVal) > 1:
        return 1
    else:
        return (val - minVal) / (maxVal - minVal)


traits = [0, 0.1, 0.15, 0.2]
fluctuationScore = 0.1
overlapTime = 5
ageRange = 100
minVal = 10000

totalXVals = []
totalYVals = []

minVal = 0
maxVal = findProb(100, covidConstants, 0.2, covidConstants["maxExposureBeforeRedundant"]) * covidConstants["bonusWeighting"]
for i in range(len(traits)):
    xVals = []
    yVals = []
    for age in range(ageRange):
        y = round(findProb(age, covidConstants, traits[i], 5), 2)
        xVals.append(age)
        yVals.append(normalizeVal(y, minVal, maxVal))
    totalXVals.append(xVals)
    totalYVals.append(yVals)

for index, item in enumerate(totalXVals):
    plt.plot(item, totalYVals[index], label=traits[index])

plt.ylabel("Probability")
plt.xlabel("Age")

plt.legend()
plt.show()

