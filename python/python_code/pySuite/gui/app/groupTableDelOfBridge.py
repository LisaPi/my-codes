#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-11-08
@author: beyondzhou
@name: groupTableDelOfBridge.py
'''

def groupTableDelOfBridge():
    
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeCmd, cliBridgeReset, cliPortsIdList
    from guiCommLib import guiAddBridge, guiAddPortIntoBridge, guiAddGroupTableIntoBridge, guiDelGroupTableOfBridge
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
    guiAddPortIntoBridge(browser, bridge, portsIdList[:10])
    browser.quit()
    
    print ':::Step 2: add group table into bridges through gui'
    groupid = "100"
    grouptype = "all"
    actions = "output:2"
    browser = loginPha()
    guiAddGroupTableIntoBridge(browser, bridge=bridge, groupid=groupid, grouptype=grouptype, actions=actions)
    browser.quit()
    
    print ':::Step 3: get group table information before del through cli'
    time.sleep(1)
    subject = cliBridgeCmd(cli, "ovs-ofctl dump-groups br0")
    if re.search('group_id=%s,type=%s,bucket=actions=%s' % (groupid, grouptype, actions), subject):
        print 'Group table before del check pass for brige:%s' % bridge
    else:
        print 'Group table before del check fail for brige:%s' % bridge
        myglobals.g_iResult = 1
        
    print ':::Step 4: del group table through gui'
    browser = loginPha()
    guiDelGroupTableOfBridge(browser, bridge="br0", groupid=groupid)

    print ':::Step 5: get group table information through cli'
    time.sleep(1)
    subject = cliBridgeCmd(cli, "ovs-ofctl dump-groups br0")
    if re.search('group_id=%s,type=%s,bucket=actions=%s' % (groupid, grouptype, actions), subject):
        print 'Group table del check fail for brige:%s' % bridge
        myglobals.g_iResult = 1
    else:
        print 'Group table del check pass for brige:%s' % bridge
               
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
    groupTableDelOfBridge()