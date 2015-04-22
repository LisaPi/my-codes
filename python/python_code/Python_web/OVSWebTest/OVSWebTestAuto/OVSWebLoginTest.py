from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import unittest, time, re
import sys
sys.path.append("/public")
from public import webtestinfo

errus, errpw = webtestinfo.errorinfo()
us,pw = webtestinfo.userinfo()
baseurl = webtestinfo.baseurl()

class OVSWebLoginTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = baseurl
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_OVSWebLoginTest(self):        
        driver = self.driver
        driver.get(self.base_url + "/")
        #self.assertIn('Pica8 OVS Switch Management Panel', driver.title)
        print "Access %s" %(self.base_url)
        #assert 'Pica8 OVS Switch Management Panel' in web
        element = driver.find_element_by_tag_name('h2')
        assert element.text == 'Pica8 OVS Switch Management Panel'
        driver.find_element_by_name("username").clear()
        driver.find_element_by_name("username").send_keys(errus)
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys(errpw)
        driver.find_element_by_xpath("//button[@type='submit']").click()
        print "The error password cause loggin fail"
        driver.find_element_by_name("username").clear()
        driver.find_element_by_name("username").send_keys(us)
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys(pw)
        driver.find_element_by_xpath("//button[@type='submit']").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_link_text("Switch Resource"))
        print "The correct username and password cause loggin ok"
 
        #check switch basic info 
        print "In configuration interface"
        ConLabels = driver.find_element_by_tag_name("form").find_elements_by_tag_name("label")
        ConPs = driver.find_element_by_tag_name("form").find_elements_by_tag_name("p")
        conlabel = []
        conp = []
        num = 0
        for ConLabel in ConLabels:
            conlabel.extend(ConLabel.text)          
            ConP = ConPs[num]
            conp.append(ConP.text)  
            num = num + 1

        #check help infos
        driver.find_element_by_link_text("Help").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//div[@ng-view]/span"))
        helpa = driver.find_element_by_xpath("//div[@ng-view]/span").text
        print(helpa)

        #check the monitor infos
        driver.find_element_by_link_text("Monitor").click()
        WebDriverWait(driver, 20).until_not(lambda x: x.find_element_by_link_text("Create a bridge"))
        print "Enter monitor interface"
        MonLabels = driver.find_element_by_tag_name("form").find_elements_by_tag_name("label")
        MonPs = driver.find_element_by_tag_name("form").find_elements_by_tag_name("p")
        num = 0
        monlabel = []
        monp = []
        for MonLabel in MonLabels:
            monlabel.extend(MonLabel.text)          
            MonP = MonPs[num]
            monp.append(MonP.text) 
            num = num + 1
        
        if conp == monp:
            print "Switch info check ok!" 
        else:
            print "Switch info check fail!" 
            
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

