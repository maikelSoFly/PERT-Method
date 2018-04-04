import json
import os


def readData(dataName):
    dataPath = os.path.join("../data", dataName)
    list = []
    with open(dataPath, 'r') as f:
        list.extend(json.loads(f.read()).values())
        return list


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
    for taskId, task in enumerate(tasks):
        previousTasksIds = task["previous"]
        minStart = 0
        times = task["times"]

        if len(previousTasksIds) == 1:
            minStart = tasks[previousTasksIds[0]]["times"]["minEnd"]

        if len(previousTasksIds) >= 2:
            prevTasksTms = [tasks[id]['times']['minEnd']
                            for id in previousTasksIds]
            minStart = max(prevTasksTms)

        times["minStart"] = minStart
        times['minEnd'] = minStart + times['tm']


# Rekurencją zrobione będzie
def processBackward(all_tasks, task):
    children = [all_tasks[id] for id in task['previous']]
    for child in children:
        print(child['taskID'])
        processBackward(all_tasks, child)


# def postProcess(tasks):


if __name__ == '__main__':

    taskData = readData("tasks.json")
    processForward(taskData)
    processBackward(taskData, taskData[-1])
    # processBackward(taskData)
    # for id, value in enumerate(taskData):
    #     print(id, value['times']['minStart'], value['times']['minEnd'])

    # print(calculateExpected(value["times"]))
    # value["timeStart"] = 6.
    # calculateVariation(taskData)
    # print(taskData)

    # docs
    # https://mfiles.pl/pl/index.php/PERT
    # https://4business4you.com/biznes/zarzadzanie-projektami/metoda-pert-w-praktyce/
