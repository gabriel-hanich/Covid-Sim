from types import DynamicClassAttribute
import lib.entities as entities
from lib.readCsv import getData
from lib.generateRandom import generateFromList
from lib.generateRandom import generateKidsCount
from lib.generateRandom import generateFromCurve
from lib.generateRandom import calculateExposureChance
from lib.generateRandom import calculateExposureChanceLegacy
from lib.generateRandom import normalizeVal
from lib.decodeMinMax import decode
from lib.generateRandom import generateTimePeriod
import matplotlib.pyplot as plt
from collections import Counter
import os
import random
import json
from perlin_noise import PerlinNoise

# Constants
dayCount = 30  # How long the sim will go for
doRandomStarter = False
saveDayData = False  # Whether to save the stats for each sim day or not to a .JSON file
writeFileDaily = True # Whether to WRITE this data to a file each day (May increase load time however data will be saved if program crashes)
startingCases = 2
startingIndex = 198

thingsToPlot = ["totalActiveInfections", "dailyCases", "dailyDeaths", "dailyHotSpots"]

# Read the Json File
townName = "myTown"
iterationName = "iteration2"

with open("Generated towns/" + townName + "/" + townName + ".json", "r") as townFile:
    townData = json.load(townFile)

dataVersion = townData["general"][0]["dataVersion"]

# Generate constants data
with open("data/" + dataVersion + "/diversityData.json", "r", encoding='utf-8') as divFile:
    constants = json.load(divFile)

with open("data/" + dataVersion + "/Covid/spread.json", "r", encoding='utf-8') as divFile:
    covidConstants = json.load(divFile)


# Interpret the JSON data into lists and classes
peopleList = []
homeList = []
workList = []
locationList = []
unfullWorksites = 0
for person in townData["people"]:
    thisPerson = entities.person(
        person["age"], person["gender"], person["id"], float(person["fluctuationScore"]))
    thisPerson.setWorkplace(person["work"])
    thisPerson.addAdress(person["adress"])
    thisPerson.setCovidConstants(covidConstants)
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
    if(person.age < 15):
        if(person.workPlace != "None"):
            print("Oh dear, child labor detected")

shopData = json.load(open("data/" + dataVersion + "/House/shopping.json"))
shopList = [shop for shop in locationList if shop.locType == "shop"]

exerciseList = [
    exercise for exercise in locationList if exercise.locType == "exercise"]

maleExerciseData = json.load(
    open("data/" + dataVersion + "/Male/exerciseFreq.json"))
femaleExerciseData = json.load(
    open("data/" + dataVersion + "/Male/exerciseFreq.json"))


allLocations = homeList + workList + locationList

# Infect starting people with COVID
if doRandomStarter:
    print("STARTER INFECTION ATTRIBUTES")
    for _ in range(startingCases):
        infectedPerson = peopleList[random.randint(0, len(peopleList) - 1)]
        infectedPerson.setCovid(True, 0)
        try:
            print("PERSON ID:" + str(infectedPerson.id)
                  + "\nAGE " + str(infectedPerson.age)
                  + "\nHOME " + str(infectedPerson.adress.id)
                  + "\nWORKPLACE " + str(infectedPerson.workPlace.id) + "\n")
        except AttributeError:
            print("PERSON ID:" + str(infectedPerson.id)
                  + "\nAGE " + str(infectedPerson.age)
                  + "\nHOME " + str(infectedPerson.adress.id)
                  + "\nNO JOB\n")
else:
    print("STARTER INFECTION ATTRIBUTES")
    for i in range(startingCases):
        peopleList[i + startingIndex].getCovid(
            0, covidConstants["maxExposureBeforeRedundant"])
        try:
            print("PERSON ID:" + str(peopleList[i + startingIndex].id)
                  + "\nAGE " + str(peopleList[i + startingIndex].age)
                  + "\nHOME " + str(peopleList[i + startingIndex].adress.id)
                  + "\nWORKPLACE " + str(peopleList[i + startingIndex].workPlace.id) + "\n")
        except AttributeError:
            print("AA")
            print("PERSON ID:" + str(peopleList[i + startingIndex].id)
                  + "\nAGE " + str(peopleList[i + startingIndex].age)
                  + "\nHOME " + str(peopleList[i + startingIndex].adress.id)
                  + "\nNO JOB\n")

