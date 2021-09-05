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

# Constants
dayCount = 18 # How long the sim will go for


# Read the Json File
fileName = "town1.json"

with open("Generated towns/" + fileName, "r") as townFile:
    townData = json.load(townFile)

dataVersion = townData["general"][0]["dataVersion"]

# Generate constants data 
with open("data/" + dataVersion + "/diversityData.json", "r", encoding='utf-8') as divFile:
    constants = json.load(divFile)



# Interpret the JSON data into lists and classes
peopleList = []
homeList = []
workList = []
locationList = []
unfullWorksites = 0
for person in townData["people"]:
    thisPerson = entities.person(person["age"], person["gender"], person["id"])
    thisPerson.setWorkplace(person["work"])
    thisPerson.addAdress(person["adress"])
    peopleList.append(thisPerson)

for house in townData["house"]:
    thisHouse = entities.house(house["residentCount"], house["id"])
    for resident in range(house["residentCount"]):
        thisId = house["resident" + str(resident)]
        for person in peopleList:
            if person.id == thisId:
                thisHouse.addResident(person)
                break
    homeList.append(thisHouse)

for workPlace in townData["workplace"]:
    thisWorkplace = entities.workPlace(
                    workPlace["essentialStatus"], workPlace["genderRatio"], workPlace["ageDistro"], 
                    workPlace["workerCount"], workPlace["daysCount"], workPlace["id"])

    for worker in range(workPlace["workerCount"] - 1):
        try:
            for person in peopleList:
                if person.id == workPlace["worker" + str(worker)]:
                    thisWorkplace.addWorker(person)
                    break
        except KeyError:
            unfullWorksites += 1

            
    workList.append(thisWorkplace)

for location in townData["location"]:
    thisLocation = entities.otherLocation(location['locType'], location["id"])
    locationList.append(thisLocation)

def findFromId(id, objList):
    for obj in objList:
        if obj.id == id:
            return obj
    return "None"

for person in peopleList:
    person.setWorkplace(findFromId(person.workPlace, workList))
    person.addAdress(findFromId(person.adress, homeList))


# Calculate days off
daysOff = []
for i in range(constants["time"]["daysOffPerWeek"]):
    daysOff.append(7 - i)
daysOff.sort()

weekCount = 0
for day in range(dayCount):
    day += 1
    isWeekend = False
    if day % 7 == 0 or day % 7 in daysOff:
        isWeekend = True

    if not isWeekend: # If its a weekday
        weekDayIndex = day % 7
        if weekDayIndex == 1: # If its the first day of the week    
            for person in peopleList:
                if person.workPlace != "None":
                    person.generateWorkPlan(7 - constants["time"]["daysOffPerWeek"])
        
        for person in peopleList:
            if person.workPlace != "None":
                if person.workPlan[weekDayIndex - 1]:
                    person.goPlace(entities.vist(person.workPlace, person, constants["time"]["dayStart"], constants["time"]["dayEnd"], day))
    
