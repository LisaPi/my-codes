from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import unittest, time, re
import sys
sys.path.append("/public")
from public import OVSlogin
from public import webtestinfo
baseurl=webtestinfo.baseurl()
br = webtestinfo.bridgename()

class OVSWebAddbrTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = baseurl
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_OVSWebAddbrTest(self):
        driver = self.driver
        driver.get(self.base_url + "/")
        OVSlogin.OVSlogin(self)
                
        #Create a new bridge
        driver.find_element_by_link_text("Create a bridge").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//form[@name='newbrform']/div/label").text) 
        addbr = driver.find_element_by_xpath("//form[@name='newbrform']/div/label").text
        assert addbr == 'New Bridge Name:'
        driver.find_element_by_xpath("//input[@type='text']").clear()
        time.sleep(2)
        driver.find_element_by_xpath("//input[@type='text']").send_keys(br)
        time.sleep(5)
        driver.find_element_by_css_selector("button.btn.btn-default").click()
        WebDriverWait(driver, 50).until(lambda x: x.find_element_by_link_text(br))
        BrInfo = driver.find_element_by_link_text(br).text
        print "%s added ok in configuration interface" %(BrInfo)

        driver.find_element_by_link_text("Monitor").click()
        WebDriverWait(driver, 20).until_not(lambda x: x.find_element_by_link_text("Create a bridge"))
        print "Enter monitor interface"
        BrInfo = driver.find_element_by_link_text(br).text
        print "%s added ok in monitor interface" %(BrInfo)
                
        #Back configuration interface
        driver.find_element_by_link_text("Configuration").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_link_text("Create a bridge"))
        driver.find_element_by_link_text(br).click()
        WebDriverWait(driver, 50).until(lambda x: x.find_element_by_link_text("Basic Info"))
        print "Bridge %s has open" %(br)

        #Check the infos in configuration
        driver.find_element_by_link_text("Basic Info").click()
        time.sleep(2)
        ConLabels = driver.find_element_by_tag_name("form").find_elements_by_tag_name("label")
        ConPs = driver.find_element_by_tag_name("form").find_elements_by_tag_name("p")
        num = 0
        ConBasic = []
        for ConLabel in ConLabels:
            conlabel = ConLabel.text
            ConP = ConPs[num]
            ConBasic.append(ConP.text)
            num = num + 1
        print(ConBasic)

        driver.find_element_by_link_text("Controllers").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='ControllerCtrl']/h4"))
        ConContr = driver.find_element_by_xpath("//div[@ng-controller='ControllerCtrl']//p").text
        assert ConContr == "There isn't any controller configured."

        driver.find_element_by_link_text("Ports").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='PortsCtrl']/h4"))
        ConPort = driver.find_element_by_xpath("//div[@ng-controller='PortsCtrl']//p").text
        assert ConPort == "There isn't any port on this bridge."

        driver.find_element_by_link_text("Tunnels").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='TunnelCtrl']/h4"))
        ConTunnel = driver.find_element_by_xpath("//div[@ng-controller='TunnelCtrl']//p").text
        assert ConTunnel == "There isn't any tunnel configured."

        driver.find_element_by_link_text("Link Aggregation").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='BondCtrl']/h4"))
        ConLag = driver.find_element_by_xpath("//div[@ng-controller='BondCtrl']//p").text
        assert ConLag == "There isn't any link aggregation configured."

        driver.find_element_by_link_text("Group Table").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='GroupCtrl']/h4"))
        time.sleep(10)
        ConGroup = driver.find_element_by_xpath("//div[@ng-controller='GroupCtrl']//p").text
        assert ConGroup == "There isn't any groups configured."
        
        driver.find_element_by_link_text("Meter Table").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='MeterCtrl']/h4"))
        time.sleep(10)
        ConMeter = driver.find_element_by_xpath("//div[@ng-controller='MeterCtrl']//p").text
        assert ConMeter == "There isn't any meters configured."
        
        driver.find_element_by_link_text("Flow Table").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='FlowTableCtrl']/h4"))  
        time.sleep(10)
        driver.find_element_by_css_selector("em").click()
        ConFlow = driver.find_element_by_xpath("//tbody//td[4]/div").text
        assert ConFlow == "NORMAL"
        
        driver.find_element_by_link_text("Mirrors").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='MirrorCtrl']/h4")) 
        ConMirror = driver.find_element_by_xpath("//div[@ng-controller='MirrorCtrl']//p").text
        assert ConMirror == "There isn't any Mirrors configured."
        
        driver.find_element_by_link_text("NetFlow").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='NetFlowCtrl']/h4")) 
        ConNetFlow = driver.find_element_by_xpath("//div[@ng-controller='NetFlowCtrl']//p").text
        assert ConNetFlow == "NetFlow isn't configured."
        
        driver.find_element_by_link_text("sFlow").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='sFlowCtrl']/h4")) 
        ConsFlow = driver.find_element_by_xpath("//div[@ng-controller='sFlowCtrl']//p").text
        assert ConsFlow == "sFlow isn't configured."

        #Check the infos in Monitor
        driver.find_element_by_link_text("Monitor").click()
        WebDriverWait(driver, 20).until_not(lambda x: x.find_element_by_link_text("Create a bridge"))
        driver.find_element_by_link_text(br).click()
        time.sleep(10)
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_tag_name("td"))
        MonTds = driver.find_element_by_id("basic").find_elements_by_tag_name("td")
        MonBasic = []
        for MonTd in MonTds:
            if MonTd.text != br:
                MonBasic.append(MonTd.text)

        if ConBasic == MonBasic:
            print "Basic info check ok!"
        else:
            print "Basic info check fail"

        driver.find_element_by_link_text("Controller").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("controller"))
        MonContr = driver.find_element_by_id("controller").find_element_by_tag_name("p").text
        if ConContr == MonContr:
            print "controller info check ok!"
        else:
            print "controller info check fail!"

        driver.find_element_by_link_text("Port").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("port"))
        MonPort = driver.find_element_by_id("port").find_element_by_tag_name("p").text
        if ConPort == MonPort:
            print "port info check ok!"
        else:
            print "port info check fail!"

        driver.find_element_by_link_text("Tunnel").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("tunnel"))
        MonTunnel = driver.find_element_by_id("tunnel").find_element_by_tag_name("p").text
        if ConTunnel == MonTunnel:
            print "Tunnel info check ok!"
        else:
            print "Tunnel info check fail!"
        
        driver.find_element_by_link_text("LAG").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("lag"))
        MonLag = driver.find_element_by_id("lag").find_element_by_tag_name("p").text
        if ConLag == MonLag:
            print "LAG info check ok!"
        else:
            print "LAG info check fail!"

        driver.find_element_by_link_text("Flow Table").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("flow"))
        MonFlows = driver.find_element_by_xpath("//div[@id='flow']//td[4]/div")
        MonFlow = MonFlows.text        
        if ConFlow == MonFlow:
            print "Flow info check ok!"
        else:
            print "Flow info check fail!"
        
        driver.find_element_by_link_text("Group Table").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("group"))
        MonGroup = driver.find_element_by_id("group").find_element_by_tag_name("p").text
        if ConGroup == MonGroup:
            print "Group info check ok!"
        else:
            print "Group info check fail!"

        driver.find_element_by_link_text("Meter Table").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("meter"))
        MonMeter = driver.find_element_by_id("meter").find_element_by_tag_name("p").text
        if ConMeter == MonMeter:
            print "Meter info check ok!"
        else:
            print "Meter info check fail!"

        driver.find_element_by_link_text("Visibility").click()
        driver.find_element_by_link_text("Mirror").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("mirror"))
        MonMirror = driver.find_element_by_id("mirror").find_element_by_tag_name("p").text
        if ConMirror == MonMirror:
            print "Mirror info check ok!"
        else:
            print "Mirror info check fail!"

        driver.find_element_by_link_text("Visibility").click()
        driver.find_element_by_link_text("NetFlow").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("netflow"))
        MonNetFlow = driver.find_element_by_id("netflow").find_element_by_tag_name("p").text
        if ConNetFlow == MonNetFlow:
            print "NetFlow info check ok!"
        else:
            print "NetFlow info check fail!"

        driver.find_element_by_link_text("Visibility").click()
        driver.find_element_by_link_text("sFlow").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("sflow"))
        MonsFlow = driver.find_element_by_id("sflow").find_element_by_tag_name("p").text
        if ConsFlow == MonsFlow:
            print "sFlow info check ok!"
        else:
            print "sFlow info check fail!"

        #delete br0
        driver.find_element_by_link_text("Configuration").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_link_text("Create a bridge"))
        driver.find_element_by_link_text(br).click() 
        time.sleep(5)
        driver.find_element_by_link_text("Delete").click()
        time.sleep(5)
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("del-br0"))
        time.sleep(5)
        #buttons = driver.find_elements_by_tag_name("button")
        #print(buttons)
        
        length = len(driver.find_elements_by_tag_name("button"))
        length = length - 3        
        for i in range(1, length):
            buttons = driver.find_elements_by_tag_name("button")
            button = buttons[i]
            butt = button.text
            if butt == "Delete":
                button.click()

        time.sleep(5)
        WebDriverWait(driver, 20).until_not(lambda x: x.find_element_by_link_text(br))
        print "%s delete ok!" %(br)

        #log out
        driver.find_element_by_link_text("Log Out").click()
            
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main(verbosity=2)

