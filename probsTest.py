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


def freqFunction(day, age, exposureTime, infectionDuration):
    val = (day - infectionDuration / 2) ** 2
    return val * -1

def normalizeVal(val, minVal, maxVal):
    try:
        if (val - minVal) / (maxVal - minVal) > 1:
            return 1
        else:
            return (val - minVal) / (maxVal - minVal)
    except ZeroDivisionError:
        return 0

infectionDuration = 16

smallestVal = 0
for age in range(10):
    val = {}
    vals = []
    for infectionDays in range(16):
        y = freqFunction(infectionDays, age * 5, 8, infectionDuration)
        vals.append(y)
        if y not in val:
            val[y] = 1
        elif y in val:
            val[y] += 1
        if y < smallestVal:
            smallestVal = y

    newVals = []
    for val in vals:
        val = val + abs(smallestVal)
        newVals.append(normalizeVal(val, 0, abs(smallestVal)))


    # val = collections.OrderedDict(sorted(val.items()))

    # plt.plot(val.keys(), val.values())
    plt.plot(newVals, label= str(age * 5))

plt.legend()
plt.show()
