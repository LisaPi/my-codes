from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import unittest, time, re 

def baseurl(): 
    ip = "http://10.10.50.138"
    return ip

def errorinfo():
    us  = 'root'
    pw = 'piac8'
    return us,pw
    
def userinfo(): 
    us  = 'root'
    pw = 'pica8' 
    return us,pw

def bridgename():
    br = 'br0'
    return br
    