# Calculate the highest possible score someone can have for getting COVID (highest number possible from calculateExposure())
maxPossibleCovidScore = calculateExposureChanceLegacy(
    covidConstants["maxPossibleAge"], covidConstants, covidConstants["maxExposureBeforeRedundant"], covidConstants["maxPossibleFlucScore"])
maxPossibleCovidSymptomScore = 200

covidConstants["maxPossibleCovidScore"] = maxPossibleCovidScore
covidConstants["maxPossibleCovidSymptomScore"] = maxPossibleCovidSymptomScore

lastDeathCount = 0
lastInfectedCount = 0
lastAwareCount = 0

# Init Data Logging
if not os.path.exists("Generated towns/" + townName + "/simData/" + iterationName):
    os.makedirs("Generated towns/" + townName + "/simData/" + iterationName)
statsDict = {}
statsDict["townName"] = townName
statsDict["simLength"] = dayCount
statsDict["dataVersion"] = dataVersion
statsDict["iterationName"] = iterationName

for i in range(dayCount):
    statsDict["day" + str(i + 1)] = {"stats": {
        "totalActiveInfections": None,
        "totalDeaths": None,
        "dailyCases": None,
        "dailyDeaths": None,
        "dailyAware": None,
        "dailyHotSpots": None
    },
        "infectedPeopleID": [],
        "infectedPlacesID": [],
        "InfectedPeopleStates": []
    }

# Calculate days off
daysOff = []
for i in range(constants["time"]["daysOffPerWeek"]):
    daysOff.append(7 - i)
daysOff.sort()

workingTimesCount = 0

