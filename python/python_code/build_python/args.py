#! /usr/bin/env python

import sys

def usage():
    print 'At least 2 arguments.'
    print 'Usage: args.py arg1 arg2 [arg3...]'
    sys.exit(1)

argc = len(sys.argv)
if argc < 3:
    usage()

print "number of args entered:", argc
print "args were:", sys.argv
