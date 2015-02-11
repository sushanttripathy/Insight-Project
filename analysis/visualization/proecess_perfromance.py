__author__ = 'Sushant'
import os

cwd = os.curdir
performance_res = os.path.join(cwd, "..", "..", "data", "performance", "resultados.txt")

with open(performance_res, "r") as in_file:
    count  = 0
    while True:
        line = in_file.readline()
        #print line
        if count > 2:
            new_line  = line.replace("|", ",")
            print new_line
        count += 1
        if not line:
            break