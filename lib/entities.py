class person:
    def __init__(self, age, gender):
        super().__init__()
        self.age = age
        self.gender = gender
        
    def addAdress(self, adress):
        self.adress = adress

class house:
    def __init__(self, residentCount):
        super().__init__()
        self.residentCount = residentCount
        self.residentList = []
    
    def addResident(self, person):
        self.residentList.append(person)
    
    def setHouseType(self, houseType):
        self.type = houseType

class workPlace:
    def __init__(self, essentialStatus, genderRatio, ageDistro, workerCount):
        super().__init__()
        self.essentialStatus = essentialStatus
        self.genderRatio = genderRatio
        self.ageDisto = ageDistro
        self.workerList = []
        self.workerCount = workerCount

    def addWorker(self, worker):
        self.workerList.append(worker)
    
