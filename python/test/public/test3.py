#!/usr/bin/env python

import login1
import os
import time

f=open("login.txt")
line = f.readlines()
f.close()

for info in line:
    a=info.split()
    ip=a[0]
    user=a[1]
    password=a[2]
#Login SW
child=login1.ssh_login(ip,user,password)


f=open("1.txt")
lines = f.readlines()  
f.close()


for data in lines:
    b=data.split()
    command=[b[0],b[1]]
    print command
    prompt=b[2]
    print prompt
    platform=b[5]
    num=b[6]
    print num

#Send Linux commands
for cmd in command:
    login1.sendExpect(child,cmd,prompt)

#check version
result = login1.checkCmd (child, 'version',num)
print result
if result:
    print 'version number is correct'
else:
    print 'version number is wrong'
