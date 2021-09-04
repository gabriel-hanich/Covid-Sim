import random

class person:
    def __init__(self, age, gender, id):
        super().__init__()
        self.age = age
        self.gender = gender
        self.id = id
        self.workPlace = "None"
        self.adress = "None"
        self.workCount = 0
        
    def addAdress(self, adress):
        self.adress = adress
    
    def setWorkplace(self, workPlace):
        self.workPlace = workPlace
    
    def generateWorkPlan(self, workingDays):
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

class house:
    def __init__(self, residentCount, id):
        super().__init__()
        self.residentCount = residentCount
        self.id = id
        self.residentList = []
    
    def addResident(self, person):
        self.residentList.append(person)
    
    def setHouseType(self, houseType):
        self.type = houseType

class workPlace:
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
    
class otherLocation:
    def __init__(self, locType, id):
        super().__init__()
        self.locType = locType
        self.visitLog = {}
        self.id = id

    def visit(self, person, time):
        if time not in visitLog:
            self.visitLog[time] = [person]
        else:
            self.visitLog[time].append(person)

    