__author__ = 'Sushant'
import os

with open("catenated.txt", "w") as out_file:
    with open("catenator.txt", "r") as in_file:
        out_buf = ""
        while True:
            line = in_file.readline()
            line = line.strip()
            if len(line):
                print os.path.getsize(line)
                if os.path.isfile(line) and os.path.getsize(line):
                    print "Reading : "+line
                    with open(line, "r") as in_file2:
                        buf = in_file2.read()
                        out_buf += buf
            if not line:
                break
        out_file.write(out_buf)

