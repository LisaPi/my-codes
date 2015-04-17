#!/usr/bin/env python


import os
import sys

if len(sys.argv) <> 3:
    print "Usage: " + sys.argv[0] + "file1 file2"
    sys.exit(-1)

file1 = sys.argv[1]
file2 = sys.argv[2]

list1 = {}
for line in open(file1):
    list1[line.split()[0]] = 1
for line in open(file2):
    key = line.split()[0]
    if key not in list1:
        sys.stdout.write(line)
            


