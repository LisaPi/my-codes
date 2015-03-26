#!/usr/bin/python


import pexpect
import login
import login1
import re
import os 
import time


vlans = ['2','3']
prompt = '[$#>]'
ip,username,password,port,cmd = login.xorpinfo()
print ip,username,password,port,cmd

print "###Test start###"
#login sw
child = login1.Xorp_config(ip,username,password)

#send linux commands
for icmds in cmd:
    login1.sendExpect(child,icmds,prompt)


#send CLI commands
for iport in port:
    print 'iport:', iport
    login1.sendExpect(child,'/pica/bin/pica_sh -c "configure;set interface gigabit-ethernet %s disable true;commit"' %(iport), prompt)
    time.sleep(8)

#Configure vlans
for ivlan in vlans:
    print 'ivlan:', ivlan
    login1.sendExpect(child,'/pica/bin/pica_sh -c "configure;set vlans vlan-id %s;commit"' %(ivlan),prompt)
    time.sleep(6)

#Check the vlan configuration
#subject = login1.sendExpect(child,'/pica/bin/pica_sh -c "show vlans"',prompt)
#if re.search(r'%s.*%s' % (vlans[0],vlans[1]),str(subject)):
#    print 'Check pass'
#else:
#    print 'Check fail'
time.sleep(5) 
result = login1.checkCmd (child, '/pica/bin/pica_sh -c "show vlans"', '%s.*%s'  % (vlans[0],vlans[1]))
if result :
    print "chekc pass for vlans!"
else:
    print "check fail for vlans!"

#Clear the configuration 
time.sleep(8)
for ivlan in vlans:
    print 'ivlan :', ivlan
    login1.sendExpect(child,'/pica/bin/pica_sh -c "configure;delete vlans vlan-id %s;commit"' %(ivlan),prompt)
    time.sleep(10) 
time.sleep(8)    
for iport in port:
    login1.sendExpect(child,'/pica/bin/pica_sh -c "configure;set interface gigabit-ethernet %s disable false;commit"' %(iport), prompt)
    time.sleep(8)
time.sleep(10)

print "###Test end###"
