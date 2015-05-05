#!/usr/bin/python


import pexpect
import login
import login1
import re
import os 
import time


vlans = [i for i in range(2,4095)]
ports = [i for i in range(2,4)]
prompt = '[$#>]'
ip,username,password,port,cmd = login.xorpinfo()
print ip,username,password,port,cmd

print "###Test start###"
#login sw
child = login1.Xorp_config(ip,username,password)

#send linux commands
for icmds in cmd:
    login1.sendExpect(child,icmds,prompt)

#Configure vlans and ports
for iport in ports: 
    print 'iport :',iport
    for ivlan in vlans:
        print 'ivlan :',ivlan
        login1.sendExpect(child,'/xorplus/bin/xorplus_sh -c "configure;set interface gigabit-ethernet ge-1/1/%s family ethernet-switching vlan members %s;commit"' %(iport,ivlan),prompt)
        time.sleep(15)
#for ivlan in vlans:
#    print 'ivlan :',ivlan
#    login1.sendExpect(child,'/xorplus/bin/xorplus_sh -c  "configure;set interface gigabit-ethernet ge-1/1/1 family ethernet-switching vlan members %s;commit"' %(ivlan),prompt)
#    time.sleep(11)
