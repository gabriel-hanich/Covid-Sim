from os import truncate
import lib.entities as entities
from lib.readCsv import getData
from lib.generateRandom import generateFromList
from lib.generateRandom import generateKidsCount
from lib.generateRandom import generateFromCurve
from lib.decodeMinMax import decode
from lib.generateRandom import generateTimePeriod
import matplotlib.pyplot as plt
from collections import Counter
import random
import json
import numpy as np
import math
import collections

myPerson = entities.person(45, "Male", "P00001")
covidConstants = {"exposureWeighting": 1, "vaccineWeighting": 1, "ageWeighting": 0.1, "maxExposurebeforeRedunant": 15}

def calculateExposureChance(covidConstants, person, periodsTogether):
    chance = generateFromCurve(0.5, 0.5) + (1 / abs(covidConstants["maxExposurebeforeRedunant"] - periodsTogether) * covidConstants["exposureWeighting"]) 
    if chance > 1:
        chance = 1
    return chance


print(calculateExposureChance(covidConstants, myPerson, 5))
val = {}
val2 = {}

for i in range(10000):
    x = round(calculateExposureChance(covidConstants, myPerson, 2), 1)
    y = round(calculateExposureChance(covidConstants, myPerson, 10), 1)
    if x not in val:
        val[x] = 1
    elif x in val:
        val[x] += 1

    if y not in val2:
        val2[y] = 1
    elif y in val2:
        val2[y] += 1


val = collections.OrderedDict(sorted(val.items()))
val2 = collections.OrderedDict(sorted(val2.items()))


plt.plot(val.keys(), val.values(), label="Exposed for 2 periods")
plt.plot(val2.keys(), val2.values(), label="Exposed for 10 Periods")
plt.legend()
plt.show()
