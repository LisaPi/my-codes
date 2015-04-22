#!/usr/bin/env python

import pxssh
import pexpect
import getpass, os
import re

prompt = '[$#>]'

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
host = '10.10.50.45'
user = 'root'
password = 'pica8sqa'
directory = '/home/build/ctrlr/run'
target = '10.10.50.177'
ports = ['te-1/1/1', 'te-1/1/2', 'te-1/1/3', 'te-1/1/4']

# Do ssh command
def ssh_login (user, host, password):

    # Prompt
    loginprompt = '[$#>]'

    # Get spawn id
    s = pxssh.pxssh()
    s.login (host, user, password, original_prompt=loginprompt, login_timeout=1000000)
    return s

# Do send and expect
def sendExpect (child, command, prompt):

    child.sendline ('%s' % command)
    child.expect('%s' % prompt)
    print "%s%s" % (child.after,child.before)

# Do cmd check
def checkCmd (child, command, expect_value):

    child.sendline ('%s' % command)
    child.expect('(.*)%s' % prompt)
    match = child.match.group()

    flag = re.search('%s' % expect_value, match)   
    return flag   

# Generate any number mac address being in incr order
def geneMac(mac, num):
    # Change the mac address format into list with its value type is string
    macs = mac.split(':')

    num = int(num)
    print '11111111111'
    print type(num)
    print '22222222222'
    # Change the string list into int list
    #macs = map(int, macs)
    macs = [int(x, 16) for x in macs]

    # Change the value of list into hex format
    macs = ''.join('%02x'%i for i in macs)
    tmp = '0x'
    macs = tmp + macs
    macs = int(macs,16)

    # Generate mac address
    sMacs = []
    for i in range(macs, macs + num):
        j = (i >> 40) & 0xFF
        k = format(j, "02x")
        sMac = k

        j = (i >> 32) & 0x00FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = (i >> 24) & 0x0000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = (i >> 16) & 0x000000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = (i >> 8) & 0x00000000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = i & 0x0000000000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        sMacs.append(sMac)

    # Return the mac list
    return sMacs

def controller (host, user, password, directory, target, ports):

    # Login
    child = ssh_login (user, host, password)

    # Kill pica controller to avoid confuse
    sendExpect(child, 'pkill pica', prompt)

    # Swith to directory that controller is at
    sendExpect(child, 'cd %s' % directory, prompt)

    # Set env
    for e in ["export CTRLR_SYSCONFDIR=.", "export CTRLR_PKGDATADIR=.", "export CTRLR_RUNDIR=.", "export CTRLR_LOGDIR=.", "export CTRLR_DBDIR=."]:
        sendExpect(child, '%s' % e, prompt)

    # Delete db before and create new db
    for d in ["controller.db", "running.db"]:
        sendExpect(child, 'rm -rf %s' % d, prompt)
    for t in ["controller", "running"]:
        sendExpect(child, './ovsdb-tool create ./%s.db ./%s.schema' % (t, t), prompt)

    # Start controller
    sendExpect(child, './pica-ctrlr controller.db running.db --remote=ptcp:6640:%s &' % host, prompt)

    # Check whether controller is alive
    sendExpect(child, 'ps aux | grep pica', prompt)

    # Delete bridege before
    sendExpect(child, './ctrlr-vsctl del-sw sw0', prompt)

    # Create bridge
    did = '2113456789abcdef'
    sendExpect(child, './ctrlr-vsctl add-sw sw0 -- set switch sw0 target=%s' % target, prompt)
    sendExpect(child, './ctrlr-vsctl add-br sw0 sw0_br0 -- set bridge sw0_br0 datapath_type=pica8 datapath_id=%s local_controller_role=master' % did, prompt)

    # Add ports into bridge
    for port in ports:
        sendExpect(child, './ctrlr-vsctl add-port sw0_br0 sw0_%s vlan_mode=trunk tag=1 -- set Interface sw0_%s type=pica8 options:link_speed=1G' % (port, port), prompt)

    # Set controller for switch
    sendExpect(child, './ctrlr-vsctl set-controller sw0_br0 tcp:%s:6633' % host, prompt)

    # Show bridge for switch
    sendExpect(child, './ctrlr-vsctl show', prompt)
    sendExpect(child, 'pwd', prompt)

    return child
