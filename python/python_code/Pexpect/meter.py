#!/usr/bin/env python

#from controller import controller
#from controller import ssh_login
from controller import *
import time

# Start controller, create bridge, add ports into bridge
child = controller(host, user, password, directory, target, ports)

# Set env
for e in ["export CTRLR_SYSCONFDIR=.", "export CTRLR_PKGDATADIR=.", "export CTRLR_RUNDIR=.", "export CTRLR_LOGDIR=.", "export CTRLR_DBDIR=."]:
    sendExpect(child, '%s' % e, prompt)

# Check whether controller is alive
sendExpect(child, 'ulimit -c unlimited', prompt)
sendExpect(child, 'ps aux | grep pica', prompt)

#Add meter named mt0, id=1, type=drop
sendExpect(child, './ctrlr-vsctl -- set Bridge sw0_br0 meters:0=@mt -- --id=@mt create Meter name=mt0 id=1 band:{type=drop,rate=10000}', prompt)
sendExpect(child, './ctrlr-vsctl list meter', prompt)
sendExpect(child, './ctrlr-vsctl list-meter sw0_br0', prompt)


# Check group at switch (Suppose user:admin password:pica8 for switch)
switch = ssh_login('admin', target, '123123')
sendExpect(switch, 'ovs-ofctl dump-meters br0', prompt)
sendExpect(switch, 'ovs-ofctl show br0', prompt)

# Do the flow check
result = checkCmd(switch, 'ovs-ofctl dump-meters br0', '%s' % ('type=drop rate=10000') )
if result:
    print 'Meter adding Pass!'
else:
    print 'Meter adding Fail!'

# End
sendExpect(switch, 'exit', '.*')
sendExpect(child, 'exit', '.*')

