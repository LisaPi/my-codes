#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-10-08
@author: beyondzhou
@name: bridgeBasicInfo.py
'''

def bridgeBasicInfo():
    
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeCmd, cliBridgeReset
    from guiCommLib import guiAddBridge, guiAddPortIntoBridge
    import re
    import myglobals
    
    # Capture and delete all bridge at switch if there exist
    cli = loginCli()
    cliBridgeReset(cli)
            
    print ':::Step 1: add two bridges and add port into bridge through gui'
    guiPortList = {'br0': [1,2,3,4,5,6,7,8,9,10], 'br1': [11,12,13,14,15,16,17,18,19,20]}

    browser = loginPha()
    for num in range(2):
        guiAddBridge(browser, "br%s" % num)
    guiAddPortIntoBridge(browser, "br0", guiPortList['br0'])
    guiAddPortIntoBridge(browser, "br1", guiPortList['br1'])
    
    print ':::Step 2: get bridge basic information through cli'
    bridges = ['br0', 'br1']
    for bridge in bridges:
        subject = cliBridgeCmd(cli, "ovs-ofctl show %s | grep addr:" % bridge)
        expectPortList = [str(a) for a in guiPortList["%s" % bridge]]
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
    bridgeBasicInfo()