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


def freqFunction(val):
    return val
val = {}

for age in range(100):
    x = freqFunction(1)
    if x not in val:
        val[x] = 1
    elif x in val:
        val[x] += 1


val = collections.OrderedDict(sorted(val.items()))

plt.plot(val.keys(), val.values())

plt.show()
