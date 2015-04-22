#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-10-08
@author: beyondzhou
@name: portAddIntoBridge.py
'''

def portAddIntoBridge():
    
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeCmd, cliBridgeReset, cliPortsIdList
    from guiCommLib import guiAddBridge, guiAddPortIntoBridge
    import re
    import myglobals
    import time
    
    # Capture and delete all bridge at switch if there exist
    cli = loginCli()
    cliBridgeReset(cli)
     
    # Capture all ports id list
    portsIdList = cliPortsIdList(cli)
    print 'portsIdList: ', portsIdList
           
    print ':::Step 1: add a bridge and add all ports into bridge through gui'
    bridge = "br0"
    browser = loginPha()
    guiAddBridge(browser, bridge) 
    guiAddPortIntoBridge(browser, bridge, portsIdList)
    
    print ':::Step 2: get bridge basic information through cli'
    time.sleep(1)
    subject = cliBridgeCmd(cli, "ovs-ofctl show %s | grep addr:" % bridge)
    expectPortList = portsIdList
    actualPortList = re.findall(r"([0-9]+)\(.*?\)", subject)
    print 'expectPortList: %s' % expectPortList
    print 'actualPortList: %s' % actualPortList
    if actualPortList == expectPortList:
        print 'PortList check pass for brige:%s' % bridge
    else:
        print 'PortList check fail for brige:%s' % bridge
        myglobals.g_iResult = 1 

    # Reset config
    cliBridgeReset(cli)
    browser.quit()
    cli.close()
    
    # Conclusion
    if myglobals.g_iResult == 0:
        print '\nThe test pass!'
    else:
        print '\nThe test fail!'
        
if __name__ == "__main__":
    portAddIntoBridge()