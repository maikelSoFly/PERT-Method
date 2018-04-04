import json
import os

def readData(dataName):
    dataPath = os.path.join("../data", dataName)
    with open(dataPath, 'r') as f:
            return f.read()

if __name__ == '__main__':
    readData("tasks.json")
