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

healthScore = 0
fluctutaionScore = 0.1
covidStatus = True

myPerson = entities.person(30, "Male", "P00001", fluctutaionScore)

myPerson.covidStatus = True

for day in range(30):
    if myPerson.newDay() == "DEAD":
        print("DEATH on day " + str(day))
        break
    print(myPerson.healthScore)
