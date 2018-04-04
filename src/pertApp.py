import json
import os


def readData(dataName):
    dataPath = os.path.join("../data", dataName)
    with open(dataPath, 'r') as f:
        return json.loads(f.read())


def calculateExpected(times):
    numerator = times["tc"] + 4 * times["tm"] + times["tp"]
    times["expected"] = numerator/6
    return times["expected"]


def calculateVariation(tasks):
    for key, task in tasks.items():
        times = task["times"]
        numerator = times["tp"] - times["tc"]
        task["variation"] = (numerator/6)**2


def standardDeviation(times):
    numerator = times["tp"] + times["tc"]
    return numerator/6


def processForward(tasks):
    for taskId, task in tasks.items():
        previousTasksIds = task["previous"]
        minStart = 0
        times = task["times"]

        if len(previousTasksIds) == 1:
            minStart = tasks[previousTasksIds[0]]["times"]["tm"]
        if len(previousTasksIds) >= 2:
            prevTasksTms = [tasks[id]['times']['tm']
                            for id in previousTasksIds]
            minStart = max(prevTasksTms)

        times["minStart"] = minStart

# def processBackward(tasks):

# def postProcess(tasks):


if __name__ == '__main__':

    taskData = readData("tasks.json")
    processForward(taskData)
    for key, value in taskData.items():
        print(key, value['times']['minStart'])

        # print(calculateExpected(value["times"]))
        # value["timeStart"] = 6.
        # calculateVariation(taskData)
        # print(taskData)


# docs
# https://mfiles.pl/pl/index.php/PERT
# https://4business4you.com/biznes/zarzadzanie-projektami/metoda-pert-w-praktyce/
