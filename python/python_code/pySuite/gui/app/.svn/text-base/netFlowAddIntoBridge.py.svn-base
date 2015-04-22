#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-11-09
@author: beyondzhou
@name: netFlowAddIntoBridge.py
'''

def netFlowAddIntoBridge():
    
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeCmd, cliBridgeReset, cliPortsIdList
    from guiCommLib import guiAddBridge, guiAddPortIntoBridge, guiAddNetFlowIntoBridge
    import re
    import myglobals
    import time
    
    # Capture and delete all bridge at switch if there exist
    cli = loginCli()
    cliBridgeReset(cli)
     
    # Capture all ports id list
    portsIdList = cliPortsIdList(cli)
    cli.close()
    print 'portsIdList: ', portsIdList
           
    print ':::Step 1: add a bridge and add all ports into bridge through gui'
    bridge = "br0"
    browser = loginPha()
    guiAddBridge(browser, bridge) 
    guiAddPortIntoBridge(browser, bridge, portsIdList[:10])
    browser.quit()
    
    print ':::Step 2: add netFlow into bridges through gui'  
    bridge = "br0"
    sIp = '1.1.1.1'
    sTime = 100
    sPort = 6622
    
    browser = loginPha()
    guiAddNetFlowIntoBridge(browser, 
                           bridge=bridge,
                           sIp = sIp,
                           sTime = sTime,
                           sPort = sPort)  

    print ':::Step 3: get netFlow information through cli'
    time.sleep(5)
    cli = loginCli()
    subject = cliBridgeCmd(cli, "ovs-vsctl list netflow")
    if re.search(r'(?s)active_timeout.*%s.*targets.*%s:%s' % (sTime, sIp, sPort), subject):
        print 'Add netFlow check Pass!'
    else:
        print 'Add netFlow check Fail!'
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
    netFlowAddIntoBridge()