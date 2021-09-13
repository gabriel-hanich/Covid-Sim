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

# Constants
dayCount = 18 # How long the sim will go for


# Read the Json File
fileName = "town2.json"

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

    for worker in range(int(workPlace["workerCount"] - 1)):
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


shopData = json.load(open("data/" + dataVersion + "/House/shopping.json"))
shopList = [shop for shop in locationList if shop.locType == "shop"]

exerciseList = [exercise for exercise in locationList if exercise.locType == "exercise"]

maleExerciseData = json.load(open("data/" + dataVersion + "/Male/exerciseFreq.json"))
femaleExerciseData = json.load(open("data/" + dataVersion + "/Male/exerciseFreq.json"))

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
            worked = False
            if person.workPlace != "None":
                if person.workPlan[weekDayIndex - 1]: # If someone has to work that day
                    # Generate their working times
                    hoursToWork = round(generateFromCurve(int(person.workPlace.daysCount )+ 3, (int(person.workPlace.daysCount) + 3) / 4))
                    workingTimes = generateTimePeriod(int(constants["time"]["dayStart"]), int(constants["time"]["dayEnd"]), int(hoursToWork))
                    person.goPlace(entities.vist(person.workPlace, person, workingTimes["start"], workingTimes["end"], day))
                    worked = True
            if person.age > constants['age']['youngEnd']:
                if not worked: # If the person is old enough to do the shopping AND NOT at work
                    shopProb = 0
                    if day - person.adress.lastShoppingDay != 0: # If the shopping hasn't already been done that day by another family member
                        shopProb = (day - person.adress.lastShoppingDay) / shopData["avgDaysBetweenShops"]
                    probList = [[True, shopProb * 100], [False, 100 - shopProb * 100]]
                    if generateFromList(probList): # If the person decides to go shopping
                        timeTaken = round(generateFromCurve(shopData["avgTimeForShop"], shopData["timeVar"]))
                        shopTimes = generateTimePeriod(int(constants["time"]["dayStart"]), int(constants["time"]["dayEnd"]), int(timeTaken))
                        
                        shopChosen = shopList[random.randint(0, len(shopList) - 1)]
                        
                        person.goPlace(entities.vist(shopChosen, person, shopTimes["start"], shopTimes["end"], day))
            # Calculate if person can do exercise
            if person.age > globals()[person.gender + "ExerciseData"]["minAge"]:
                exerciseData = globals()[person.gender + "ExerciseData"]
                eProb = 0
                if day - person.dayOfLastExercise != 0: # If they haven't already exercised that day
                    eProb = (day - person.dayOfLastExercise) / (exerciseData["avgDaysBetweenExercise"] + (exerciseData["betweenExerciseVar"] * exerciseData["betweenVarMultiplier"]))
                eList = [[True, eProb * 100], [False, 100 - eProb * 100]]
                if generateFromList(eList): # If person decides to do exercise
                    busyTime = person.findFreePeriods(day)
                    if busyTime["end"] - busyTime["start"] <= exerciseData["latestTime"] - exerciseData["earliestTime"]: # If the person has time in their day to exercise
                        if busyTime["start"] - busyTime["start"] >= exerciseData["latestTime"] - busyTime["end"]: # If they have more time in the morning
                            foundVal = False
                            while not foundVal:
                                exerciseDuration = round(generateFromCurve(exerciseData["avgExerciseTime"], exerciseData["timeVar"]))
                                if exerciseDuration < busyTime["start"] - exerciseData["earliestTime"]:
                                    foundVal = True
                            exerciseTimes = generateTimePeriod(exerciseData["earliestTime"], busyTime["start"], exerciseDuration)
                        else: # If they are more free in the afternoon
                            foundVal = False
                            while not foundVal:
                                exerciseDuration = round(generateFromCurve(exerciseData["avgExerciseTime"], exerciseData["timeVar"]))
                                if exerciseDuration < exerciseData["latestTime"] - busyTime["end"]:
                                    foundVal = True
                            exerciseTimes = generateTimePeriod(busyTime["end"], exerciseData["latestTime"], exerciseDuration)
                        person.updateExercise(day)
                        person.goPlace(entities.vist(exerciseList[random.randint(0, len(exerciseList) - 1)], person, exerciseTimes["start"], exerciseTimes["end"], day))

                        
    
    if isWeekend:
        for person in peopleList:
            if person.age > globals()[person.gender + "ExerciseData"]["minAge"]:
                exerciseData = globals()[person.gender + "ExerciseData"]
                eProb = 0
                if day - person.dayOfLastExercise != 0: # If they haven't already exercised that day
                    eProb = (day - person.dayOfLastExercise) / (exerciseData["avgDaysBetweenExercise"] + (exerciseData["betweenExerciseVar"] * exerciseData["betweenVarMultiplier"]))
                eProb *= exerciseData["weekendmultiplier"]
                eList = [[True, eProb * 100], [False, 100 - eProb * 100]]
                if generateFromList(eList):
                    person.updateExercise(day)
                    exerciseDuration = round(generateFromCurve(exerciseData["avgExerciseTime"], exerciseData["timeVar"]))
                    exerciseTimes = generateTimePeriod(exerciseData["earliestTime"], exerciseData["latestTime"], exerciseDuration)
                    person.goPlace(entities.vist(exerciseList[random.randint(0, len(exerciseList) - 1)], person, exerciseTimes["start"], exerciseTimes["end"], day))
                    

print(peopleList[1].findFreePeriods(2))