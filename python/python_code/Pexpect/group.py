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

#Add group named g0, id=0, type=indirect
sendExpect(child, './ctrlr-vsctl -- set Bridge sw0_br0 groups:0=@gp -- --id=@gp create Group name=g0 id=0', prompt)
sendExpect(child, './ctrlr-vsctl -- set Group g0 type=indirect buckets=@bt -- --id=@bt create Bucket name=bt0', prompt)
sendExpect(child, './ctrlr-vsctl -- set Bucket bt0 actions:output=2', prompt)
sendExpect(child, './ctrlr-vsctl list group', prompt)
sendExpect(child, './ctrlr-vsctl list-group sw0_br0', prompt)


# Check group at switch (Suppose user:admin password:pica8 for switch)
switch = ssh_login('admin', target, '123123')
sendExpect(switch, 'ovs-ofctl dump-groups br0', prompt)
sendExpect(switch, 'ovs-ofctl show br0', prompt)

# Do the flow check
result = checkCmd(switch, 'ovs-ofctl dump-groups br0', '%s' % ('group_id=0,type=indirect,bucket=actions=output:2') )
if result:
    print 'Group adding Pass!'
else:
    print 'Group adding Fail!'

# End
sendExpect(switch, 'exit', '.*')
sendExpect(child, 'exit', '.*')

