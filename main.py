import lib.entities as entities
from lib.readCsv import getData
from lib.generateRandom import generateFromList
from lib.generateRandom import generateKidsCount
import matplotlib.pyplot as plt
from collections import Counter
import random

constants = {}

#Get Diversity data about population

divFile = open("data/diversityData.txt", "r", encoding='utf-8')
divData = divFile.readlines()
for line in divData:
    constants[line[1:line.find(">")]] = int(line[line.find(">") + 1:-1])
divFile.close()

genderFreq = [["male", float(constants["male"])], ["female", float(constants["female"])]]

maleAgeFreq = getData("data/Male/ageDistro.csv", True)
femaleAgeFreq = getData("data/Female/ageDistro.csv", True)
houseDensityFreq = getData("data/House/densityDistro.csv", True)

peopleList = []
# Generate population
for i in range(constants["population"]):
    gender = generateFromList(genderFreq)
    ageRange = generateFromList(globals()[gender + "AgeFreq"]) # Generate a random age range based off of data, (e.g 0-5)
    minAge = int(ageRange[:ageRange.find("-")]) #
    maxAge = int(ageRange[ageRange.find("-")+1:])
    age = random.randint(minAge, maxAge) # Generate a random age in the specified age range
    peopleList.append(entities.person(age, gender))

# Generate Houses
houseList = []
totalHouseCount = 0
while True:
    if totalHouseCount + 6 < constants["population"]:
        houseDensity = int(generateFromList(houseDensityFreq))
    else:
        houseDensity =  constants["population"] - totalHouseCount
        totalHouseCount += houseDensity
        break
    houseList.append(entities.house(houseDensity))
    totalHouseCount += houseDensity


# Populate houses based off houseType and fullness data
for house in houseList:
    if house.residentCount == 1:
        house.setHouseType("single")
        for personIndex, person, in enumerate(peopleList):
            if person.age > constants["midStart"]:
                peopleList.pop(personIndex)
                house.addResident(person) # If the person is old enough to live by themselves, put them in a single house
                break
    
    else: # If the house contains more then one person
        isKids = False # Find if there are any more kids in the population
        for sampleIndex, samplePerson in enumerate(peopleList):
            if samplePerson.age < constants["youngEnd"]:
                isKids = True
                break
        
        if isKids:
            house.setHouseType("family") # If there are kids remaining, the house will become a family type house
            kidList = []
            adultList = []
            for i in range(generateKidsCount(house.residentCount)): # Find a certain amount of kids for the house
                for kidIndex, kid in enumerate(peopleList):
                    if kid.age < constants["youngEnd"]:
                        kidList.append(kid)
                        peopleList.pop(kidIndex)
                        break
            for i in range(house.residentCount - len(kidList)): # Fill the remaining vacancies with adults
                for peopleIndex, people in enumerate(peopleList):
                    if people.age > constants["youngEnd"]:
                        adultList.append(people)
                        peopleList.pop(peopleIndex)
                        break
            
            for kid in kidList:
                house.addResident(kid)
            for adult in adultList:
                house.addResident(adult)
        
        else:
            house.setHouseType("group")
            for i in range(house.residentCount):
                for personIndex, person in enumerate(peopleList):
                    if person.age > constants["youngEnd"]:
                        house.addResident(person)
                        peopleList.pop(personIndex)
                        break

# for house in houseList:
#     if house.residentCount != len(house.residentList):
#         print(house.type)
#         print(house.residentCount)
#         print(len(house.residentList))
#         print(house.residentList)
#         print("==")

# print(len(peopleList))

x = constants["population"]
for h in houseList:
    x = x - int(h.residentCount)

print(x)


