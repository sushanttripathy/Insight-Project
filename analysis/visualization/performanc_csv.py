__author__ = 'Sushant'
import csv

file_path = "performance_3.csv"

with open(file_path, "rb") as in_file:
    reader = csv.reader(in_file, delimiter=",")
    count = 0
    hits = 0
    misses = 0
    false_alarms = 0
    for row in reader:
        if row[0] != '':
            h = int(row[0])
            m = int(row[1])
            fa = int(row[2])
            count += 1

            if h:
                hits += 1
            if m:
                misses += 1
            if fa:
                false_alarms += 1
            if count % 50 == 0:
                print str(count) + "," + str(hits) + "," + str(misses) + "," + str(false_alarms)

    print str(count) + "," + str(hits) + "," + str(misses) + "," + str(false_alarms)