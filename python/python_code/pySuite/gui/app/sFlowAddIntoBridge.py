#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-11-09
@author: beyondzhou
@name: sFlowAddIntoBridge.py
'''

def sFlowAddIntoBridge():
    
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeCmd, cliBridgeReset, cliPortsIdList
    from guiCommLib import guiAddBridge, guiAddPortIntoBridge, guiAddsFlowIntoBridge
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
    
    print ':::Step 2: add sFlow into bridges through gui'  
    bridge = "br0"
    sPolling = '20'
    sHeader = '128'
    sAgent = 'eth0'
    sSampling = '128'
    sIp = '1.1.1.1'
    sPort = 6622
    
    browser = loginPha()
    guiAddsFlowIntoBridge(browser, 
                           bridge=bridge,
                           sPolling = sPolling,
                           sHeader = sHeader,
                           sAgent = sAgent,
                           sSampling = sSampling,
                           sIp =  sIp,
                           sPort = sPort)  

    print ':::Step 3: get sFlow information through cli'
    time.sleep(5)
    cli = loginCli()
    subject = cliBridgeCmd(cli, "ovs-vsctl list sflow")
    if re.search(r'(?s)agent.*%s.*header.*%s.*polling.*%s.*sampling.*%s.*targets.*%s:%s' % (sAgent, sHeader, sPolling, sSampling, sIp, sPort), subject):
        print 'Add sFlow check Pass!'
    else:
        print 'Add sFlow check Fail!'
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
    sFlowAddIntoBridge()