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
    for task in tasks:
        previousTasksIds = toInt(task["previous"])
        minStart = 0
        times = task["times"]

        if len(previousTasksIds) == 1:
            minStart = tasks[previousTasksIds[0]]["times"]["minEnd"]

        if len(previousTasksIds) >= 2:
            prevTasksMinEnds = [tasks[id]['times']['minEnd']
                                for id in previousTasksIds]
            # Getting latest min end time when there are more than one "prevs"
            minStart = max(prevTasksMinEnds)

        times["minStart"] = minStart
        times['minEnd'] = minStart + times['tm']


def toInt(arr):
    return list(map(lambda char: ord(char.lower())-97, arr))


def getOrphanedTasks(tasks):
    tasksWithParentsIds = []
    for task in tasks:
        for taskId in toInt(task["previous"]):
            if taskId not in tasksWithParentsIds:
                tasksWithParentsIds.append(taskId)

    return [tasks[id] for id in [item for item in range(len(tasks)) if item not in tasksWithParentsIds]]


def processBackward(tasks):
    def traverse(task):
        nonlocal tasks
        prevs = [tasks[id] for id in toInt(task["previous"])]

        for prev in prevs:
            # print(task['taskID'], ' -> ', prev['taskID'])
            nextMaxStart = task['times']['maxStart']

            if 'maxEnd' in prev['times']:
                # Getting latest start time when there are more than one "nexts"
                if prev['times']['maxEnd'] > nextMaxStart:
                    prev['times']['maxEnd'] = nextMaxStart
            else:
                prev['times']['maxEnd'] = nextMaxStart

            prev['times']['maxStart'] = prev['times']['maxEnd'] - \
                prev['times']['tm']

            # prev will be next for its prevs 🧠
            traverse(prev)

    for task in getOrphanedTasks(tasks):
        # Orphaned tasks have equal max and min end time
        task['times']['maxEnd'] = task['times']['minEnd']
        task['times']['maxStart'] = task['times']['maxEnd'] - \
            task['times']['tm']
        # Traversing through the graph from every orhpaned tasks
        traverse(task)

    # First task also has equal max and min end time
    tasks[0]['times']['maxEnd'] = tasks[0]['times']['minEnd']
    tasks[0]['times']['maxStart'] = tasks[0]['times']['maxEnd'] - \
        tasks[0]['times']['tm']

    # Calculating slack time
    for task in tasks:
        endSlack = task['times']['maxEnd'] - task['times']['minEnd']
        startSlack = task['times']['maxStart'] - task['times']['minStart']
        task['times']['slack'] = min([endSlack, startSlack])


def findCriticalPaths(tasks):
    visited = {}
    # Mark all the tasks as not visited
    for task in tasks:
        visited[task['taskID']] = False

    # Create an array to store different paths
    paths = []
    tempPath = []

    def traverse(task):
        nonlocal visited
        nonlocal tasks
        nonlocal paths
        nonlocal tempPath
        # Mark the current node as visited and store in tempPath[]
        visited[task['taskID']] = True
        tempPath.append(task)

        # If current task is "start" task, temp path is
        # finished, then check if it is critical
        if len(task['previous']) == 0 and all(task['times']['slack'] == 0 for task in tempPath):
            paths.append(tempPath[:])
        else:
            # If current task is not "start" task,
            # continue traversing
            for child in [tasks[id] for id in toInt(task['previous'])]:
                if visited[child['taskID']] == False:
                    traverse(child)

        # Remove current task from tempPath[] and mark it as unvisited
        tempPath.pop()
        visited[task['taskID']] = False

    # Traversing through the graph from every orhpaned tasks
    for task in getOrphanedTasks(tasks):
        traverse(task)

    return paths


def printCriticalPaths(paths):
    print('\n\nCritical paths:\n')
    for path in paths:
        print('START', end=' -> ')
        for task in reversed(path):
            print(task['taskID'], end=' -> ')
        print('END')


if __name__ == '__main__':

    taskData = readData("tasks.json")
    processForward(taskData)
    processBackward(taskData)

    for id, task in enumerate(taskData):
        print('{}.  minS: {:.2f} maxS: {:.2f} minE: {:.2f} maxE: {:.2f} slack: {:.2f}'.format(
            task['taskID'],
            task['times']['minStart'],
            task['times']['maxStart'],
            task['times']['minEnd'],
            task['times']['maxEnd'],
            task['times']['slack']
        ))

    criticalPaths = findCriticalPaths(taskData)
    printCriticalPaths(criticalPaths)

    # docs
    # https://mfiles.pl/pl/index.php/PERT
    # https://4business4you.com/biznes/zarzadzanie-projektami/metoda-pert-w-praktyce/
