#!/usr/bin/env python

from controller import controller
from controller import ssh_login

##################################################
# Define your own information
#
# host:       the server ip that controller is running
# user:       the user name to access to above server
# password:   the password for the above user
# directory:  the directory where controller stores
# target:     the swith ip
# ports:      the ports of above switch
##################################################
host = '10.10.50.42'
user = 'root'
password = 'pica8'
directory = '/home/ychen/ctrlr/run'
target = '10.10.50.142'
ports = ['ge-1/1/1', 'ge-1/1/2']

# Start controller, create bridge, add ports into bridge
child = controller(host, user, password, directory, target, ports)

# Set env
for e in ["export CTRLR_SYSCONFDIR=.", "export CTRLR_PKGDATADIR=.", "export CTRLR_RUNDIR=.", "export CTRLR_LOGDIR=.", "export CTRLR_DBDIR=."]:
    child.sendline ('%s' % e)
    child.expect('.*')
    print child.before


# Add flow table 0
child.sendline ('./ctrlr-vsctl -- set Bridge sw0_br0 flow_tables:0=@ft -- --id=@ft create Flow_Table name=table0')
child.expect('ctrlr-vsctl')
print child.before
child.sendline ('./ctrlr-vsctl list flow_table')
child.expect('ctrlr-vsctl')
print child.before



#Add a static flow with flow action Meter
child.sendline('./ctrlr-vsctl -- set Bridge sw0_br0 meters:0=@mt -- --id=@mt create Meter name=mt0 id=1 band:{type=drop,rate=10000}')
child.expect('ctrlr-vsctl')
print child.before
child.sendline('./ctrlr-vsctl list meter')
child.expect('ctrlr-vsctl')
print child.before

child.sendline('./ctrlr-vsctl -- add Flow_Table table0 static_flows @sf2 -- --id=@sf2 create Static_Flow name=sf4 match:{in_port=1,eth_type=0x0800,eth_dst=22:22:22:22:22:22} actions:meter=1,output=2')
child.expect('ctrlr-vsctl')
print child.before

child.sendline('./ctrlr-vsctl --static list-flow sw0_br0')
child.expect('ctrlr-vsctl')
print child.before

#let the switch connect to controller
child.sendline('./ctrlr-vsctl set-controller sw0_br0 tcp:10.10.50.42:6633')
child.expect('ctrlr-vsctl')
print child.before


#end
child.sendline ('ps aux | grep pica')
child.expect('ps aux')
print child.before