weekCount = 0
for day in range(dayCount):
    day += 1
    isWeekend = False
    if day % 7 == 0 or day % 7 in daysOff:
        isWeekend = True

    for personIndex, person in enumerate(peopleList):
        personStatus = person.newDay(day)
    if not isWeekend:  # If its a weekday
        weekDayIndex = day % 7
        if weekDayIndex == 1:  # If its the first day of the week
            for person in peopleList:
                if person.workPlace != "None":
                    person.generateWorkPlan(
                        7 - constants["time"]["daysOffPerWeek"])

        for person in peopleList:
            worked = False
            if person.workPlace != "None":
                # If someone has to work that day
                if person.workPlan[weekDayIndex - 1]:
                    # Generate their working times
                    hoursToWork = round(generateFromCurve(
                        int(person.workPlace.daysCount) + 3, (int(person.workPlace.daysCount) + 3) / 4))
                    workingTimes = generateTimePeriod(int(constants["time"]["dayStart"]), int(
                        constants["time"]["dayEnd"]), int(hoursToWork))
                    person.workPlace.haveVisitor(entities.visit(
                        person.workPlace, person, workingTimes["start"], workingTimes["end"], day))
                    workingTimesCount += 1
                    worked = True
            if person.age > constants['age']['youngEnd']:
                if not worked:  # If the person is old enough to do the shopping AND NOT at work
                    shopProb = 0
                    # If the shopping hasn't already been done that day by another family member
                    if day - person.adress.lastShoppingDay != 0:
                        shopProb = (day - person.adress.lastShoppingDay) / \
                            shopData["avgDaysBetweenShops"]
                    probList = [[True, shopProb * 100],
                                [False, 100 - shopProb * 100]]
                    # If the person decides to go shopping
                    if generateFromList(probList):
                        timeTaken = round(generateFromCurve(
                            shopData["avgTimeForShop"], shopData["timeVar"]))
                        shopTimes = generateTimePeriod(int(constants["time"]["dayStart"]), int(
                            constants["time"]["dayEnd"]), int(timeTaken))

                        shopChosen = shopList[random.randint(
                            0, len(shopList) - 1)]

                        shopChosen.haveVisitor(entities.visit(
                            shopChosen, person, shopTimes["start"], shopTimes["end"], day))
            # Calculate if person can do exercise
            if person.age > globals()[person.gender + "ExerciseData"]["minAge"]:
                exerciseData = globals()[person.gender + "ExerciseData"]
                eProb = 0
                if day - person.dayOfLastExercise != 0:  # If they haven't already exercised that day
                    eProb = (day - person.dayOfLastExercise) / (exerciseData["avgDaysBetweenExercise"] + (
                        exerciseData["betweenExerciseVar"] * exerciseData["betweenVarMultiplier"]))
                eList = [[True, eProb * 100], [False, 100 - eProb * 100]]
                if generateFromList(eList):  # If person decides to do exercise
                    busyTime = person.findFreePeriods(day)
                    # If the person has time in their day to exercise
                    if busyTime["end"] - busyTime["start"] <= exerciseData["latestTime"] - exerciseData["earliestTime"]:
                        # If they have more time in the morning
                        if busyTime["start"] - busyTime["start"] >= exerciseData["latestTime"] - busyTime["end"]:
                            foundVal = False
                            while not foundVal:
                                exerciseDuration = round(generateFromCurve(
                                    exerciseData["avgExerciseTime"], exerciseData["timeVar"]))
                                if exerciseDuration < busyTime["start"] - exerciseData["earliestTime"]:
                                    foundVal = True
                            exerciseTimes = generateTimePeriod(
                                exerciseData["earliestTime"], busyTime["start"], exerciseDuration)
                        else:  # If they are more free in the afternoon
                            foundVal = False
                            while not foundVal:
                                exerciseDuration = round(generateFromCurve(
                                    exerciseData["avgExerciseTime"], exerciseData["timeVar"]))
                                if exerciseDuration < exerciseData["latestTime"] - busyTime["end"]:
                                    foundVal = True
                            exerciseTimes = generateTimePeriod(
                                busyTime["end"], exerciseData["latestTime"], exerciseDuration)
                        person.updateExercise(day)
                        person.goPlace(entities.visit(exerciseList[random.randint(0, len(
                            exerciseList) - 1)], person, exerciseTimes["start"], exerciseTimes["end"], day))
                        chosenLocation = exerciseList[random.randint(
                            0, len(exerciseList) - 1)]
                        chosenLocation.haveVisitor(entities.visit(
                            chosenLocation, person, exerciseTimes["start"], exerciseTimes["end"], day))

    if isWeekend:
        for person in peopleList:
            if person.age > globals()[person.gender + "ExerciseData"]["minAge"]:
                exerciseData = globals()[person.gender + "ExerciseData"]
                eProb = 0
                if day - person.dayOfLastExercise != 0:  # If they haven't already exercised that day
                    eProb = (day - person.dayOfLastExercise) / (exerciseData["avgDaysBetweenExercise"] + (
                        exerciseData["betweenExerciseVar"] * exerciseData["betweenVarMultiplier"]))
                eProb *= exerciseData["weekendmultiplier"]
                eList = [[True, eProb * 100], [False, 100 - eProb * 100]]
                if generateFromList(eList):
                    person.updateExercise(day)
                    exerciseDuration = round(generateFromCurve(
                        exerciseData["avgExerciseTime"], exerciseData["timeVar"]))
                    exerciseTimes = generateTimePeriod(
                        exerciseData["earliestTime"], exerciseData["latestTime"], exerciseDuration)
                    chosenLocation.haveVisitor(entities.visit(
                        chosenLocation, person, exerciseTimes["start"], exerciseTimes["end"], day))

    # Assume that person is home all times when they are not out
    for person in peopleList:
        for spareTime in [[0, person.findFreePeriods(day)["start"]], [person.findFreePeriods(day)["end"], constants["time"]["periodsPerDay"]]]:
            thisVisit = entities.visit(
                person.adress, person, spareTime[0], spareTime[1], day)
            person.goPlace(thisVisit)
            person.adress.haveVisitor(thisVisit)

    hotSpotLocations = []
    for location in allLocations:
        visitLog = location.visitLog
        try:
            for log in visitLog[day]:
                if log.person.covidStatus:
                    hotSpotLocations.append(location.id)
                    posLog = log
                    possiblePeriods = []
                    for i in range(log.endPeriod - log.startPeriod + 1):
                        possiblePeriods.append(i + log.startPeriod)
                    for searchLog in visitLog[day]:
                        if not searchLog.person.covidStatus:
                            searchPeriods = []
                            for k in range(searchLog.endPeriod - searchLog.startPeriod + 1):
                                searchPeriods.append(k + searchLog.startPeriod)
                            overLapScore = len(
                                list(set(possiblePeriods).intersection(searchPeriods)))
                            covidChance = calculateExposureChance(
                                searchLog.person, covidConstants, overLapScore)
                            covidChance = normalizeVal(
                                covidChance, 0, maxPossibleCovidScore)
                            if generateFromList([[True, covidChance * 100], [False, 100 - (covidChance * 100)]]):
                                searchLog.person.getCovid(day, overLapScore)
                    break
        except KeyError:
            pass

    # Log day-by-day data
    deathCount = 0
    infectedCount = 0
    infectedTodayCount = 0
    awareOfInfectionCount = -lastAwareCount
    infectedTodayList = []
    peopleStates = []
    for person in peopleList:
        if person.covidStatus:
            infectedCount += 1
            if person.infectionDay == day:
                infectedTodayCount += 1
                infectedTodayList.append(person.id)
            peopleStates.append({ 
                "covidStatus":person.covidStatus,
                "awareOfInfection":person.awareOfInfection,
                "healthScore":person.healthScore,
                "isAlive":person.isAlive
                })
        if person.awareOfInfection:
            awareOfInfectionCount += 1
        if person.isAlive == False:
            deathCount += 1

    statsDict["day" + str(day)]["stats"]["totalActiveInfections"] = infectedCount
    statsDict["day" + str(day)]["stats"]["totalDeaths"] = deathCount
    statsDict["day" + str(day)]["stats"]["dailyCases"] = infectedTodayCount
    statsDict["day" + str(day)]["stats"]["dailyDeaths"] = deathCount - lastDeathCount
    statsDict["day" + str(day)]["stats"]["dailyAware"] = awareOfInfectionCount
    statsDict["day" + str(day)]["stats"]["dailyHotSpots"] = len(hotSpotLocations)
    statsDict["day" + str(day)]["infectedPeopleID"] = infectedTodayList
    statsDict["day" + str(day)]["infectedPlacesID"] = hotSpotLocations
    statsDict["day" + str(day)]["infectedPlacesID"] = hotSpotLocations
    statsDict["day" + str(day)]["peopleStates"] = peopleStates

    lastDeathCount = deathCount
    lastInfectedCount = infectedCount
    lastAwareCount = awareOfInfectionCount

    if writeFileDaily:
        with open("Generated Towns/" + townName + "/simData/" + iterationName + "/data.json", "w") as dictFile:
            json.dump(statsDict, dictFile, indent=4)

    if day == 1:
        print("LOADING " + str(round(day / dayCount * 100)) +
              "%", end="", flush=True)
    else:
        print("\b" * len(str(round((day - 1) / dayCount * 100)) + "%") +
              str(round(day / dayCount * 100)) + "%", end="", flush=True)


if not writeFileDaily:
    with open("Generated Towns/" + townName + "/simData/" + iterationName + "/data.json", "w") as dictFile:
        json.dump(statsDict, dictFile, indent=4)


print("\n")

for stat in thingsToPlot:
    plotList = []
    for day in range(dayCount):
        plotList.append(statsDict["day" + str(day + 1)]["stats"][stat])
    plt.plot(plotList, label=stat)

plt.title("Covid cases over time")
plt.legend()

plt.show()
