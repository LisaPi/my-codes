#!/usr/bin/env python

from controller import *

# Start controller, create bridge, add ports into bridge
child = controller(host, user, password, directory, target, ports)

# Set env
for e in ["export CTRLR_SYSCONFDIR=.", "export CTRLR_PKGDATADIR=.", "export CTRLR_RUNDIR=.", "export CTRLR_LOGDIR=.", "export CTRLR_DBDIR=."]:
    sendExpect(child, '%s' % e, prompt)

# Check whether controller is alive
sendExpect(child, 'ps aux | grep pica', prompt)

# Add flow table 0
sendExpect(child, './ctrlr-vsctl -- set Bridge sw0_br0 flow_tables:0=@ft -- --id=@ft create Flow_Table name=table0', prompt)
sendExpect(child, './ctrlr-vsctl list flow_table', prompt)

# Add table miss flow
sendExpect(child, './ctrlr-vsctl -- add Flow_Table table0 static_flows @sf0 -- --id=@sf0 create Static_Flow name=sf0 match:eth_src=22:11:11:11:11:11 actions:output=controller', prompt)

# Add dynamic flow
sendExpect(child, './ctrlr-vsctl -- set Flow_Table table0 dynamic_flows=@df0 -- --id=@df0 create Dynamic_Flow name=df0', prompt)

# Set priority and match and static flow on Dynamic_Flow df0
sendExpect(child, './ctrlr-vsctl -- set Dynamic_Flow df0 priority=1 match:eth_src=22:11:11:11:11:11', prompt)
sendExpect(child, './ctrlr-vsctl -- set Dynamic_Flow df0 flows=@flow -- --id=@flow create Static_Flow name=sf1 match:{in_port=in_port,eth_dst=22:00:00:00:00:00} actions:output=all', prompt)
sendExpect(child, './ctrlr-vsctl list dynamic_flow', prompt)
sendExpect(child, './ctrlr-vsctl list static_flow', prompt)
sendExpect(child, 'ps aux | grep pica', prompt)

# Send packets to swith to generate dynamic flow
while 1:
    print "Please send packets (source mac is 22:11:11:11:11:11) to swith to generate dynamic flow!!!"
    print "Have sent packets to swith "
    answer = raw_input('y/n: ')

    if answer == 'y':
        break

# Check dynamic flow at switch (Suppose user:admin password:123456 for switch)
switch = ssh_login('admin', target, '123456')
sendExpect(switch, 'ovs-ofctl dump-flows br0', prompt)
sendExpect(switch, 'ovs-ofctl show br0', prompt)

# Do the flow check
result = checkCmd(switch, 'ovs-ofctl dump-flows br0', '22:00:00:00:00:00')
if result:
    print 'Dynamic single flow check Pass!'
else:
    print 'Dynamic single flow check Fail!'

# End
#sendExpect(switch, 'exit', '.*')
#sendExpect(child, 'exit', '.*')
