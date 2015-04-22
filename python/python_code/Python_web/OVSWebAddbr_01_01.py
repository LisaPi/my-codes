from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import unittest, time, re

class OVSWebAddbrTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://10.10.50.138/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_OVSWebAddbrTest(self):
        driver = self.driver
        driver.get(self.base_url)
        adr = "Access %s" %self.base_url
        print (adr)
        driver.implicitly_wait(10)
        h2 = driver.find_element_by_tag_name('h2').text
        display = "The login page display %s" %h2
        print (display)
        #assert 'Pica8 OVS Switch Management Panel' in web
        assert h2 == 'Pica8 OVS Switch Management Panel'
        driver.find_element_by_name("username").clear()
        driver.find_element_by_name("username").send_keys("root")
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("pica8")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        time.sleep(10)
        #Show the switch info
        Labels = driver.find_element_by_tag_name("form").find_elements_by_tag_name("label")
        Ps = driver.find_element_by_tag_name("form").find_elements_by_tag_name("p")
        num = 0
        for Label in Labels:
            label = Label.text
            P = Ps[num]
            p = P.text
            infos = "%s %s" %(label, p)
            print(infos)
            num = num + 1
        
        #Create a new bridge
        driver.find_element_by_link_text("Create a bridge").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//form[@name='newbrform']/div/label"))
        addbr = driver.find_element_by_xpath("//form[@name='newbrform']/div/label").text
        assert addbr == 'New Bridge Name:'
        driver.find_element_by_xpath("//input[@type='text']").clear()
        driver.find_element_by_xpath("//input[@type='text']").send_keys("br0")
        driver.find_element_by_css_selector("button.btn.btn-default").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_link_text("br0"))
        #Check the new bridge create ok
        BrInfo = driver.find_element_by_link_text("br0").text
        br0 = "%s create ok" %BrInfo
        print(br0)
        #Check the state of the new bridge
        #span = driver.find_element_by_link_text("br0").find_element_by_tag_name("span")
        #span = span.get_attribute("class")
        #print(span)
        #Enter help interface
        driver.find_element_by_link_text("Help").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-view]/span"))
        helpa = driver.find_element_by_xpath("//div[@ng-view]/span").text
        print(helpa)
        #Back configuration interface
        driver.find_element_by_link_text("Configuration").click()
        #time.sleep(20)
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_link_text("br0"))
        driver.find_element_by_link_text("br0").click()
        #time.sleep(50)
        WebDriverWait(driver, 50).until(lambda x: x.find_element_by_link_text("Basic Info"))
        #Check the br0 link open
        #spana = driver.find_element_by_link_text("br0").find_element_by_tag_name("span")
        #spana = spana.get_attribute("class")
        #print(spana)
        print "Bridge br0 has open"
        #Check the default infos
        driver.find_element_by_link_text("Basic Info").click()
        time.sleep(2)
        #Show the default basic info
        Labels = driver.find_element_by_tag_name("form").find_elements_by_tag_name("label")
        Ps = driver.find_element_by_tag_name("form").find_elements_by_tag_name("p")
        num = 0
        for Label in Labels:
            label = Label.text
            P = Ps[num]
            p = P.text
            infos = "%s %s" %(label, p)
            print(infos)
            num = num + 1
        driver.find_element_by_link_text("Controllers").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='ControllerCtrl']/h4"))
        infos = driver.find_element_by_xpath("//div[@ng-controller='ControllerCtrl']//p").text
        print(infos)
        assert infos == "There isn't any controller configured."
        driver.find_element_by_link_text("Ports").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='PortsCtrl']/h4"))
        infos = driver.find_element_by_xpath("//div[@ng-controller='PortsCtrl']//p").text
        print(infos)
        assert infos == "There isn't any port on this bridge."
        driver.find_element_by_link_text("Tunnels").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='TunnelCtrl']/h4"))
        infos = driver.find_element_by_xpath("//div[@ng-controller='TunnelCtrl']//p").text
        print(infos)
        assert infos == "There isn't any tunnel configured."
        driver.find_element_by_link_text("Link Aggregation").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='BondCtrl']/h4"))
        infos = driver.find_element_by_xpath("//div[@ng-controller='BondCtrl']//p").text
        print(infos)
        assert infos == "There isn't any link aggregation configured."
        driver.find_element_by_link_text("Group Table").click()
        time.sleep(3)
        infos = driver.find_element_by_xpath("//div[@ng-controller='GroupCtrl']//p").text
        print(infos)
        assert infos == "There isn't any groups configured."
        driver.find_element_by_link_text("Meter Table").click()
        time.sleep(3)
        infos = driver.find_element_by_xpath("//div[@ng-controller='MeterCtrl']//p").text
        print(infos)
        assert infos == "There isn't any meters configured."
        driver.find_element_by_link_text("Flow Table").click()
        time.sleep(3)   
        driver.find_element_by_css_selector("em").click()
        infos = driver.find_element_by_xpath("//tbody//td[4]/div").text
        print(infos)
        assert infos == "NORMAL"
        driver.find_element_by_link_text("Mirrors").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='MirrorCtrl']/h4")) 
        infos = driver.find_element_by_xpath("//div[@ng-controller='MirrorCtrl']//p").text
        print(infos)
        assert infos == "There isn't any Mirrors configured."
        driver.find_element_by_link_text("NetFlow").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='NetFlowCtrl']/h4")) 
        infos = driver.find_element_by_xpath("//div[@ng-controller='NetFlowCtrl']//p").text
        print(infos)
        assert infos == "NetFlow isn't configured."
        driver.find_element_by_link_text("sFlow").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_xpath("//div[@ng-controller='sFlowCtrl']/h4")) 
        sflow = driver.find_element_by_xpath("//div[@ng-controller='sFlowCtrl']/h4").text
        print(sflow)
        infos = driver.find_element_by_xpath("//div[@ng-controller='sFlowCtrl']//p").text
        print(infos)
        assert infos == "sFlow isn't configured."
    
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

