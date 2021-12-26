from typing import OrderedDict

import lib.entities as entities
from lib.readCsv import getData
from lib.generateRandom import generateFromList
from lib.generateRandom import generateKidsCount
from lib.generateRandom import generateFromCurve
from lib.decodeMinMax import decode
from lib.generateRandom import generateTimePeriod
from lib.generateRandom import calculateSymptomStrength
import matplotlib.pyplot as plt
import random
import json
import numpy as np
import math
import collections


def freqFunction(day, age, infectionTime):
    val = day ** 2 + (age * infectionTime)
    return val

def normalizeVal(val, minVal, maxVal):
    try:
        if (val - minVal) / (maxVal - minVal) > 1:
            return 1
        else:
            return (val - minVal) / (maxVal - minVal)
    except ZeroDivisionError:
        return 0


for time in range(5):
    val = {}
    vals = []
    largestVal = 0
    for infectionDays in range(14):
        y = freqFunction(infectionDays, 5 * 5, time)
        vals.append(y)
        if y not in val:
            val[y] = 1
        elif y in val:
            val[y] += 1
        if y > largestVal:
            largestVal = y

    print(largestVal)
    newVals = []
    for val in vals:
        newVals.append(normalizeVal(val, 0, largestVal))


    # val = collections.OrderedDict(sorted(val.items()))

    # plt.plot(val.keys(), val.values())
    plt.plot(newVals, label= str(time))

plt.legend()
plt.show()
