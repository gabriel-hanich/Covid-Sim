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

startPeriodA = 10
endPeriodA = 15

startPeriodB = 9
endPeriodB = 16

possiblePeriods = []
for i in range(endPeriodA - startPeriodA + 1):
    possiblePeriods.append(i + startPeriodA)

visitedPeriods = []
for i in range(endPeriodB - startPeriodB + 1):
    visitedPeriods.append(i + startPeriodB)

print(possiblePeriods)
print(visitedPeriods)

overLapScore = len(list(set(possiblePeriods).intersection(visitedPeriods)))
print(overLapScore)