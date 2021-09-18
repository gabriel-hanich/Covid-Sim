from abc import abstractproperty
from os import altsep, stat

from numpy.core.einsumfunc import _einsum_dispatcher
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
workerPeopleList = peopleList[:]
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
    for prob in workerProbability: # Calculate how many jobs will have each range of employee counts
        workerCountList.append([prob[0], round(prob[1] / 100 * siteCount)])
        workerSiteCount += round(prob[1] / 100 * siteCount)
    for dayRange in daysProb: # Calculate how many jobs will have each specific day per week requirement
        dayList.append([dayRange[0], round(dayRange[1] / 100 * siteCount)])
        dayRangeSiteCount += round(dayRange[1] / 100 * siteCount)
    
    if workerSiteCount != siteCount: # Check for rounding errors
        i = random.randint(0, len(workerCountList) - 1)
        workerCountList[i] = [workerCountList[i][0], workerCountList[i][1] + (siteCount - workerSiteCount)]
        workerSiteCount = siteCount

    if dayRangeSiteCount != siteCount:
        i = random.randint(0, len(dayList) - 1)
        dayList[i] = [dayList[i][0], dayList[i][1] + (siteCount - dayList)]
        dayRangeSiteCount = siteCount

    for site in range(siteCount): # Actually generate the job
        workerIndex = random.randint(0, len(workerCountList) - 1) # Pick the number of employees
        workerRange = workerCountList[workerIndex][0]
        workerCountList[workerIndex][1] -= 1 # Remove it from list to remove duplictaes
        if workerCountList[workerIndex][1] == 0:
            workerCountList.pop(workerIndex) 
        workerCount = decode(workerRange)
        workerCount = random.randint(workerCount["minVal"], workerCount["maxVal"])

        dayIndex = random.randint(0, len(dayList) - 1) # Pick number of days that heed to be worked per week
        dayCount = dayList[dayIndex][0]
        dayList[dayIndex][1] -= 1 # Limit duplicates
        if dayList[dayIndex][1] == 0:
            dayList.pop(dayIndex)
        maleRatio = round(generateFromCurve(0.5, constants["jobs"]["maxWorkPlaceGenderRatio"] / 100), 2) # Generate a random male percentage from Bell Curve
        genderRatio = [["male", maleRatio * workerCount], ["female", 1 - (maleRatio  * workerCount)]]
        ageCount = []
        ageTotal = 0
        for age in ageProb:
            ageCount.append([age[0], round(age[1] / 100 * workerCount)])
            ageTotal += round(age[1] / 100 * workerCount)
        if ageTotal != workerCount:
            ageIndex = random.randint(0, len(ageCount) - 1)
            ageCount[ageIndex][1] += workerCount - ageTotal

        siteGeneratedCount += 1
        prefix = "EW"
        if index == 1:
            prefix = "NW"
        id = generateId(prefix, siteGeneratedCount)

        jobsList.append(entities.workPlace(status, genderRatio, ageCount, workerCount, int(dayCount), id))


# Workplaces with the lowest worker counts are given first priority in choosing workers
jobsList.sort(key=lambda x: x.workerCount, reverse = False)
totalJobSpots = 0
# Fill each workplace with workers
for workPlace in jobsList:
    totalJobSpots += workPlace.workerCount
    for spot in range(workPlace.workerCount): # The first 'pass' to recruit ideal workers based off age and gender
        ageIndex = random.randint(0, len(workPlace.ageDistro) - 1)
        ageRange = workPlace.ageDistro[ageIndex][0]
        workPlace.ageDistro[ageIndex][1] -= 1
        if workPlace.ageDistro[ageIndex][1] == 0:
            workPlace.ageDistro.pop(ageIndex)
        ageRange = decode(ageRange)
        for personIndex, person in enumerate(workerPeopleList):
            if person.age >= ageRange["minVal"] and person.age <= ageRange["maxVal"]:
                workPlace.addWorker(person)
                person.setWorkplace(workPlace.id)
                workerPeopleList.pop(personIndex)
                break 
    if len(workPlace.workerList) != workPlace.workerCount: # Fill in any gaps that the first pass failed to recruit 
        for spot in range(workPlace.workerCount - len(workPlace.workerList)):
            for peopleIndex, people in enumerate(workerPeopleList):
                if people.age >= constants["age"]["minJobAge"] and person.age < constants["age"]["maxJobAge"]:
                    workPlace.addWorker(people)
                    people.setWorkplace(workPlace.id)
                    workerPeopleList.pop(peopleIndex)
                    break

