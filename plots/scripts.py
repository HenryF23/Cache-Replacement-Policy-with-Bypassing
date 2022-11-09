from asyncore import read
from operator import index
import os
import re
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

datadir = os.getenv("LAB_PATH") + '/results_10M/'

benchmarkList = ["600.perlbench_s-210B.champsimtrace.xz",
                 "602.gcc_s-734B.champsimtrace.xz",
                 "625.x264_s-18B.champsimtrace.xz",
                 "641.leela_s-800B.champsimtrace.xz",
                 "648.exchange2_s-1699B.champsimtrace.xz"]

benchmarkListShorten = ["600", "602", "625", "641", "648"]

# * This will return a float number
def readFloatingPointFromFile(fileName, valueName):
    val = 0
    with open(datadir + fileName) as f:
        r = f.read()
        matches = re.findall(valueName + " (\d+\.\d+)", r)
        if (len(matches) == 0):
            val = 0
        else:
            val = float(matches[0])
    
    return val

def readIntFromFile(fileName, valueName):
    val = 0
    with open(datadir + fileName) as f:
        r = f.read()
        matches = re.findall(valueName + " (\d+)", r)
        if (len(matches) == 0):
            val = 0
        else:
            val = int(matches[0])

    return val


def readIntFromFileWithLineNumber(fileName, valueName, lineNumber):
    val = 0
    with open(datadir + fileName) as f:
        r = f.readlines()
        matches = re.findall(valueName + " (\d+)", r[lineNumber])
        if (len(matches) == 0):
            val = 0
        else:
            val = int(matches[0])

    return val

def readFloatFromFileWithLineNumber(fileName, valueName, lineNumber):
    val = 0
    with open(datadir + fileName) as f:
        r = f.readlines()
        matches = re.findall(valueName + " (\d+\.\d+)", r[lineNumber])
        if (len(matches) == 0):
            val = 0
        else:
            val = float(matches[0])

    return val


if __name__ == "__main__":

    print("Done!")