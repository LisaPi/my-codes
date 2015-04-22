from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import unittest, time, re

class OVSWebAddPort_01_01(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://10.10.50.138/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_OVSWebAddPort_01_01(self):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element_by_name("username").clear()
        driver.find_element_by_name("username").send_keys("root")
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("pica8")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        WebDriverWait(driver, 20).until(lambda x: x.find_element_by_link_text("br0"))
        driver.find_element_by_link_text("br0").click()
        driver.find_element_by_link_text("Ports").click()
        
        #Add port1
        driver.find_element_by_link_text("Add a new port").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_id("newport"))
        Select(driver.find_element_by_xpath("//div[@id='newport']/div/div/div[2]/form/div/select")).select_by_visible_text("1")
        driver.find_element_by_css_selector("div.modal-footer > button.btn.btn-default").click() 
        WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath("//a[@href='#port-1']/em").text)
        port1 = driver.find_element_by_xpath("//a[@href='#port-1']/em").text
        print(port1)
        driver.find_element_by_css_selector("em.ng-binding").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_id("port-1"))
        LABELs = driver.find_element_by_id("port-1").find_elements_by_tag_name("label")
        Ps = driver.find_element_by_id("port-1").find_elements_by_tag_name("p")
        num = 0
        for LABEL in LABELs:
            label = LABEL.text
            P = Ps[num]
            p = P.text
            infos = "%s %s" %(label, p)
            print(infos)
            num = num + 1
        
        #Add port2        
        driver.find_element_by_link_text("Add a new port").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_id("newport"))
        Select(driver.find_element_by_xpath("//div[@id='newport']/div/div/div[2]/form/div/select")).select_by_visible_text("2")
        driver.find_element_by_css_selector("#newport > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
        WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath("//a[@href='#port-2']/em").text)
        port2 = driver.find_element_by_xpath("//a[@href='#port-2']/em").text
        print(port2)
        driver.find_element_by_xpath("//div[@id='portlist']/div[2]/div/h5/a/em").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_id("port-2"))
        LABELs = driver.find_element_by_id("port-2").find_elements_by_tag_name("label")
        Ps = driver.find_element_by_id("port-2").find_elements_by_tag_name("p")
        num = 0
        for LABEL in LABELs:
            label = LABEL.text
            P = Ps[num]
            p = P.text
            infos = "%s %s" %(label, p)
            print(infos)
            num = num + 1

        #Add port3
        driver.find_element_by_link_text("Add a new port").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_id("newport"))
        Select(driver.find_element_by_xpath("//div[@id='newport']/div/div/div[2]/form/div/select")).select_by_visible_text("3")
        Select(driver.find_element_by_xpath("//div[@id='newport']/div/div/div[2]/form/div[2]/div/select")).select_by_visible_text("trunk")
        driver.find_element_by_xpath("(//input[@type='number'])[18]").clear()
        driver.find_element_by_xpath("(//input[@type='number'])[18]").send_keys("2")
        driver.find_element_by_css_selector("form[name=\"newportform\"] > div.well > div.form-group > div.input-group > span.input-group-btn > button.btn.btn-default").click()
        driver.find_element_by_xpath("(//input[@type='number'])[19]").clear()
        driver.find_element_by_xpath("(//input[@type='number'])[19]").send_keys("3")
        driver.find_element_by_xpath("(//button[@type='button'])[22]").click()
        driver.find_element_by_xpath("(//input[@type='number'])[20]").clear()
        driver.find_element_by_xpath("(//input[@type='number'])[20]").send_keys("100")
        driver.find_element_by_xpath("(//button[@type='button'])[23]").click()
        driver.find_element_by_css_selector("#newport > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
        WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath("//a[@href='#port-3']/em").text)
        port3 = driver.find_element_by_xpath("//a[@href='#port-3']/em").text
        print(port3)
        driver.find_element_by_xpath("//div[@id='portlist']/div[3]/div/h5/a/em").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_id("port-3"))
        LABELs = driver.find_element_by_id("port-3").find_elements_by_tag_name("label")
        Ps = driver.find_element_by_id("port-3").find_elements_by_tag_name("p")
        num = 0
        for LABEL in LABELs:
            label = LABEL.text
            P = Ps[num]
            p = P.text
            infos = "%s %s" %(label, p)
            print(infos)
            num = num + 1
        
        #Add port4
        driver.find_element_by_link_text("Add a new port").click()
        Select(driver.find_element_by_xpath("//div[@id='newport']/div/div/div[2]/form/div/select")).select_by_visible_text("11")
        Select(driver.find_element_by_xpath("//div[@id='newport']/div/div/div[2]/form/div[2]/div/select")).select_by_visible_text("trunk")
        driver.find_element_by_xpath("(//input[@type='number'])[25]").clear()
        driver.find_element_by_xpath("(//input[@type='number'])[25]").send_keys("2")
        driver.find_element_by_xpath("(//input[@type='number'])[26]").clear()
        driver.find_element_by_xpath("(//input[@type='number'])[26]").send_keys("100")
        driver.find_element_by_css_selector("form[name=\"newportform\"] > div.well > div.form-group > div.input-group > span.input-group-btn > button.btn.btn-default").click()
        driver.find_element_by_xpath("(//input[@type='number'])[27]").clear()
        driver.find_element_by_xpath("(//input[@type='number'])[27]").send_keys("200")
        driver.find_element_by_xpath("(//button[@type='button'])[31]").click()
        driver.find_element_by_xpath("(//input[@type='number'])[28]").clear()
        driver.find_element_by_xpath("(//input[@type='number'])[28]").send_keys("4094")
        driver.find_element_by_xpath("(//button[@type='button'])[32]").click()
        driver.find_element_by_css_selector("#newport > div.modal-dialog > div.modal-content > div.modal-footer > button.btn.btn-default").click()
        WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath("//a[@href='#port-11']/em").text)
        port3 = driver.find_element_by_xpath("//a[@href='#port-11']/em").text
        print(port3)
        driver.find_element_by_xpath("//div[@id='portlist']/div[4]/div/h5/a/em").click()
        WebDriverWait(driver, 2).until(lambda x: x.find_element_by_id("port-11"))
        LABELs = driver.find_element_by_id("port-11").find_elements_by_tag_name("label")
        Ps = driver.find_element_by_id("port-11").find_elements_by_tag_name("p")
        num = 0
        for LABEL in LABELs:
            label = LABEL.text
            P = Ps[num]
            p = P.text
            infos = "%s %s" %(label, p)
            print(infos)
            num = num + 1

        #Check the ports list
        PORTs = driver.find_elements_by_tag_name("em")
        for port in PORTs:
            port = port.text
            print(port)

        #Enter MONITOR interface to cheak infos
        driver.find_element_by_link_text("Monitor").click()
        WebDriverWait(driver, 5).until_not(lambda x: x.find_element_by_link_text("Create a bridge"))
        driver.find_element_by_link_text("br0").click()
        WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath("//tabel//td").text)
        BasInfos = driver.find_element_by_tag_name("tabel").find_element_by_tag_name("td")
        for basinfo in BasInfos:
            info = basinfo.text
            print(info)
        driver.find_element_by_link_text("Port").click()
        
    
        
    
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