locationTypes = getData("data/" + dataVersion + "/location/typeDiv.csv", True)
locationTypeList = []
locationCount = round((constants["general"]["population"] / len(houseList)) * len(jobsList))
for loc in locationTypes:
    locationTypeList.append([loc[0], round(loc[1] / 100 * locationCount)])

locationList = []
locCount = 0
for locType in locationTypeList:
    for i in range(locType[1]): 
        locCount += 1
        id = generateId("I", locCount)
        locationList.append(entities.otherLocation(locType[0], locCount))

# Find Stats about population
homelessCount = 0
ableCount = 0
employedCount = 0
unEmployedCount = 0
for person in peopleList:
    workingAge = False
    if person.adress[0] != "H":
        homelessCount += 1
    if people.age >= constants["age"]["minJobAge"] and person.age < constants["age"]["maxJobAge"]:
        ableCount += 1
        if person.workPlace == "None":
            unEmployedCount += 1
    if person.workPlace != "None":
        employedCount += 1
missingSpots = 0
for site in jobsList:
    missingSpots += site.workerCount - len(site.workerList)

# Data readouts
print("PEOPLE GENERATED = " + str(len(peopleList)))
print("HOUSES MADE = " + str(len(houseList)))
print("PEOPLE NOT IN A HOUSE = " + str(homelessCount))
print("AVERAGE PEOPLE PER HOUSE = " + str(round(len(peopleList) / len(houseList), 2)))
print("\n")
print("NUMBER OF JOBSITES = " + str(len(jobsList)))
print("NUMBER OF UNFILLED POSITIONS = " + str(missingSpots))
print("AVERAGE PEOPLE EMPLOYED PER JOB SITE = " + str(round(employedCount / len(jobsList), 2)))
print("LABOUR FORCE = " + str(ableCount))
print("NUMBER OF EMPLOYED PEOPLE = " + str(employedCount))
print("PARTICIPATION RATE = " + str(round(employedCount / ableCount, 2)))

# Write the stuff to a file
jsonDict = {}
for keyWord in ["general", "people", "workplace", "house", "location"]:
    jsonDict[keyWord] = []

jsonDict["general"].append({
    "population": constants["general"]["population"],
    "houseCount": str(len(houseList)),
    "workPlaceCount": str(len(jobsList)),
    "otherLocationCount": str(len(locationList)),
    "dataVersion": str(dataVersion)
    })

for person in peopleList:
    jsonDict["people"].append({
    'id': person.id,
    'gender': person.gender,
    'age': person.age,
    'work': person.workPlace,
    'adress': person.adress 
    })

for house in houseList:
    thisData = {
        "id": house.id,
        "residentCount": house.residentCount,
        'type': house.type
    }
    for index, person in enumerate(house.residentList):
        thisData["resident" + str(index)] = person.id
    
    jsonDict["house"].append(thisData)

for workPlace in jobsList:
    thisData = {
        "id": workPlace.id,
        "essentialStatus": workPlace.essentialStatus,
        "ageDistro": workPlace.ageDistro,
        "genderRatio": workPlace.genderRatio,
        "workerCount": workPlace.workerCount,
        "daysCount": workPlace.daysCount
    }
    for index, person in enumerate(workPlace.workerList):
        thisData["worker" + str(index)] = person.id
    
    jsonDict["workplace"].append(thisData)

for location in locationList:
    thisData = {
        "id": location.id,
        "locType": location.locType
    }
    jsonDict["location"].append(thisData)

fileName = input("And what would you like to call the file?\n")
if fileName.lower() != "exit":
    with open("Generated towns/" + fileName + ".json", "w") as finalFile:
        json.dump(jsonDict, finalFile, indent=4)
