import lib.entities as entities
from lib.readCsv import getData
from lib.generateRandom import generateFromList
from lib.generateRandom import generateKidsCount
from lib.generateRandom import generateFromCurve
from lib.decodeMinMax import decode
import matplotlib.pyplot as plt
from collections import Counter
import random
import numpy as np

constants = {}

#Get Diversity data about population

divFile = open("data/diversityData.txt", "r", encoding='utf-8')
divData = divFile.readlines()
for line in divData:
    try:
        constants[line[1:line.find(">")]] = int(line[line.find(">") + 1:-1])
    except ValueError:
        constants[line[1:line.find(">")]] = float(line[line.find(">") + 1:-1])
        
divFile.close()

genderFreq = [["male", float(constants["male"])], ["female", float(constants["female"])]]

maleAgeFreq = getData("data/Male/ageDistro.csv", True)
femaleAgeFreq = getData("data/Female/ageDistro.csv", True)
houseDensityFreq = getData("data/House/densityDistro.csv", True)

housePeopleList = []
# Generate population
for i in range(constants["population"]):
    gender = generateFromList(genderFreq)
    ageRange = generateFromList(globals()[gender + "AgeFreq"]) # Generate a random age range based off of data, (e.g 0-5)
    ageRange = decode(ageRange)
    age = random.randint(ageRange["minVal"], ageRange["maxVal"]) # Generate a random age in the specified age range
    housePeopleList.append(entities.person(age, gender))

workerPeopleList = housePeopleList[:]
# Generate Houses
houseList = []
totalHouseCount = 0
while True:
    if totalHouseCount + 6 < constants["population"]:
        houseDensity = int(generateFromList(houseDensityFreq))
    else:
        houseDensity =  constants["population"] - totalHouseCount
        houseList.append(entities.house(houseDensity))
        totalHouseCount += houseDensity
        break
    houseList.append(entities.house(houseDensity))
    totalHouseCount += houseDensity


# Populate houses based off houseType and fullness data
for house in houseList:
    if house.residentCount == 1:
        house.setHouseType("single")
        for personIndex, person, in enumerate(housePeopleList):
            if person.age > constants["midStart"]:
                housePeopleList.pop(personIndex)
                house.addResident(person) # If the person is old enough to live by themselves, put them in a single house
                break
    
    else: # If the house contains more then one person
        isKids = False # Find if there are any more kids in the population
        for sampleIndex, samplePerson in enumerate(housePeopleList):
            if samplePerson.age < constants["youngEnd"]:
                isKids = True
                break
        
        if isKids:
            house.setHouseType("family") # If there are kids remaining, the house will become a family type house
            kidList = []
            adultList = []
            for i in range(generateKidsCount(house.residentCount)): # Find a certain amount of kids for the house
                for kidIndex, kid in enumerate(housePeopleList):
                    if kid.age < constants["youngEnd"]:
                        kidList.append(kid)
                        housePeopleList.pop(kidIndex)
                        break
            for i in range(house.residentCount - len(kidList)): # Fill the remaining vacancies with adults
                for peopleIndex, people in enumerate(housePeopleList):
                    if people.age > constants["youngEnd"]:
                        adultList.append(people)
                        housePeopleList.pop(peopleIndex)
                        break
            
            for kid in kidList:
                house.addResident(kid)
            for adult in adultList:
                house.addResident(adult)
        
        else:
            house.setHouseType("group")
            for i in range(house.residentCount):
                for personIndex, person in enumerate(housePeopleList):
                    if person.age >= constants["youngEnd"]:
                        house.addResident(person)
                        housePeopleList.pop(personIndex)
                        break

# Find number of people above Young Catergory
oldCount = 0
for person in workerPeopleList:
    if person.age >= constants["youngEnd"]:
        oldCount += 1

# Caculate the average amount of jobs an essential and non essential workplace will create

essentialWorkerProbability = getData("data/Workplace/essential/workerCountDistro.csv", True)
nonessentialWorkerProbability = getData("data/Workplace/nonessential/workerCountDistro.csv", True)
labels = ["Essential", "Nonesential"]

