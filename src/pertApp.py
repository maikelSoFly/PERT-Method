import json
import os

def readData(dataName):
    dataPath = os.path.join("../data", dataName)
    with open(dataPath, 'r') as f:
            return json.loads(f.read())

def calculateExpected(times):
    numerator = times["tc"] + 4 * times["tm"] + times["tp"]
    return numerator/6

def calculateVariation(times):
    numerator = times["tp"] - times["tc"]
    return (numerator/6)**2

def standardDeviation(times):
    numerator = times["tp"] + times["tc"]
    return numerator/6

if __name__ == '__main__':
    taskData = readData("tasks.json")
    for key, value in taskData.items():
        print(calculateExpected(value["times"]))
        value["timeStart"] = 6.
