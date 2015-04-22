from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class OVSWebLogin_01_01(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://10.10.50.138"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_OVSWebLogin_01_01(self):
        driver = self.driver
        driver.get(self.base_url + "/")
        #self.assertIn('Pica8 OVS Switch Management Panel', driver.title)
        element = driver.find_element_by_tag_name("h2").text
        self.assertEqual(element, 'Pica8 OVS Switch Management Panel')
        #assert element.text == 'Pica8 OVS Switch Management Panel'
        driver.find_element_by_name("username").clear()
        driver.find_element_by_name("username").send_keys("root")
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("piac8")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_name("username").clear()
        driver.find_element_by_name("username").send_keys("root")
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("pica8")
        self.driver.implicitly_wait(30)
        ng_scope = driver.find_elements_by_class_name("ng-scope")
        print(ng_scope)
        #swinfo = driver.find_element_by_tag_name('h4').text
        self.assertEqual(ng_scope, 'Switch Information')
        #assert element.text == 'Switch Model:'
        element = element.find_element_by_tag_name('p')
        assert element.text == '2.0.6'
    
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

