import lib.entities as entities
from lib.readCsv import getData
from lib.generateRandom import generateFromList
from lib.generateRandom import generateKidsCount
from lib.generateRandom import generateFromCurve
from lib.decodeMinMax import decode
import matplotlib.pyplot as plt
from collections import Counter
import random
import json
import numpy as np

daysToWork = 1
daysWorked = 0
daysToWorkList = []
for i in range(5):
    daysToWorkList.append(0)

for i in range(daysToWork):
    foundVal = False
    while not foundVal:
        pos = random.randint(0, len(daysToWorkList) - 1)
        if daysToWorkList[pos] == 0:
            daysToWorkList[pos] = 1

            foundVal = True