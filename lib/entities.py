import random
from lib.generateRandom import generateFromCurve, generateFromList, normalizeVal
from perlin_noise import PerlinNoise

class person:
    def __init__(self, age, gender, id, fluctuationScore):
        super().__init__()
        self.age = age
        self.gender = gender
        self.id = id
        self.fluctuationScore = fluctuationScore

        self.workPlace = "None"
        self.adress = "None"
        self.visitLog = {}
        self.dayOfLastExercise = 0

        self.covidStatus = False
        self.awareOfInfection = False
        self.infectionDay = 0
        self.hadCovid = False

        self.healthScore = 0
        self.isAlive = True

    def newDay(self, dayNum):
        if not self.covidStatus: # Covid stops person from defaulting to healthy (healthscore = 0) each day
            self.healthScore = 0

        if self.covidStatus:
            if self.hasSymptoms:
                try:
                    symptomChance = self.symptomStrengths[dayNum]
                except KeyError:
                    print("AAA")
                    print("\n")
                    print(self.covidStatus)
                    print(self.infectionEndDay)
                    print(self.awareOfInfection)
                    print(dayNum)
                    print(self.symptomStrengths)
                if generateFromList([[True, symptomChance * 100], [False, 100 - (symptomChance * 100)]]):
                    self.awareOfInfection = True

            if dayNum >= self.infectionEndDay: # After infection has passed reset health score
                self.covidStatus = False
                self.healthScore = 0
                self.awareOfInfection = False
                self.hadCovid = True


        if generateFromList([[True, (100 * self.fluctuationScore)], [False, (100 - 100 * self.fluctuationScore)]]): # Check if person is gonna have health dip
            self.healthScore += round(generateFromCurve(self.fluctuationScore, self.fluctuationScore), 2)



        if self.healthScore > 0.9: # If person is close to death
            if generateFromList([[True, (self.healthScore / 2) * 100], [False, 100 - (self.healthScore / 2) * 100]]): # Find if person should die
                self.isAlive = False



    def addAdress(self, adress):
        self.adress = adress

    def setWorkplace(self, workPlace):
        self.workPlace = workPlace

    def generateWorkPlan(self, workingDays):
        # Generates a list which dictates when the person goes to work
        self.workPlan = []
        for _ in range(workingDays):
            self.workPlan.append(False)

        for _ in range(int(self.workPlace.daysCount)):
            foundVal = False
            while not foundVal:
                pos = random.randint(0, len(self.workPlan) - 1)
                if self.workPlan[pos] == False:
                    self.workPlan[pos] = True
                    foundVal = True

    def findFreePeriods(self, day):
        earliestStart = 24
        latestEnd = 0
        try:
            for item in self.visitLog[day]:
                if item.startPeriod < earliestStart:
                    earliestStart = item.startPeriod
                if item.endPeriod > latestEnd:
                    latestEnd = item.endPeriod
        except KeyError:
            earliestStart = 0
            latestEnd = 24
        return {"start": earliestStart, "end": latestEnd}

    def goPlace(self, place):
        try:
            self.visitLog[place.day].append(place)
        except KeyError:
            self.visitLog[place.day] = [place]

    def updateExercise(self, day):
        self.dayOfLastExercise = day

    def setCovidConstants(self, constants):
        self.covidConstants = constants

    def getCovid(self, dayNumber, exposureTime):
        noise = PerlinNoise(octaves= 5)
        self.infectionDay = dayNumber
        self.covidStatus = True
        infectionDuration = int(generateFromCurve(self.covidConstants["avgInfectionDuration"], self.covidConstants["infectionVariability"]))
        self.exposureTime = exposureTime
        self.infectionEndDay = dayNumber + infectionDuration

        # Calculate if person is asymptomatic
        if generateFromList([[True, (100 * self.covidConstants["asymptomaticChance"])], [False, 100 -(100 * self.covidConstants["asymptomaticChance"])]]):
            self.hasSymptoms = False
        else:
            self.hasSymptoms = True
        self.symptomStrengths = {}
        for day in range(infectionDuration + 1):
            noiseVal = abs(noise(day / infectionDuration) * 3)
            self.symptomStrengths[dayNumber + day + 1] = noiseVal





class location:
    def __init__(self):
        self.visitLog = {}

    def haveVisitor(self, visit):
        try:
            self.visitLog[visit.day].append(visit)
        except KeyError:
            self.visitLog[visit.day] = [visit]

        visit.person.goPlace(visit)


class house(location):
    def __init__(self, residentCount, id):
        super().__init__()
        self.residentCount = residentCount
        self.id = id
        self.residentList = []
        self.lastShoppingDay = 0

    def addResident(self, person):
        self.residentList.append(person)

    def setHouseType(self, houseType):
        self.type = houseType

    def doShopping(self, day):
        self.lastShoppingDay = day

class workPlace(location):
    def __init__(self, essentialStatus, genderRatio, ageDistro, workerCount, daysCount, id):
        super().__init__()
        self.essentialStatus = essentialStatus
        self.genderRatio = genderRatio
        self.ageDistro = ageDistro
        self.workerList = []
        self.workerCount = workerCount
        self.daysCount = daysCount
        self.id = id

    def addWorker(self, worker):
        self.workerList.append(worker)

class otherLocation(location):
    def __init__(self, locType, id):
        super().__init__()
        self.locType = locType
        self.id = id
        self.visitLog = {}

class visit:
    def __init__(self, location, person, startPeriod, endPeriod, day):
        super().__init__()
        self.location = location
        self.person = person
        self.startPeriod = startPeriod
        self.endPeriod = endPeriod
        self.day = day

    def toDict(self):
        return{
            "location": self.location.id,
            "person": self.person.id,
            "startPeriod": self.startPeriod,
            "endPeriod": self.endPeriod,
            "day": self.day
        }


