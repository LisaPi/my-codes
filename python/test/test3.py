#!/usr/bin/env python

import login
import os
import time


f=open("1.txt")
line = f.readline()  
f.close()


for data in line:
    a=line.split()
    #print data
    #print a

ip=a[0]
#print ip
user=a[1]
#print user
password=a[2]
#print password
command=[a[3],a[4]]
#print command

#login SW 
login.pica8_login(ip,user,password,command,port=22)

