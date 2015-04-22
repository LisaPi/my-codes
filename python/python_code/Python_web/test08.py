
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class Untitled2(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://10.10.50.138/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_untitled2(self):
        driver = self.driver
        driver.implicitly_wait(20)
        driver.get(self.base_url)
        element1 = driver.find_element_by_tag_name('h2')
        print(element1.text)
        assert element1.text == 'Pica8 OVS Switch Management Panel'
        driver.find_element_by_name("username").clear()
        driver.find_element_by_name("username").send_keys("root")
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("pica8")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        time.sleep(10)
        element2 = driver.find_element_by_xpath("//label[1]")
        print(element2.text)
        #for handle in driver.window_handles:
        #  driver.switch_to_window(handle)
        #driver.switch_to_window("")
        driver.find_element_by_link_text("Create a bridge").click()
        time.sleep(20)
        bbb = driver.find_element_by_xpath("//form[@name='newbrform']/div/label")
        #bbb = driver.find_element_by_class_name("control-label")
        print(bbb.text)
        assert bbb.text == 'New Bridge Name:'
        driver.find_element_by_xpath("//input[@type='text']").clear()
        #driver.find_element_by_xpath("//input[@ng-model='new_br_name']").clear()
        driver.find_element_by_xpath("//input[@type='text']").send_keys("br1")
        #driver.find_element_by_xpath("//input[@type='text']").clear()
        driver.find_element_by_css_selector("button.btn.btn-default").click()
        time.sleep(50)
        driver.find_element_by_css_selector("span.glyphicon.glyphicon-plus").click()
        time.sleep(2000)
        driver.find_element_by_link_text("Controllers").click()
        driver.find_element_by_link_text("Ports").click()
    
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

