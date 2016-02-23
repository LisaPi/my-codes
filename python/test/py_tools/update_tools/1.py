#!/usr/bin/env python


def a():
    b = {}
    for i in range(3):
        b['part' + str(i)] = i
    print b['part0']
    print b['part1']
    print b['part2']
    print b
a() 
