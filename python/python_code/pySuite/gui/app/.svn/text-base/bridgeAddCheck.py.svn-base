#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-11-09
@author: beyondzhou
@name: bridgeAddCheck.py
'''

def bridgeAddCheck():
    
    import time
    
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeNum, cliBridgeReset
    
    from guiCommLib import guiAddBridge
    
    import myglobals
    
    print ':::Step 1: delete bridge through cli'
    # Login into switch through cli
    cli = loginCli()
    cliBridgeReset(cli)
    
    print ':::Step 2: login in switch and add bridges through gui'
    expect_bridge_number = 10
    browser = loginPha()
    for num in range(expect_bridge_number):
        guiAddBridge(browser, "br%s" % num)
        
    time.sleep(1)
    
    print ':::Step 3: login in switch and check bridges through cli'
    actual_bridge_number = cliBridgeNum(cli)
    print 'Expect bridge num: %s' % expect_bridge_number
    print 'Actual bridge num: %s' % actual_bridge_number
    if expect_bridge_number == actual_bridge_number:
        print 'Bridge number check pass!'
    else:
        print 'Bridge number check fail'
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
    bridgeAddCheck()