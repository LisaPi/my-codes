from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import unittest, time, re
import webtestinfo
 
us,pw = webtestinfo.userinfo() 

def OVSlogin(self):
    driver = self.driver
    driver.get(self.base_url + "/")
    driver.find_element_by_name("username").clear()
    driver.find_element_by_name("username").send_keys(us)
    driver.find_element_by_name("password").clear()
    driver.find_element_by_name("password").send_keys(pw)
    driver.find_element_by_xpath("//button[@type='submit']").click()
    WebDriverWait(driver, 20).until(lambda x: x.find_element_by_link_text("Switch Resource"))
    time.sleep(5)
    print "login ok!"