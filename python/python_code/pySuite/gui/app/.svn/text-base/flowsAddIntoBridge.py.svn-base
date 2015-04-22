#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-11-09
@author: beyondzhou
@name: flowsAddIntoBridge.py
'''

def flowsAddIntoBridge():
    
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeCmd, cliBridgeReset, cliPortsIdList
    from guiCommLib import guiAddBridge, guiAddPortIntoBridge, guiAddFlowsIntoBridge
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
    
    print ':::Step 2: add flows into bridges through gui'  
    bridge = "br0"
    flows = '''in_port=1,actions=2
               in_port=2,actions=1
               in_port=3,actions=4
               in_port=4,actions=3'''
    
    browser = loginPha()
    guiAddFlowsIntoBridge(browser, 
                          bridge=bridge,
                          flows=flows)  

    print ':::Step 3: get flows information through cli'
    time.sleep(5)
    cli = loginCli()
    subject = cliBridgeCmd(cli, "ovs-ofctl dump-flows br0")
    flows = flows.split('\n')
    for flow in flows:
        match = re.search(r"in_port=([0-9]+).*actions=([a-zA-Z0-9:]+)", flow)
        in_port = match.group(1)
        actions = match.group(2)
        if re.search(r'in_port=%s.*output:%s' % (in_port, actions), subject):
            print 'Flow with in_port=%s actions=%s check Pass!' % (in_port, actions)
        else:
            print 'Flow with in_port=%s actions=%s check Fail!' % (in_port, actions)
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
    flowsAddIntoBridge()