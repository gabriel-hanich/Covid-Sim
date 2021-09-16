from abc import abstractproperty
from os import altsep, stat
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

import time
dataVersion = "1"
#Get Diversity data about population
with open("data/" + dataVersion + "/diversityData.json", "r", encoding='utf-8') as divFile:
    constants = json.load(divFile)

def generateId(prefix, val):
    return prefix.upper() + ("0" * (6 - len(str(val)))) + str(val)

maleAgeFreq = getData("data/" + dataVersion + "/Male/ageDistro.csv", True)
femaleAgeFreq = getData("data/" + dataVersion + "/Female/ageDistro.csv", True)
houseDensityFreq = getData("data/" + dataVersion + "/House/densityDistro.csv", True)

traitList = []

population = 0

for gender in ["male", "female"]:
    for ageRange in globals()[gender + "AgeFreq"]:
        freq = ((constants["gender"][gender + "Percent"] / 100) * (ageRange[1] / 100))
        
        traitList.append([gender, ageRange[0], round(freq * constants["general"]["population"])])
        population += round(freq * constants["general"]["population"])


peopleList = []
generatedCount = 0 
for trait in traitList:
    gender = trait[0]
    ageRange = decode(trait[1]) 
    for person in range(trait[-1]):
        generatedCount += 1
        peopleList.append(entities.person(random.randint(ageRange["minVal"], ageRange["maxVal"]), gender, generateId("P", generatedCount)))

# Calculate number of houses required
houseCount = 0 
houseDensityCount = []
for val in houseDensityFreq:
    houseCount += float(val[0]) * (float(val[1]) / 100)
houseCount = round(constants["general"]["population"] / houseCount)
totalAvailable = 0
for density in houseDensityFreq:
    houseDensityCount.append([int(density[0]), round(houseCount * (density[1] / 100))])
    totalAvailable += round(int(density[0]) * round(houseCount * (density[1] / 100)))
count = 0

if totalAvailable != constants["general"]["population"]: # In case of rounding errors correct list to allow ensure each house can be filled
    difference = constants['general']['population'] - totalAvailable
    for index, item in enumerate(houseDensityCount):  
        if int(difference * -1) == int(item[0]) or int(difference) == int(item[0]):
            houseDensityCount[index] = [item[0], item[1] + difference]
        count += houseDensityCount[index][0] * houseDensityCount[index][1]

# Sort people into the houses

houseList = []
houseCount = 0
for val in houseDensityCount:
    for i in range(val[1]):
        houseCount += 1
        id = generateId("H", houseCount)
        houseList.append(entities.house(val[0], id))

housePeopleList = peopleList[:]
# Sort people into the houses (same algorithm as last time)
for house in houseList:
    if house.residentCount == 1:
        house.setHouseType("single")
        for personIndex, person, in enumerate(housePeopleList):
            if person.age > constants["age"]["midStart"]:
                housePeopleList.pop(personIndex)
                person.addAdress(house.id)
                house.addResident(person) # If the person is old enough to live by themselves, put them in a single house
                break
    
    else: # If the house contains more then one person
        isKids = False # Find if there are any more kids in the population
        for sampleIndex, samplePerson in enumerate(housePeopleList):
            if samplePerson.age < constants["age"]["youngEnd"]:
                isKids = True
                break
        
        if isKids:
            house.setHouseType("family") # If there are kids remaining, the house will become a family type house
            kidList = []
            adultList = []
            for i in range(generateKidsCount(house.residentCount)): # Find a certain amount of kids for the house
                for kidIndex, kid in enumerate(housePeopleList):
                    if kid.age < constants["age"]["youngEnd"]:
                        kidList.append(kid)
                        housePeopleList.pop(kidIndex)
                        break
            for i in range(house.residentCount - len(kidList)): # Fill the remaining vacancies with adults
                for peopleIndex, people in enumerate(housePeopleList):
                    if people.age > constants["age"]["youngEnd"]:
                        adultList.append(people)
                        housePeopleList.pop(peopleIndex)
                        break
            
            for kid in kidList:
                house.addResident(kid)
                kid.addAdress(house.id)
            for adult in adultList:
                house.addResident(adult)
                adult.addAdress(house.id)
        
        else:
            house.setHouseType("group")
            for i in range(house.residentCount):
                for personIndex, person in enumerate(housePeopleList):
                    if person.age >= constants["age"]["youngEnd"]:
                        house.addResident(person)
                        person.addAdress(house.id)
                        housePeopleList.pop(personIndex)
                        break

