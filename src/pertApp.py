import json
import csv
import os
from prettytable import PrettyTable


def readData(fileName, dataName='task'):
    dataPath = os.path.join("../data", fileName)
    print('Reading from: ', dataPath)
    list = []
    dict = {}
    with open(dataPath, 'r') as f:
        if dataName == 'task':
            list.extend(json.loads(f.read()).values())
            return list
        elif dataName == 'distribution':
            spamreader = csv.reader(f, delimiter=';')
            for row in spamreader:
                dict[row[0]] = row[1]
            return dict


def calculateExpected(tasks):
    for task in tasks:
        times = task['times']
        if 'expected' in times:
            continue
        numerator = times["tc"] + 4 * times["tm"] + times["tp"]
        times["expected"] = numerator/6


def calculateVariation(tasks):
    for task in tasks:
        times = task["times"]
        if 'expected' in times:
            continue
        numerator = times["tp"] - times["tc"]
        times["variation"] = (numerator/6)**2


def calculateStandardDeviation(tasks):
    for task in tasks:
        times = task['times']
        if 'expected' in times:
            continue
        numerator = times["tp"] + times["tc"]
        times['deviation'] = numerator/6


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
        times['minEnd'] = minStart + times['expected']


def toInt(arr):
    return list(map(lambda char: ord(char.lower())-97, arr))


def getOrphaned(tasks):
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
            nextMaxStart = task['times']['maxStart']
            times = prev['times']

            if 'maxEnd' in prev['times']:

                # Getting latest start time when there are more than one "nexts"
                if times['maxEnd'] > nextMaxStart:
                    times['maxEnd'] = nextMaxStart
            else:
                times['maxEnd'] = nextMaxStart

            times['maxStart'] = times['maxEnd'] - \
                times['expected']

            # prev will be next for its prevs 🧠
            traverse(prev)

    for task in getOrphaned(tasks):
        # Orphaned tasks have equal max and min end time
        times = task['times']
        times['maxEnd'] = times['minEnd']
        times['maxStart'] = times['maxEnd'] - \
            times['expected']
        # Traversing through the graph from every orhpaned tasks
        traverse(task)

    # First task also has equal max and min end time
    times = tasks[0]['times']
    times['maxEnd'] = times['minEnd']
    times['maxStart'] = times['maxEnd'] - \
        times['expected']

    # Calculating slack time
    for task in tasks:
        times = task['times']
        endSlack = times['maxEnd'] - times['minEnd']
        startSlack = times['maxStart'] - times['minStart']
        times['slack'] = min([endSlack, startSlack])


def PERT(tasks):
    processForward(tasks)
    processBackward(tasks)


def findCriticalPaths(tasks, printTree=True):
    visited = {}
    # Mark all the tasks as not visited
    for task in tasks:
        visited[task['taskID']] = False

    # Create an array to store different paths
    paths = []
    tempPath = []
    levels = [] # for printing tree
    treeStr = '\nEND'

    def appendTreePrint(level, task):
        nonlocal levels
        nonlocal treeStr 
        nonlocal tempPath
        left = '\n'
        for l in range(level):
            if l in levels:
                left += '│'
            else:
                left += ' '
        forkChar = '├' if level in levels else '└'
        treeStr += left+forkChar+task['taskID']

        if len(task['previous']) == 0:
            treeStr += '⏤ START'
            duration = 0
            for task in tempPath:
                duration += task['times']['expected']
            treeStr += '  \t{:.1f}{}'.format(duration, task['times']['timeType'])
        
        if len(task['previous']) > 1:
            levels.append(level+1)


    def traverse(task, level=0):
        nonlocal visited
        nonlocal tasks
        nonlocal paths
        nonlocal tempPath
        nonlocal treeStr
        nonlocal printTree
        # Mark the current node as visited and store in tempPath[]
        visited[task['taskID']] = True
        tempPath.append(task)

        if printTree:
            appendTreePrint(level, task)
            
        
        # If current task is "start" task, temp path is
        # finished, then check if it is critical
        if len(task['previous']) == 0 and all(task['times']['slack'] == 0 for task in tempPath):
            treeStr += ' 🔴'
            
            paths.append(tempPath[:])
        else:
            
            # If current task is not "start" task,
            # continue traversing
            for child in [tasks[id] for id in toInt(task['previous'])]:
                if not visited[child['taskID']]:
                    traverse(child, level+1)

        # Remove current task from tempPath[] and mark it as unvisited
        tempPath.pop()
        visited[task['taskID']] = False
       #
        if printTree and level in levels:
            levels.remove(level)

    # Traversing through the graph from every orhpaned tasks
    orphaned = getOrphaned(tasks) 

    if printTree and len(orphaned) > 1:
        levels.append(0)

    for task in orphaned:
        treeStr += '\n│\n│'
        traverse(task)
    
    if printTree:
        print(treeStr)
    return paths


