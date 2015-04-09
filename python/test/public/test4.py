#!/usr/bin/env python

import login1
import os
import time

f=open("login.txt")
line = f.readlines()
f.close()

for info in line:
    a=info.split()
#Login SW
child=login1.ssh_login(a[0],a[1],a[2])


f=open("2.txt")
lines = f.readlines()  
f.close()


for data in lines:

    print 'data:', data
    b=data.split()
    command=[b[0],b[1]]
    #Send Linux commands
    for cmd in command:
        login1.sendExpect(child,cmd,b[2])

    #check version
    result = login1.checkCmd (child, b[0],b[5])
    print result
    if result:
        print 'check is correct'
    else:
        print 'check is wrong'
