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

dataVersion = "1"
#Get Diversity data about population
with open("data/" + dataVersion + "/diversityData.json", "r", encoding='utf-8') as divFile:
    constants = json.load(divFile)




genderFreq = [["male", constants["gender"]["malePercent"]], ["female", constants["gender"]["femalePercent"]]]



maleAgeFreq = getData("data/" + dataVersion + "/Male/ageDistro.csv", True)
femaleAgeFreq = getData("data/" + dataVersion + "/Female/ageDistro.csv", True)
houseDensityFreq = getData("data/" + dataVersion + "/House/densityDistro.csv", True)

def generateId(prefix, val):
    return prefix.upper() + ("0" * (6 - len(str(val)))) + str(val)


housePeopleList = []
# Generate population
for i in range(constants["general"]["population"]):
    gender = generateFromList(genderFreq)
    ageRange = generateFromList(globals()[gender + "AgeFreq"]) # Generate a random age range based off of data, (e.g 0-5)
    ageRange = decode(ageRange)
    age = random.randint(ageRange["minVal"], ageRange["maxVal"]) # Generate a random age in the specified age range
    id = generateId("P", i + 1)

    housePeopleList.append(entities.person(age, gender, id))

workerPeopleList = housePeopleList[:]
jsonPeopleList =  housePeopleList[:]
# Generate Houses
houseList = []
totalHouseCount = 0
while True:
    if totalHouseCount + 6 < constants["general"]["population"]:
        houseDensity = int(generateFromList(houseDensityFreq))
        id = generateId("H", totalHouseCount + 1)
    else:
        houseDensity =  constants["general"]["population"] - totalHouseCount
        id = generateId("H", totalHouseCount + 1)
        houseList.append(entities.house(houseDensity, id))
        totalHouseCount += houseDensity
        break
    
    houseList.append(entities.house(houseDensity, id))
    totalHouseCount += houseDensity


# Populate houses based off houseType and fullness data
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
for person in workerPeopleList:
    if person.age >= constants["age"]["minJobAge"] and person.age < constants["age"]["maxJobAge"]:
        ableCount += 1

# Caculate the average amount of jobs an essential and non essential workplace will create

essentialWorkerProbability = getData("data/" + dataVersion + "/Workplace/essential/workerCountDistro.csv", True)
nonessentialWorkerProbability = getData("data/" + dataVersion + "/Workplace/nonessential/workerCountDistro.csv", True)
labels = ["Essential", "Nonesential"]

for index, probabiltiy in enumerate([essentialWorkerProbability, nonessentialWorkerProbability]):
    t = 0
    for valRange, valFreq in probabiltiy:
        vals = decode(valRange)
        
        valAvg = (vals["minVal"] + vals["maxVal"]) / 2
        t += valAvg * (valFreq / 100)

    constants["jobs"]["avgPosCount" + labels[index]] = t


# Find number of Workplaces required
employment = 1 - (constants["jobs"]["unemployment"] / 100)
for workplace in labels:
    constants["jobs"]["workCount" + workplace] = round(((employment * ableCount) / constants["jobs"]["avgPosCount" + workplace]) * constants["jobs"]["jobBuffer"])

# Generate Work places 
workList = []
#  Get the age distrubution and frequencies for essential non-essential workplaces
constants["jobs"]["essentialAgeDistro"] = getData("data/" + dataVersion + "/Workplace/essential/ageDistro.csv", True) 
constants["jobs"]["nonessentialAgeDistro"] = getData("data/" + dataVersion + "/Workplace/nonessential/ageDistro.csv", True)
essentialCount = 0
for workPlace in range(constants["jobs"]["workCountEssential"]):
    maleRatio = round(generateFromCurve(0.5, constants["jobs"]["maxWorkPlaceGenderRatio"] / 100), 2) * 100 # Generate a random male percentage from Bell Curve
    genderRatio = [["male", maleRatio], ["female", 100 - maleRatio]]
    
    essentialStatus = generateFromList(getData("data/" + dataVersion + "/Workplace/essentialDistro.csv", True))
    ageDistro = getData("data/" + dataVersion + "/Workplace/" + essentialStatus + "/ageDistro.csv", True)

    daysCount = generateFromList(getData("data/" + dataVersion + "/Workplace/"+ essentialStatus + "/daysDistro.csv", True))

    workerCountRange = generateFromList(globals()[essentialStatus + "WorkerProbability"])
    workerCountRange = decode(workerCountRange)
    workerCount = random.randint(int(workerCountRange["minVal"]), int(workerCountRange["maxVal"]))
    if essentialStatus == "essential":
        id = generateId("EW", essentialCount + 1)
        essentialCount += 1
    else:
        id = generateId("NW", workPlace - essentialCount + 1)

    workList.append(entities.workPlace(essentialStatus, genderRatio, ageDistro, workerCount, daysCount, id))



# Workplaces with the lowest worker counts are given first priority in choosing workers
workList.sort(key=lambda x: x.workerCount, reverse = False)
totalJobSpots = 0
# Fill each workplace with workers
for workPlace in workList:
    totalJobSpots += workPlace.workerCount
    for spot in range(workPlace.workerCount): # The first 'pass' to recruit ideal workers based off age and gender
        ageRange = generateFromList(constants["jobs"][workPlace.essentialStatus + "AgeDistro"])
        ageRange = decode(ageRange)
        chosenGender = generateFromList(workPlace.genderRatio)
        for personIndex, person in enumerate(workerPeopleList):
            if person.gender == chosenGender:
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
                
locationCount = round((constants["general"]["population"] / len(houseList)) * len(workList))

locationList = []
for location in range(locationCount):
    id = generateId("L", location)
    locationList.append(entities.otherLocation("Undefined", id))



# Calculate how many people are employed, and how many empty positons there are
employedCount = 0
unEmployedCount = 0
ableCount = 0
for people in jsonPeopleList:
    if people.age >= constants["age"]["minJobAge"] and person.age < constants["age"]["maxJobAge"]:
        if people.workPlace != "None":
            employedCount += 1
        else:
            unEmployedCount += 1
        ableCount += 1
    

# Print out data about 
print("PEOPLE GENERATED = " + str(constants["general"]["population"]))
print("HOUSES MADE = " + str(len(houseList)))
print("PEOPLE NOT IN A HOUSE = " + str(len(housePeopleList)))
print("AVERAGE PEOPLE PER HOUSE = " + str(constants["general"]["population"] / len(houseList)))
print("NUMBER OF WORKPLACES = " + str(len(workList)))
print("WORKER SPOTS AVAILABLE = " + str(totalJobSpots))
print("AVERAGE SPOTS PER WORKPLACE = " + str(round(totalJobSpots / len(workList), 2)))
print("PEOPLE ABLE TO WORK = " + str(ableCount))
print("EMPLOYED COUNT = " + str(employedCount))
print("UNEMPLOYED COUNT (over 15) = " + str(unEmployedCount))
print("UNEMPLOYMENT RATE = " + str(round(unEmployedCount / ableCount, 3)))
print("OTHER LOCATIONS = " + str(locationCount))


# Gather data into a singular dict to write as a JSON file 

jsonDict = {}
for keyWord in ["general", "people", "workplace", "house", "location"]:
    jsonDict[keyWord] = []

jsonDict["general"].append({
    "population": constants["general"]["population"],
    "houseCount": str(len(houseList)),
    "workPlaceCount": str(len(workList)),
    "otherLocationCount": str(len(locationList)),
    "dataVersion": str(dataVersion)
    })

for person in jsonPeopleList:
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

for workPlace in workList:
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
