#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-11-08
@author: beyondzhou
@name: guiCommLib.py
'''

import time
from selenium.webdriver.support.ui import Select

# add bridge through gui
def guiAddBridge(browser, bridgeName):

    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    
    browser.find_element_by_link_text("Create a bridge").click()
    time.sleep(1)
    browser.find_element_by_xpath("//input[@type='text']").clear()
    browser.find_element_by_xpath("//input[@type='text']").send_keys(bridgeName)
    browser.find_element_by_css_selector("div.modal-footer > button.btn.btn-default").click()
    time.sleep(0)
    
    print 'Add bridge %s into switch done!' % bridgeName
    
    return

# edit bridge through gui
def guiEditBridge(browser, bridgeName,
                  datapathid = None,
                  failmode = None):

    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    
    browser.find_element_by_link_text(bridgeName).click()
    time.sleep(1)
    browser.find_element_by_link_text("Edit").click()
    time.sleep(1)
    if datapathid is not None:
        browser.find_element_by_name("datapath_id").clear()
        browser.find_element_by_name("datapath_id").send_keys(datapathid)
    if failmode is not None:
        Select(browser.find_element_by_xpath("//div[@id='editbasic']/div/div/div[2]/form/div[2]/select")).select_by_visible_text(failmode)
    browser.find_element_by_css_selector("#editbasic > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
    
    print 'Edit bridge %s from switch done!' % bridgeName
    
    return

# del bridge through gui
def guiDelBridge(browser, bridgeName):

    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    
    browser.find_element_by_link_text(bridgeName).click()
    time.sleep(1)
    browser.find_element_by_link_text("Delete").click()
    time.sleep(1)
    browser.find_element_by_xpath("(//button[@type='button'])[4]").click()
        
    print 'Del bridge %s from switch done!' % bridgeName
    
    return

# add controller into bridge through gui
def guiAddControllerIntoBridge(browser, bridge = None, 
                               method='Tcp', 
                               connection_mode='out-of-band', 
                               ip_address=None, 
                               port='6633'):  
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content

    browser.find_element_by_link_text(bridge).click()
    time.sleep(1)
    browser.find_element_by_link_text("Controllers").click()
    time.sleep(1)    
    browser.find_element_by_link_text("Add a new controller").click()
    time.sleep(1)  
    Select(browser.find_element_by_xpath("//div[@id='newctrl']/div/div/div[2]/form/div[2]/select")).select_by_visible_text(connection_mode)
    browser.find_element_by_name("ip").clear()
    browser.find_element_by_name("ip").send_keys(ip_address)
    browser.find_element_by_xpath("//input[@type='number']").clear()
    browser.find_element_by_xpath("//input[@type='number']").send_keys(port)
    browser.find_element_by_css_selector("button.btn.btn-default").click()
        
    return

# edit controller of bridge through gui
def guiEditControllerOfBridge(browser, bridge = None, 
                               method='Tcp', 
                               connection_mode='out-of-band', 
                               pri_ip_address=None,
                               pri_port = None,
                               ip_address=None, 
                               port='6633'):
    
    pri_id = '%s-%s' % (pri_ip_address, pri_port)
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content

    browser.find_element_by_link_text(bridge).click()
    time.sleep(1)
    browser.find_element_by_link_text("Controllers").click()
    time.sleep(1)    
    browser.find_element_by_link_text("Edit").click()
    time.sleep(1)    
    Select(browser.find_element_by_xpath("//div[@id='%s']/div/div/div[2]/form/div[2]/select" % pri_id)).select_by_visible_text(connection_mode)
    browser.find_element_by_name("eip").clear()
    browser.find_element_by_name("eip").send_keys(ip_address)
    browser.find_element_by_xpath("//input[@type='number']").clear()
    browser.find_element_by_xpath("//input[@type='number']").send_keys(port)
    time.sleep(1)
    browser.find_element_by_xpath("//div[@id='%s']/div/div/div[3]/button[1]" % pri_id).click()    
    return

# del controller from bridge through gui
def guiDelControllerFromBridge(browser, bridge,                                
                               pri_ip_address=None,
                               pri_port = None,):
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    
    pri_id = '%s-%s' % (pri_ip_address, pri_port)
    
    browser.find_element_by_link_text(bridge).click()
    time.sleep(1)
    browser.find_element_by_link_text("Controllers").click()
    time.sleep(1)
    browser.find_element_by_link_text("Delete").click()
    time.sleep(1)
    browser.find_element_by_xpath("//div[@id='del-%s']/div/div/div[3]/button[2]" % pri_id).click()    
        
    return

# add ports into bridge through gui
def guiAddPortIntoBridge(browser, bridge, ports):
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    
    browser.find_element_by_link_text(bridge).click()
    time.sleep(1)
    browser.find_element_by_link_text("Ports").click()
    time.sleep(1)
    for port in ports:
        browser.find_element_by_link_text("Add a new port").click()
        time.sleep(1)
        Select(browser.find_element_by_xpath("//div[@id='newport']/div/div/div[2]/form/div/select")).select_by_visible_text(str(port))
        Select(browser.find_element_by_xpath("//div[@id='newport']/div/div/div[2]/form/div[2]/div/select")).select_by_visible_text("trunk")
        browser.find_element_by_css_selector("#newport > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()

        print 'Add port:%s into bridge:%s done!' % (port, bridge)
        
    return

# edit ports of bridge through gui
def guiEditPortOfBridge(browser, bridge, port, ports):
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    
    # Get the port start index
    for tPort in range(len(ports)):
        if ports[tPort] == port:
            index = int(tPort)
    
    dindex = index + 1        
    bindex = index * 9 + 2
            
    browser.find_element_by_link_text(bridge).click()
    time.sleep(1)
    browser.find_element_by_link_text("Ports").click()
    time.sleep(1)
    if dindex == 1:
        browser.find_element_by_css_selector("em.ng-binding").click()
        browser.find_element_by_css_selector("button.btn.btn-default").click()
    else:
        browser.find_element_by_xpath("//div[@id='portlist']/div[%d]/div/h5/a/em" % dindex).click()
        browser.find_element_by_xpath("(//button[@type='button'])[%s]" % bindex).click()
    
    return

# add gre tunnel into bridge through gui
def guiAddGreTunnelIntoBridge(browser, bridge = None):  
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content

    browser.find_element_by_link_text("br0").click()
    time.sleep(3)
    browser.find_element_by_link_text("Tunnels").click()
    browser.find_element_by_link_text("Add a new tunnel").click()
    browser.find_element_by_name("tunnelNum").clear()
    browser.find_element_by_name("tunnelNum").send_keys("1")
    browser.find_element_by_name("rip").clear()
    browser.find_element_by_name("rip").send_keys("1.1.1.1")
    browser.find_element_by_name("lip").clear()
    browser.find_element_by_name("lip").send_keys("2.2.2.2")
    browser.find_element_by_name("sMac").clear()
    browser.find_element_by_name("sMac").send_keys("22:11:11:11:11:11")
    browser.find_element_by_name("dMac").clear()
    browser.find_element_by_name("dMac").send_keys("22:00:00:00:00:00")
    browser.find_element_by_name("vlan").clear()
    browser.find_element_by_name("vlan").send_keys("100")
    Select(browser.find_element_by_name("ePort")).select_by_visible_text("3")
    #Select(browser.find_element_by_xpath("//div[@id='newtunnel']/div/div/div[2]/form/div[6]/select")).select_by_visible_text("3")
    #browser.find_element_by_xpath("//div[@id='newtunnel']/div/div/div[2]/form/div[6]/select").send_keys("3")
    
    browser.find_element_by_css_selector("button.btn.btn-default").click()
        
    return

# add group table into bridge through gui
def guiAddGroupTableIntoBridge(browser, 
                               bridge = None,
                               groupid = None,
                               grouptype = None,
                               actions = None,
                               watchgroup = None,
                               watchport = None):  
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    browser.find_element_by_link_text(bridge).click()
    time.sleep(3)
    browser.find_element_by_link_text("Group Table").click()
    time.sleep(1)
    browser.find_element_by_link_text("Add a new group").click()
    time.sleep(1)
    browser.find_element_by_name("id").clear()
    browser.find_element_by_name("id").send_keys(groupid)
    browser.find_element_by_xpath("//input[@type='text']").clear()
    browser.find_element_by_xpath("//input[@type='text']").send_keys(actions)
    browser.find_element_by_xpath("(//button[@type='button'])[6]").click()
    #browser.find_element_by_xpath("//div[@id='newgroup']/div/div/div[2]/form/div[3]/div/table/tbody/tr[2]/td[4]").send_keys("output:3")
    browser.find_element_by_css_selector("#newgroup > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()

    return

# del group table of bridge through gui
def guiDelGroupTableOfBridge(browser, 
                               bridge = None,
                               groupid = None):  
    
    delnodeA = '#del-%s' % groupid
    delnodeB = 'del-%s' % groupid
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    browser.find_element_by_link_text(bridge).click()
    time.sleep(3)
    browser.find_element_by_link_text("Group Table").click()
    time.sleep(1)
    browser.find_element_by_xpath("(//strong[contains(text(),%s)])" % groupid).click()
    browser.find_element_by_xpath("//a[@href='%s']" % delnodeA).click()
    browser.find_element_by_xpath("//div[@id='%s']/div/div/div[3]/button[2]" % delnodeB).click()
    #browser.find_element_by_css_selector("#del-100 > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
    
    return

# add meter into bridge through gui
def guiAddMeterIntoBridge(browser, 
                          bridge = None,
                          meterid = None,
                          meterflag = None,
                          metertype = None,
                          meterrate = None,
                          meterburst = None,
                          meterpreclevel = None):  
    '''
    metertype should be DSCP_REMARK or DROP
    '''
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    browser.find_element_by_link_text(bridge).click()
    time.sleep(3)
    browser.find_element_by_link_text("Meter Table").click()
    time.sleep(1)
    browser.find_element_by_link_text("Add a new meter").click()
    browser.find_element_by_name("id").clear()
    browser.find_element_by_name("id").send_keys(meterid)
    time.sleep(1)
    if meterflag == "all":
        browser.find_element_by_css_selector("label.ng-binding > input.ng-pristine.ng-valid").click()
    
    Select(browser.find_element_by_xpath("//div[@id='newmeter']/div/div/div[2]/form/div[3]/div/div[2]/div/table/tbody/tr[2]/td/select")).select_by_visible_text(metertype)
    time.sleep(1)
    browser.find_element_by_xpath("(//input[@type='number'])[2]").clear()
    browser.find_element_by_xpath("(//input[@type='number'])[2]").send_keys(meterrate)

    
    if meterburst is not None:
        browser.find_element_by_xpath("//div[@id='newmeter']/div/div/div[2]/form/div[3]/div/div[2]/div/table/tbody/tr[2]/td[3]").send_keys(meterburst)

    time.sleep(1)    
    if meterpreclevel is not None:
        browser.find_element_by_xpath("(//input[@type='number'])[4]").clear()
        browser.find_element_by_xpath("(//input[@type='number'])[4]").send_keys(meterpreclevel)
    browser.find_element_by_link_text("+").click()
    browser.find_element_by_css_selector("form[name=\"newmeterform\"] > div.modal-footer > button.btn.btn-default").click()
    
    return

# del meter of bridge through gui
def guiDelMeterOfBridge(browser, 
                        bridge = None,
                        meterid = None,
                       ):  
    
    delnodeA = '#del-%s' % meterid
    delnodeB = 'del-%s' % meterid
    
    # Login through gui 
    #content = browser.page_source
    #print content
    browser.find_element_by_link_text(bridge).click()
    time.sleep(3)
    #content = browser.page_source
    #print content,
    browser.find_element_by_link_text("Meter Table").click()
    time.sleep(1)
    browser.find_element_by_xpath("(//strong[contains(text(),%s)])" % meterid).click()
    browser.find_element_by_xpath("//a[@href='%s']" % delnodeA).click()
    browser.find_element_by_xpath("//div[@id='%s']/div/div/div[3]/button[2]" % delnodeB).click()
    #browser.find_element_by_css_selector("#del-100 > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
    
    return

# add flows into bridge through gui
def guiAddFlowsIntoBridge(browser, 
                          bridge = None,
                          flows = None):  
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    browser.find_element_by_link_text(bridge).click()
    time.sleep(3)
    browser.find_element_by_link_text("Flow Table").click()
    time.sleep(1)
    browser.find_element_by_link_text("Add new flows").click()
    time.sleep(1)
    browser.find_element_by_xpath("//div[@id='newflows']/div/div/div[2]/form/div/textarea").clear()
    browser.find_element_by_xpath("//div[@id='newflows']/div/div/div[2]/form/div/textarea").send_keys("%s" % flows)
    browser.find_element_by_css_selector("#newflows > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
     
    return

# add netflow into bridge through gui
def guiAddNetFlowIntoBridge(browser, 
                            bridge = None,
                            sTime = None,
                            sIp = None,
                            sPort = None):  
    
    # Login through gui 
    time.sleep(3)
    #content = browser.page_source
    #print content
    browser.find_element_by_link_text(bridge).click()
    time.sleep(3)
    browser.find_element_by_link_text("NetFlow").click()
    time.sleep(1)
    browser.find_element_by_link_text("Add").click()
    time.sleep(1)
    browser.find_element_by_css_selector("form[name=\"newnetflowform\"] > div.form-group > input[name=\"time\"]").clear()
    browser.find_element_by_css_selector("form[name=\"newnetflowform\"] > div.form-group > input[name=\"time\"]").send_keys("%s" % sTime)
    browser.find_element_by_xpath("(//input[@type='text'])[2]").clear()
    browser.find_element_by_xpath("(//input[@type='text'])[2]").send_keys("%s" % sIp)
    browser.find_element_by_xpath("(//input[@type='number'])[4]").clear()
    browser.find_element_by_xpath("(//input[@type='number'])[4]").send_keys("%s" % sPort)
    browser.find_element_by_xpath("(//button[@type='button'])[10]").click()
    browser.find_element_by_css_selector("#newnetflow > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
    
    return

# edit netflow of bridge through gui
def guiEditNetFlowOfBridge(browser, 
                            bridge = None,
                            sTime = None,
                            sIp = None,
                            sPort = None):  
    
    # Login through gui 
    #content = browser.page_source
    #print content
    browser.find_element_by_link_text("br0").click()
    time.sleep(3)
    browser.find_element_by_link_text("NetFlow").click()
    time.sleep(1)
    browser.find_element_by_link_text("Edit").click()
    time.sleep(1)
    browser.find_element_by_name("time").clear()
    browser.find_element_by_name("time").send_keys("%s" % sTime)
    browser.find_element_by_name("ip").clear()
    browser.find_element_by_name("ip").send_keys("%s" % sIp)
    browser.find_element_by_name("port").clear()
    browser.find_element_by_name("port").send_keys("%s" % sPort)
    browser.find_element_by_css_selector("#editnetflow > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
    
    return

# del netflow of bridge through gui
def guiDelNetFlowOfBridge(browser, 
                            bridge = None):  
    
    # Login through gui 
    #content = browser.page_source
    #print content
    browser.find_element_by_link_text("br0").click()
    time.sleep(3)
    browser.find_element_by_link_text("NetFlow").click()
    time.sleep(1)
    browser.find_element_by_link_text("Delete").click()
    time.sleep(1)
    browser.find_element_by_xpath("(//button[@type='button'])[4]").click()
        
    return

# add sflow into bridge through gui
def guiAddsFlowIntoBridge(browser, 
                            bridge = None,
                            sPolling = None,
                            sHeader = None,
                            sAgent = None,
                            sSampling = None,
                            sIp = None,
                            sPort = None):  
    
    browser.find_element_by_link_text("br0").click()
    time.sleep(3)
    browser.find_element_by_link_text("sFlow").click()
    time.sleep(3)
    browser.find_element_by_link_text("Add").click()
    time.sleep(3)
    browser.find_element_by_css_selector("form[name=\"newsflowform\"] > div.form-group > div.col-md-9 > input[name=\"polling\"]").clear()
    browser.find_element_by_css_selector("form[name=\"newsflowform\"] > div.form-group > div.col-md-9 > input[name=\"polling\"]").send_keys("%s" % sPolling)
    browser.find_element_by_css_selector("form[name=\"newsflowform\"] > div.form-group > div.col-md-9 > input[name=\"header\"]").clear()
    browser.find_element_by_css_selector("form[name=\"newsflowform\"] > div.form-group > div.col-md-9 > input[name=\"header\"]").send_keys("%s" % sHeader)
    browser.find_element_by_css_selector("form[name=\"newsflowform\"] > div.form-group > div.col-md-9 > input[name=\"agent\"]").clear()
    browser.find_element_by_css_selector("form[name=\"newsflowform\"] > div.form-group > div.col-md-9 > input[name=\"agent\"]").send_keys("%s" % sAgent)
    browser.find_element_by_css_selector("form[name=\"newsflowform\"] > div.form-group > div.col-md-9 > input[name=\"sampling\"]").clear()
    browser.find_element_by_css_selector("form[name=\"newsflowform\"] > div.form-group > div.col-md-9 > input[name=\"sampling\"]").send_keys("%s" % sSampling)
    browser.find_element_by_xpath("(//input[@type='text'])[4]").clear()
    browser.find_element_by_xpath("(//input[@type='text'])[4]").send_keys("%s" % sIp)
    browser.find_element_by_xpath("(//input[@type='number'])[8]").clear()
    browser.find_element_by_xpath("(//input[@type='number'])[8]").send_keys("%s" % sPort)
    browser.find_element_by_xpath("(//button[@type='button'])[10]").click()
    browser.find_element_by_css_selector("#newsflow > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
    
    return

# edit sflow into bridge through gui
def guiEditsFlowIntoBridge(browser, 
                            bridge = None,
                            sPolling = None,
                            sHeader = None,
                            sAgent = None,
                            sSampling = None,
                            sIp = None,
                            sPort = None):  
    
    browser.find_element_by_link_text("br0").click()
    time.sleep(3)
    browser.find_element_by_link_text("sFlow").click()
    time.sleep(1)
    browser.find_element_by_link_text("Edit").click()
    time.sleep(1)
    browser.find_element_by_name("polling").clear()
    browser.find_element_by_name("polling").send_keys("%s" % sPolling)
    browser.find_element_by_name("header").clear()
    browser.find_element_by_name("header").send_keys("%s" % sHeader)
    browser.find_element_by_name("agent").clear()
    browser.find_element_by_name("agent").send_keys("%s" % sAgent)
    browser.find_element_by_name("sampling").clear()
    browser.find_element_by_name("sampling").send_keys("%s" % sSampling)
    browser.find_element_by_name("ip").clear()
    browser.find_element_by_name("ip").send_keys("%s" % sIp)
    browser.find_element_by_name("port").clear()
    browser.find_element_by_name("port").send_keys("%s" % sPort)
    browser.find_element_by_css_selector("#editsflow > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
    
    return

# del sflow of bridge through gui
def guiDelsFlowOfBridge(browser, 
                        bridge = None):  
    
    browser.find_element_by_link_text("%s" % bridge).click()
    time.sleep(3)
    browser.find_element_by_link_text("sFlow").click()
    time.sleep(1)
    browser.find_element_by_link_text("Delete").click()
    browser.find_element_by_xpath("(//button[@type='button'])[4]").click()
    
    return

# check switch resource 
def guiSwitchResource(browser):
    
    '''
    Caution: so far, the function does not work normally
    '''
    # Login through gui 
    browser.implicitly_wait(40)
    #browser.find_element_by_link_text("Monitor").click()
    #browser.find_element_by_xpath("/a[text()='Monitor']").click()
    #browser.find_element_by_partial_link_text("Monitor").click()
    browser.find_element_by_css_selector("a[href='#/bridges/configure']").click()

    return

# get bridge basic information
def guiBridgeBasicInfo(browser, bridge):
    
    # Login through gui 
    browser.implicitly_wait(10)
    browser.find_element_by_link_text(bridge).click()
    browser.find_element_by_link_text("Basic Info").click()
    content = browser.page_source
    print content
       
    return content