# Find number of people above Young Catergory
ableCount = 0
for person in peopleList:
    if person.age >= constants["age"]["minJobAge"] and person.age < constants["age"]["maxJobAge"]:
        ableCount += 1
placesNeeded = round(ableCount * ((100 - constants["jobs"]["unemployment"]) / 100))

essentialRatio = getData("data/" + dataVersion + "/Workplace/essentialDistro.csv", True)

#Calculate average number of jobs a worksite creates
jobsList = []
siteGeneratedCount = 0
for index, status in enumerate(["essential", "nonessential"]):
    workerProbability = getData("data/" + dataVersion + "/Workplace/" + status + "/workerCountDistro.csv", True)
    count = 0
    for val in workerProbability:
        pair = decode(val[0])
        count += ((pair["minVal"] + pair["maxVal"]) / 2) * (val[1] / 100)
    popul = ableCount * (essentialRatio[index][1] / 100)
    siteCount = round(popul / count)
    ageProb = getData("data/" + dataVersion + "/Workplace/" + status + "/ageDistro.csv", True)
    daysProb = getData("data/" + dataVersion + "/Workplace/" + status + "/daysDistro.csv", True)
    workerCountList = []
    dayList = []
    workerSiteCount = 0
    dayRangeSiteCount = 0
    for prob in workerProbability:
        workerCountList.append([prob[0], round(prob[1] / 100 * siteCount)])
        workerSiteCount += round(prob[1] / 100 * siteCount)
    for dayRange in daysProb:
        dayList.append([dayRange[0], round(dayRange[1] / 100 * siteCount)])
        dayRangeSiteCount += round(dayRange[1] / 100 * siteCount)
    
    print(siteCount)
    if workerSiteCount != siteCount:
        i = random.randint(0, len(workerCountList) - 1)
        workerCountList[i] = [workerCountList[i][0], workerCountList[i][1] + (siteCount - workerSiteCount)]
        workerSiteCount = siteCount

    if dayRangeSiteCount != siteCount:
        i = random.randint(0, len(dayList) - 1)
        dayList[i] = [dayList[i][0], dayList[i][1] + (siteCount - dayList)]
        dayRangeSiteCount = siteCount

    for site in range(siteCount):
        workerIndex = random.randint(0, len(workerCountList) - 1)
        workerRange = workerCountList[workerIndex][0]
        workerCountList[workerIndex][1] -= 1
        if workerCountList[workerIndex][1] == 0:
            workerCountList.pop(workerIndex)
        workerCount = decode(workerRange)
        workerCount = random.randint(workerCount["minVal"], workerCount["maxVal"])

        dayIndex = random.randint(0, len(dayList) - 1)
        dayCount = dayList[dayIndex][0]
        dayList[dayIndex][1] -= 1
        if dayList[dayIndex][1] == 0:
            dayList.pop(dayIndex)
        maleRatio = round(generateFromCurve(0.5, constants["jobs"]["maxWorkPlaceGenderRatio"] / 100), 2) * 100 # Generate a random male percentage from Bell Curve
        genderRatio = [["male", maleRatio], ["female", 100 - maleRatio]]

        siteGeneratedCount += 1
        prefix = "EW"
        if index == 1:
            prefix = "NW"
        id = generateId(prefix, siteGeneratedCount)

        jobsList.append(entities.workPlace(status, genderRatio, ageProb, workerCount, int(dayCount), id))

print(len(jobsList))


