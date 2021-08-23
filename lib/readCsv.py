import csv


def getData(filepath, valIsFloat):  # Function that reads data from a csv and returns as a list of  lists (columns and rows)
    csvFile = open(filepath, "r", encoding="utf-8")
    csvReader = csv.reader(csvFile, delimiter=",")
    data = []
    for row in csvReader:
        if valIsFloat:
            data.append([row[0], float(row[1])])
        else:
            data.append(row)
    return data

if __name__ == "__main__":
    print(getData("data/Female/ageDistro.csv", True))