for index, probabiltiy in enumerate([essentialWorkerProbability, nonessentialWorkerProbability]):
    t = 0
    for valRange, valFreq in probabiltiy:
        vals = decode(valRange)
        
        valAvg = (vals["minVal"] + vals["maxVal"]) / 2
        t += valAvg * (valFreq / 100)

    constants["avgPosCount" + labels[index]] = t


# Find number of Workplaces required
employment = 1 - (constants["unemployment"] / 100)
for workplace in labels:
    constants["workCount" + workplace] = round(((employment * oldCount) / constants["avgPosCount" + workplace]) * constants["jobBuffer"])

# Generate Work places 
workList = []
#  Get the age distrubution and frequencies for essential non-essential workplaces
constants["essentialAgeDistro"] = getData("data/Workplace/essential/ageDistro.csv", True) 
constants["nonessentialAgeDistro"] = getData("data/Workplace/nonessential/ageDistro.csv", True)

for workPlace in range(constants["workCountEssential"]):
    maleRatio = round(generateFromCurve(0.5, constants["maxWorkPlaceGenderRatio"] / 100), 2) * 100 # Generate a random male percentage from Bell Curve
    genderRatio = [["male", maleRatio], ["female", 100 - maleRatio]]
    
    essentialStatus = generateFromList(getData("data/Workplace/essentialDistro.csv", True))
    ageDistro = getData("data/Workplace/" + essentialStatus + "/ageDistro.csv", True)

    workerCountRange = generateFromList(globals()[essentialStatus + "WorkerProbability"])
    workerCountRange = decode(workerCountRange)
    workerCount = random.randint(int(workerCountRange["minVal"]), int(workerCountRange["maxVal"]))

    workList.append(entities.workPlace(essentialStatus, genderRatio, ageDistro, workerCountS))
    

# Workplaces with the lowest worker counts are given first priority in choosing workers
workList.sort(key=lambda x: x.workerCount, reverse = False)

# Fill each workplace with workers
for workPlace in workList:
    for spot in range(workPlace.workerCount): # The first 'pass' to recruit ideal workers based off age and gender
        ageRange = generateFromList(constants[workPlace.essentialStatus + "AgeDistro"])
        ageRange = decode(ageRange)
        chosenGender = generateFromList(workPlace.genderRatio)
        for personIndex, person in enumerate(workerPeopleList):
            if person.gender == chosenGender:
                if person.age > ageRange["minVal"] and person.age <= ageRange["maxVal"]:
                    workPlace.addWorker(person)
                    workerPeopleList.pop(personIndex)
                    break 
    if len(workPlace.workerList) != workPlace.workerCount: # Fill in any gaps that the first pass failed to recruit 
        for spot in range(workPlace.workerCount - len(workPlace.workerList)):
            for peopleIndex, people in enumerate(workerPeopleList):
                if people.age > constants["youngEnd"]:
                    workPlace.addWorker(people)
                    workerPeopleList.pop(peopleIndex)
                    break
                
# Calculate how many people are employed, and how many empty positons there are
totalJobSpots = 0
employedCount = 0
for w in workList:
    employedCount += len(w.workerList)
    totalJobSpots += w.workerCount


print("PEOPLE GENERATED = " + str(constants["population"]))
print("HOUSES MADE = " + str(len(houseList)))
print("PEOPLE NOT IN A HOUSE = " + str(len(housePeopleList)))
print("AVERAGE PEOPLE PER HOUSE = " + str(constants["population"] / len(houseList)))
print("WORKER SPOTS AVAILABLE = " + str(totalJobSpots))
print("PEOPLE ABOVE YOUNG = " + str(oldCount))
print("EMPLOYED COUNT = " + str(employedCount))
print("UNEMPLOYED COUNT (over 15) = " + str(oldCount - employedCount))
print("UNEMPLOYMENT RATE = " + str(round((oldCount - employedCount) / oldCount, 3)))