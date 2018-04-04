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


def getTasksIdsWithParents(tasks):
    tasksWithParents = []
    for task in tasks:
        for taskId in task['previous']:
            if taskId not in tasksWithParents:
                tasksWithParents.append(taskId)
    return tasksWithParents


def handleProcessBackward(tasks):
    tasksWithParents = getTasksIdsWithParents(tasks)
    for id, task in enumerate(tasks):
        if id not in tasksWithParents:
            task['times']['maxEnd'] = task['times']['minEnd']
            task['times']['maxStart'] = task['times']['maxEnd'] - \
                task['times']['tm']
            processBackward(tasks, task, task)


def processBackward(all_tasks, task, next):
    children = [all_tasks[id] for id in task['previous']]
    for child in children:
        print(next['taskID'], ' -> ', child['taskID'])

        if 'maxEnd' in child['times']:
            if child['times']['maxEnd'] > next['times']['maxStart']:
                child['times']['maxEnd'] = next['times']['maxStart']
        else:
            child['times']['maxEnd'] = next['times']['maxStart']

        child['times']['maxStart'] = child['times']['maxEnd'] - \
            child['times']['tm']
        processBackward(all_tasks, child, child)


# def postProcess(tasks):


if __name__ == '__main__':

    taskData = readData("tasks.json")
    processForward(taskData)
    handleProcessBackward(taskData)

    for id, t in enumerate(taskData):
        print('{}.  minS: {:.2f} maxS: {:.2f} minE: {:.2f} maxE: {:.2f}'.format(
            t['taskID'],
            t['times']['minStart'],
            t['times']['maxStart'],
            t['times']['minEnd'],
            t['times']['maxEnd']
        ))

    # print(calculateExpected(value["times"]))
    # value["timeStart"] = 6.
    # calculateVariation(taskData)
    # print(taskData)

    # docs
    # https://mfiles.pl/pl/index.php/PERT
    # https://4business4you.com/biznes/zarzadzanie-projektami/metoda-pert-w-praktyce/
