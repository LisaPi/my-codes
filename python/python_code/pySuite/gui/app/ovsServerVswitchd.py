#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-10-08
@author: beyondzhou
@name: ovsServerVswitchd.py
'''

def ovsServerVswithd():
    from login import loginCli
    from cliCommLib import cliCheckCmd, cliRunCmd
    import myglobals
    
    ssh = loginCli()

    # Use dict to store ovs server and client
    ovsProcess = {'server': 'ovsdb-server', 'client': 'ovs-vswitchd'}

    # Check ovsdb-server/ovs-vswitchd startup normally or not   
    for key in ovsProcess:
        cmd = 'ps aux | grep %s | grep -v grep' % ovsProcess[key]
        match = ovsProcess[key]      
        cliCheckCmd(ssh, cmd, match)

    # Clear config
    cmds = '''
    ps aux | grep ovs
    ls /ovs/ovs-vswitchd.conf.db
    '''
    cliRunCmd(ssh, cmds)
    ssh.close()

    # Conclusion
    if myglobals.g_iResult == 0:
        print '\nThe test pass!'
    else:
        print '\nThe test fail!'
        
if __name__ == "__main__":
    ovsServerVswithd()