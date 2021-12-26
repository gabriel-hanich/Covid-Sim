import random
from lib.generateRandom import generateFromCurve, generateFromList, calculateSymptomStrength, normalizeVal

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
        self.awareOfCovidState = False
        self.infectionDay = 0

        self.healthScore = 0

    def newDay(self, dayNum):
        if not self.covidStatus: # Covid stops person from defaulting to healthy (healthscore = 0) each day
            self.healthScore = 0 
        if generateFromList([[True, (100 * self.fluctuationScore)], [False, (100 - 100 * self.fluctuationScore)]]): # Check if person is gonna have health dip
            self.healthScore += round(generateFromCurve(self.fluctuationScore, self.fluctuationScore), 2)
        
        if self.healthScore > 0.9: # If person is close to death
            if generateFromList([[True, (self.healthScore / 2) * 100], [False, 100 - (self.healthScore / 2) * 100]]): # Find if person should die
                return "DEAD"
        
        if self.covidStatus:
            symptomChance = calculateSymptomStrength(self.age, abs(dayNum - self.infectionDay), self.exposureTime)
            symptomChance = normalizeVal(symptomChance, 0, self.covidConstants["maxPossibleCovidSymptomScore"])


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
        self.infectionDay = dayNumber
        self.covidStatus = True
        self.exposureTime = exposureTime
        



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


        