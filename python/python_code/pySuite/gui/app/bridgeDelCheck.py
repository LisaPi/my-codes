#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-10-08
@author: beyondzhou
@name: bridgeDelCheck.py
'''

def bridgeDelCheck():
    
    import time
    import re 
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeReset, cliBridgeCmd
    from guiCommLib import guiAddBridge, guiDelBridge
    
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
    
    print ':::Step 4: login in switch and del bridges through gui'
    browser = loginPha()
    guiDelBridge(browser, bridge)
    time.sleep(1)
    browser.quit()

    print ':::Step 5: login in switch and check bridges through cli'
    time.sleep(1)
    subject = cliBridgeCmd(cli, "ovs-vsctl list Bridge")   
    if re.search("%s" % bridge, subject):
        print 'Del Bridge check fail!'
        myglobals.g_iResult = 1
    else:
        print 'Del Bridge check pass'

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
    bridgeDelCheck()