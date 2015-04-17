#!/usr/bin/env python

f=open('/home/lpi/test/public/3.txt','w+')
l=['a','b','c','d','e']
for i in l:
    f.writelines(i+'\n')
    #f.writelines('\n')
f.close()

