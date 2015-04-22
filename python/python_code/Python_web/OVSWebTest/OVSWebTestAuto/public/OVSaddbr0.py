from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import OVSlogin
import webtestinfo

br = webtestinfo.bridgename()
    
def OVSaddbr0(self):
    OVSlogin.OVSlogin(self)
    driver.find_element_by_link_text("Create a bridge").click()
    WebDriverWait(driver, 20).until(lambda x: x.find_element_by_xpath("//form[@name='newbrform']/div/label").text)
    driver.find_element_by_xpath("//input[@type='text']").clear()
    time.sleep(2)
    driver.find_element_by_xpath("//input[@type='text']").send_keys(br)
    driver.find_element_by_css_selector("button.btn.btn-default").click()
    WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_link_text(br))
    driver.find_element_by_link_text("Monitor").click()
    WebDriverWait(driver, 20).until_not(lambda driver: driver.find_element_by_link_text("Create a bridge"))
    driver.find_element_by_link_text("Configuration").click()
    WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_link_text(br))
    time.sleep(5)
    print "%s add ok!" %br