def printTimes(tasks):
    x = PrettyTable()

    x.field_names = ['ID', "Optimistic", "Pessimistic",
                     "Most-likely", "Expected", 'Deviation', 'Variation']

    for task in tasks:
        times = task['times']

        x.add_row([task['taskID'],
                   '{:.1f}'.format(times['tc'] if 'tc' in times else 0),
                   '{:.1f}'.format(times['tp'] if 'tp' in times else 0),
                   '{:.1f}'.format(times['tm'] if 'tm' in times else 0),
                   '{:.1f}'.format(times['expected'] if 'expected' in times else 0),
                   '{:.1f}'.format(times['deviation'] if 'deviation' in times else 0),
                   '{:.1f}'.format(times['variation'] if 'variation' in times else 0)])
    
    print('\n')
    print(x, '\n')


def printTasks(tasks):
    x = PrettyTable()

    x.field_names = ['ID', "min. Start", "max. Start",
                     "min. End", "max. End", 'Slack']

    for task in tasks:
        times = task['times']

        x.add_row([task['taskID'],
                   '{:.1f}'.format(times['minStart'] if 'minStart' in times else 0),
                   '{:.1f}'.format(times['maxStart'] if 'maxStart' in times else 0),
                   '{:.1f}'.format(times['minEnd'] if 'minEnd' in times else 0),
                   '{:.1f}'.format(times['maxEnd'] if 'maxEnd' in times else 0),
                   '{:.1f}'.format(times['slack'] if 'slack' in times else 0)])

    print('\n')
    print(x, '\n\n')


def printTasksTree(tasks, level=0):
    def traverse(task, level):
        nonlocal tasks
        nonlocal levels
        nonlocal ret

        left = '\n'
        for l in range(level):
            if l in levels:
                left += '│'
            else:
                left += ' '
        forkChar = '├' if level in levels else '└'
        ret += left+forkChar+task['taskID']
        prevs = [tasks[id] for id in toInt(task["previous"])]

        if len(prevs) == 0:
            ret += '⏤ START'
        #
        if len(prevs) > 1:
            levels.append(level+1)

        for child in prevs:
            traverse(child, level+1)
            
        if level in levels:
            levels.remove(level)
    
    levels = []
    ret = '\nEND'
    
    orphaned = getOrphaned(tasks) 

    if len(orphaned) > 1:
        levels.append(0)

    for task in orphaned:
        ret += '\n│\n│'
        traverse(task, level)

    print(ret)


def printPaths(paths):
    print('\n')
    for path in paths:
        duration = 0

        print('START', end=' ➡ ')
        for task in reversed(path):
            duration += task['times']['expected']
            print(task['taskID'], end=' ➡ ')
        print('END     (expecting {:.1f} weeks)'.format(duration))





if __name__ == '__main__':

    taskData = readData("wiki-tasks.json")
    # N(0,1)
    distr = readData('normal-distribution-table.csv', dataName='distribution')
    # print(distr['-3.73'])

    """ 
        Dane należy przeskalować w taki sposób, aby posiadały wartość średnią 
        równą 0 i odchylenie standardowe równe 1.

            X = (td - tr) / σ

                X - czas przeskalowany do N(0,1)
                td - czas dyrektywny 🤔
                tr - czas modelowy ukończenia przedsięwzięcia 🤔
                σ - odchylenie standardowe
            
        Prawdopodobieństwo zakończenia przedsięwzięcia w terminie do td:

            P(td ≤ tr) = ϕ(x)
            ϕ(x) = 1 - ϕ(-x)

    """

    #printTasksTree(taskData)
    calculateExpected(taskData)
    calculateStandardDeviation(taskData)
    calculateVariation(taskData)
    printTimes(taskData)

    PERT(taskData)
    printTasks(taskData)
    print('Critical paths:')
    criticalPaths = findCriticalPaths(taskData)
    printPaths(criticalPaths)

    # docs
    # https://mfiles.pl/pl/index.php/PERT
    # https://4business4you.com/biznes/zarzadzanie-projektami/metoda-pert-w-praktyce/
