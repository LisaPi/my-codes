#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-10-08
@author: beyondzhou
@name: controllerAddCheck.py
'''

def controllerAddCheck():
    
    import time
    import re
    
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeCmd, cliBridgeReset
    
    from guiCommLib import guiAddBridge, guiAddControllerIntoBridge
    
    import myglobals
    
    print ':::Step 1: delete bridge through cli'
    # Login into switch through cli
    cli = loginCli()
    cliBridgeReset(cli)
    
    print ':::Step 2: login in switch and add bridges through gui'
    bridge = 'br0'
    browser = loginPha()
    guiAddBridge(browser, bridge)
    time.sleep(1)
 
    print ':::Step 3: login in switch and add controller into bridges through gui'
    controllerIp = '10.10.50.41'
    controllerPort = '1234'
    guiAddControllerIntoBridge(browser, bridge, ip_address=controllerIp, port=controllerPort)

    print ':::Step 4: login in switch and check controller through cli'
    time.sleep(1)
    subject = cliBridgeCmd(cli, "ovs-vsctl list controller")   
    if re.search('tcp:%s:%s' % (controllerIp, controllerPort), subject):
        print 'Controller check pass!'
    else:
        print 'Controller check fail'
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
    controllerAddCheck()