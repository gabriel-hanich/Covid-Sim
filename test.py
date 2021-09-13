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


x = [[True, 65.21739130434783], [False, 34.78260869565217]]

print(generateFromList(x))