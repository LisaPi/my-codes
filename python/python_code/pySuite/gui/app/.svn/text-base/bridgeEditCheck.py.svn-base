#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-10-08
@author: beyondzhou
@name: bridgeEditCheck.py
'''

def bridgeEditCheck():
    
    import time
    import re 
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeReset, cliBridgeCmd
    from guiCommLib import guiAddBridge, guiEditBridge
    
    import myglobals
    
    print ':::Step 1: delete bridge through cli'
    # Login into switch through cli
    cli = loginCli()
    cliBridgeReset(cli)
    
    print ':::Step 2: login in switch and add bridges through gui'
    bridge = "br0"
    browser = loginPha()
    guiAddBridge(browser, bridge)
    time.sleep(1)
    browser.quit()
    
    print ':::Step 3: login in switch and check bridge through cli'
    subject = cliBridgeCmd(cli, "ovs-vsctl list Bridge")   
    if re.search('%s' % (bridge), subject):
        print 'Bridge check pass!'
    else:
        print 'Bridge check fail'
        myglobals.g_iResult = 1    
    
    print ':::Step 4: login in switch and edit bridges through gui'
    new_datapathid = '1271961bdcb6bd49'
    new_failmode = 'secure'
    
    browser = loginPha()
    guiEditBridge(browser, bridge, 
                  datapathid = new_datapathid,
                  failmode = new_failmode)
    time.sleep(1)
    browser.quit()

    print ':::Step 5: login in switch and check bridges through cli'
    time.sleep(1)
    subject = cliBridgeCmd(cli, "ovs-vsctl list Bridge")   
    if re.search("(%s).*?(%s)" % (new_datapathid, new_failmode), subject, re.DOTALL):
        print 'Edit Bridge check pass!'
    else:
        print 'Edit Bridge check fail'
        myglobals.g_iResult = 1
        
    # Reset config
    cliBridgeReset(cli)
    cli.close()
    browser.quit()
    
    # Conclusion
    if myglobals.g_iResult == 0:
        print '\nThe test pass!'
    else:
        print '\nThe test fail!'
        
if __name__ == "__main__":
    bridgeEditCheck()