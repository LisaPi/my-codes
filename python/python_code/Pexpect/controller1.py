#!/usr/bin/env python

import pxssh
import pexpect
import getpass, os

# Do ssh command
def ssh_login (user, host, password):

    # Prompt
    loginprompt = '[$#>]'

    # Get spawn id
    s = pxssh.pxssh()
    s.login (host, user, password, original_prompt=loginprompt)
    return s

def controller (host, user, password, directory, target, ports):

    # Login
    child = ssh_login (user, host, password)

    # Kill pica controller to avoid confuse
    child.sendline ('pkill pica')
    child.prompt()
    print child.before

    # Swith to directory that controller is at
    child.sendline ('cd %s' % directory)
    child.prompt()
    print child.before
    child.sendline ('pwd')
    child.prompt()
    print child.before

    # Set env
    for e in ["export CTRLR_SYSCONFDIR=.", "export CTRLR_PKGDATADIR=.", "export CTRLR_RUNDIR=.", "export CTRLR_LOGDIR=.", "export CTRLR_DBDIR=."]:
        child.sendline ('%s' % e)
        child.prompt()
        print child.before

    # Delete db before and create new db
    child.sendline ('rm -rf controller.db')
    child.prompt()
    print child.before
    child.sendline ('rm -rf running.db')
    child.prompt()
    print child.before
    for t in ["controller", "running"]:
        child.sendline ('./ovsdb-tool create ./%s.db ./%s.schema' % (t, t))
        child.prompt()
        print child.before

    # Start controller
    child.sendline ('./pica-ctrlr controller.db running.db --remote=ptcp:6640:%s &' % host)
    child.expect('pica-ctrlr controller.db running.db --remote=ptcp:6640')
    print child.before

    # Check whether controller is alive
    child.sendline ('ps aux | grep pica')
    child.expect('ps aux')
    print child.before

    # Delete bridege before
    child.sendline ('./ctrlr-vsctl del-sw sw0')
    child.expect('ctrlr-vsctl del-sw')
    print child.before

    # Create bridge
    child.sendline ('./ctrlr-vsctl add-sw sw0 -- set switch sw0 target=%s' % target)
    child.expect('ctrlr-vsctl add-sw sw0')
    print child.before
    child.sendline ('./ctrlr-vsctl add-br sw0 sw0_br0 -- set bridge sw0_br0 datapath_type=pica8 datapath_id=2113456789abcdef local_controller_role=master')
    child.expect('ctrlr-vsctl add-br sw0')
    print child.before

    # Add ports into bridge
    for port in ports:
        child.sendline ('./ctrlr-vsctl add-port sw0_br0 sw0_%s vlan_mode=trunk tag=1 -- set Interface sw0_%s type=pica8' % (port,port))
        child.expect('ctrlr-vsctl add-port sw0')
        print child.before

    # Set controller for bridge
    child.sendline ('./ctrlr-vsctl set-controller sw0_br0 tcp:%s:6633' %host)
    child.expect('ctrlr-vsctl set-controller')
    print child.before

    # Create bridge for switch
    child.sendline ('./ctrlr-vsctl show')
    child.expect('ctrlr-vsctl show')
    print child.before

    child.sendline ('pwd')
    child.expect('pwd')
    print child.before

    return child
