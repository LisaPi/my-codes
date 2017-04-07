from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class Untitled(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://www.baidu.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_untitled(self):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element_by_name("tj_login").click()
        driver.find_element_by_id("TANGRAM__PSP_8__userName").clear()
        driver.find_element_by_id("TANGRAM__PSP_8__userName").send_keys("xxxxx")
        driver.find_element_by_id("TANGRAM__PSP_8__password").clear()
        driver.find_element_by_id("TANGRAM__PSP_8__password").send_keys("xxxxxx")
        driver.find_element_by_id("TANGRAM__PSP_8__submit").click()
        time.sleep(30)
        driver.find_element_by_id("s_username_top").click()
        time.sleep(30)
        driver.find_element_by_class_name("myhome").click()
    
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
    unittest.main()

