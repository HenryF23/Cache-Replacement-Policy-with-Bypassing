
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

def plot():
    files = ["lru", "slru_lru_with_bp_and_selector"]
    counter = 0
    rows = []

    for benchmark in benchmarkList:
        tempRow = []
        for file in files:
            filename = benchmark + "-perceptron-no-no-no-" + file + "-1core.txt"
            llc_total_hit = readIntFromFile(
                filename, "Core_0_LLC_total_hit")
            llc_total_miss = readIntFromFile(
                filename, "Core_0_LLC_total_miss")
            llc_total_access = readIntFromFile(
                filename, "Core_0_LLC_total_access")
            tempRow.append(llc_total_hit)
        rows.append(tempRow)

    print(rows)
    df = pd.DataFrame(rows, columns=files)
    df.index = benchmarkListShorten

    df.plot(kind='bar')

    plt.title("performance comparison: lru vs full version", fontdict={'fontsize': 10})
    plt.ylabel("Miss Rate")
    plt.xticks(rotation=0)
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig('test_henry_' + str(counter) + '.png', format='png', dpi=600)
    counter = counter + 1
    print(df)


if __name__ == "__main__":
    plot()
