#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-11-09
@author: beyondzhou
@name: meterDelOfBridge.py
'''

def meterDelOfBridge():
    
    from login import loginCli, loginPha
    from cliCommLib import cliBridgeCmd, cliBridgeReset, cliPortsIdList
    from guiCommLib import guiAddBridge, guiAddPortIntoBridge, guiDelMeterOfBridge, guiAddMeterIntoBridge
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
    
    print ':::Step 2: add meter into bridges through gui'  
    bridge = "br0"
    meterid = "100"
    meterflag = "all"
    metertype = "DSCP_REMARK"
    meterrate = 1000
    meterburst = 1000
    meterpreclevel = 1
    
    browser = loginPha()
    guiAddMeterIntoBridge(browser, 
                          bridge=bridge,
                          meterid=meterid, 
                          meterflag=meterflag,
                          metertype=metertype,
                          meterrate=meterrate,
                          meterburst=meterburst,
                          meterpreclevel=meterpreclevel)  
    browser.quit()
    
    print ':::Step 3: get meter information through cli'
    time.sleep(5)
    cli = loginCli()
    subject = cliBridgeCmd(cli, "ovs-ofctl dump-meters br0")
    if re.search('meter=%s kbps stats bands' % (meterid), subject):
        print 'Meter add check pass for brige:%s' % bridge
    else:
        print 'Meter add check fail for brige:%s' % bridge
        myglobals.g_iResult = 1 
        
    print ':::Step 4: del meter through gui'
    browser = loginPha()
    guiDelMeterOfBridge(browser, bridge="br0", meterid=meterid)

    print ':::Step 5: get meter information through cli'
    time.sleep(5)
    cli = loginCli()
    subject = cliBridgeCmd(cli, "ovs-ofctl dump-meters br0")
    if re.search('meter=%s kbps stats bands' % (meterid), subject):
        print 'Meter del check fail for brige:%s' % bridge
        myglobals.g_iResult = 1 
    else:
        print 'Meter del check Pass for brige:%s' % bridge

               
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
    meterDelOfBridge()