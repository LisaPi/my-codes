#!/usr/bin/python


import time
import re
import pexpect 
import login
import login1
import os


prompt = '[$#>]'
bridge = 'br0'
in_port = '1'
out_put = '2'


ip,user,password,directory,ports,cmds = login.userinfo()
print ip,user,password,directory,ports,cmds
child = login1.pica8_config(ip, user, password, directory, ports)

#Create bridge br0 and add ports
for icmd in cmds:
    login1.sendExpect(child, icmd, prompt)
    time.sleep(0.5)
time.sleep(1)
for iport in ports:
    login1.sendExpect(child, 'ovs-vsctl add-port %s  %s vlan_mode=trunk tag=1 -- set Interface %s type=pica8' % (bridge,iport,iport), prompt)
    time.sleep(0.5)
time.sleep(1)
login1.sendExpect(child,'ovs-ofctl show %s' % bridge,prompt)

#Add flow
login1.sendExpect(child,'ovs-ofctl add-flow %s in_port=%s,actions=output:%s' % (bridge,in_port,out_put),prompt)
time.sleep(2)

#check the configure
#subject = login1.sendExpect(child,'ovs-ofctl dump-flows br0',prompt)
#print 'type(subject):', type(subject)

#match = re.search(r"in_port=([0-9]+).*actions=([a-zA-Z0-9:]+)", str(subject))
#print match.group(1),match.group(2)

#if re.search(r'in_port=%s.*output:%s' % (in_port,out_put),str(subject)):
#    print 'Configure check pass for %s' % bridge
#else:
#    print 'Cofigue check failed for %s' % bridge
result = login1.checkCmd (child, 'ovs-ofctl dump-flows %s' % bridge, 'in_port=%s.*output:%s' % (in_port,out_put))
if result :
    print 'Configure check pass for %s' % bridge
else:
    print 'Configure check faild ofr %s' % bridge

